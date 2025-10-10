// src/interface/pages/QuoteCreatePage.tsx
import { useEffect, useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  useForm,
  useFieldArray,
  type SubmitHandler,
  type Resolver,
  useWatch,
} from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { clientRepository } from '../../../infrastructure/client/clientRepository';
import { catalogRepository } from '../../../infrastructure/catalog/catalogRepository';
import type { PrestationDto } from '../../../domain/catalog/types';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';
import type { ClientDto } from '../../../domain/client/types';
import { apiClient } from '../../../infrastructure/http/apiClient';
import NavBar from '../../components/navbar/Navbar';
import Sidebar from '../../components/sidebar/Sidebar';
import styles from './quote-edit-create.module.css';

/* ---------- zod schema ---------- */
const ItemSchema = z.object({
  prestation_id: z.number().int().positive().optional(),
  description: z.string().min(1, 'Description requise'),
  qty: z.number().positive('Qty doit être > 0'),
  unit_price: z.number().nonnegative('Prix unitaire >= 0'),
  tax_rate: z.number().min(0).max(100).optional(),
  discount: z.number().nonnegative().optional(),
});

const Schema = z.object({
  client: z.string().min(1, 'Choisis un client'),
  title: z.string().min(1, 'Titre requis'),
  reference: z.string().min(1, 'Référence requise'),
  currency: z.string().length(3).default('EUR'),
  language: z.string().min(2).max(8).default('fr'),
  issue_date: z.string().min(8, 'Date requise (YYYY-MM-DD)'),
  valid_until: z.string().optional().or(z.literal('')),
  payment_terms_text: z.string().optional(),
  items: z.array(ItemSchema).min(1, 'Au moins une ligne est requise'),
});

type FormData = z.infer<typeof Schema>;

/* ---------- helper types for payload ---------- */
type QuoteItemPayload = {
  prestation_id?: number;
  description: string;
  qty: number;
  unit_price: number;
  tax_rate?: number;
  discount: number;
  metadata?: Record<string, unknown>;
};

type QuotePayload = {
  client: string;
  title: string;
  reference: string;
  currency: string;
  language: string;
  issue_date: string;
  valid_until?: string | null;
  payment_terms_text?: string | null;
  items: QuoteItemPayload[];
};

type ProfessionalMeDto = {
  id: number;
  name?: string;
  tjm_cents?: number | null;
  service_types: number[];
};

/* ---------- small utility helpers ---------- */

function useMoneyFormatter(currency?: string | null) {
  return useMemo(
    () =>
      new Intl.NumberFormat(undefined, {
        style: 'currency',
        currency: currency ?? 'EUR',
        maximumFractionDigits: 2,
      }),
    [currency],
  );
}

function todayISO(): string {
  const d = new Date();
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 10);
}

/** Extract message from various error shapes (FieldError-like or simple string) */
function extractErrorMessage(err: unknown): string | undefined {
  if (!err) return undefined;
  if (typeof err === 'string') return err;
  if (typeof err === 'object' && err !== null) {
    const e = err as Record<string, unknown>;
    if ('message' in e) {
      const m = e.message;
      return typeof m === 'string' ? m : String(m ?? '');
    }
    if ('toString' in e) return String(e);
  }
  return undefined;
}

/** Type guard minimal pour détecter un objet d'erreur axios-like */
function isAxiosLikeError(
  e: unknown,
): e is { response?: { data?: unknown }; message?: string } {
  return (
    typeof e === 'object' && e !== null && ('response' in e || 'message' in e)
  );
}

/* ---------- component ---------- */
export default function QuoteCreatePage() {
  const navigate = useNavigate();
  const [clients, setClients] = useState<ClientDto[] | 'loading' | null>(
    'loading',
  );
  const [prestations, setPrestations] = useState<
    PrestationDto[] | 'loading' | null
  >('loading');
  const [me, setMe] = useState<ProfessionalMeDto | null>(null);
  const [loading, setLoading] = useState(false);

  // Remarque: on force le type Resolver<FormData> pour que zodResolver soit compatible
  const resolver = zodResolver(Schema) as unknown as Resolver<FormData>;

  const {
    register,
    control,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver,
    defaultValues: {
      currency: 'EUR',
      language: 'fr',
      issue_date: todayISO(),
      items: [
        {
          prestation_id: undefined,
          description: 'Nouvelle prestation',
          qty: 1,
          unit_price: 0.0,
          tax_rate: 20.0,
          discount: 0.0,
        },
      ],
    },
  });

  const { fields, append, remove } = useFieldArray({ control, name: 'items' });
  const watchedItems = useWatch({ control, name: 'items' }) as
    | FormData['items']
    | undefined;
  const watchedCurrency = useWatch({ control, name: 'currency' }) || 'EUR';
  const money = useMoneyFormatter(watchedCurrency);

  const totals = useMemo(() => {
    const lines = watchedItems ?? [];
    let sub = 0;
    let tax = 0;
    for (const line of lines) {
      const qty = Number(line?.qty ?? 0);
      const unit = Number(line?.unit_price ?? 0);
      const discount = Number(line?.discount ?? 0);
      const taxRate = Number(line?.tax_rate ?? 0);

      const base = qty * unit;
      const afterDiscount = base * (1 - discount / 100);
      const lineTax = afterDiscount * (taxRate / 100);

      sub += afterDiscount;
      tax += lineTax;
    }
    return { sub, tax, total: sub + tax };
  }, [watchedItems]);

  // Charger clients — clientRepository.list() renvoie désormais toujours ClientDto[]
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const list = await clientRepository.list();
        if (!active) return;
        // list est déjà typé ClientDto[], on l'affecte directement
        setClients(list);
      } catch (e) {
        console.error('Erreur chargement clients', e);
        if (!active) return;
        setClients(null);
      }
    })();
    return () => {
      active = false;
    };
  }, []);
  // Charger les prestations liées au professionnel (me)
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        // 1) qui suis-je ?
        const meResp = await apiClient.get<ProfessionalMeDto>(
          '/api/user/professional/me/',
        );
        const ids = meResp.data?.service_types ?? [];
        setMe(meResp.data ?? null);

        // s’il n’y a rien de lié -> vide explicite (et un message UI sympa)
        if (!ids.length) {
          if (active) setPrestations([]);
          return;
        }

        // 2) catalogue filtré sur ces IDs
        const list = await catalogRepository.listPrestations({ ids });
        if (!active) return;
        setPrestations(list);
      } catch (e) {
        console.error('Erreur chargement prestations liées', e);
        if (!active) return;
        setPrestations(null);
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  // ---- helpers de narrowing sûrs
  function pickString(
    o: Record<string, unknown>,
    keys: string[],
  ): string | undefined {
    for (const k of keys) {
      const v = o[k];
      if (typeof v === 'string' && v.trim() !== '') return v;
    }
    return undefined;
  }

  function pickNumber(
    o: Record<string, unknown>,
    keys: string[],
  ): number | undefined {
    for (const k of keys) {
      const v = o[k];
      if (typeof v === 'number' && Number.isFinite(v)) return v;
    }
    return undefined;
  }

  function pickMoney(
    o: Record<string, unknown>,
    keys: string[],
  ): number | undefined {
    for (const k of keys) {
      const v = o[k];
      if (typeof v === 'number' && Number.isFinite(v)) return v;
      if (typeof v === 'string') {
        const n = Number(v);
        if (Number.isFinite(n)) return n;
      }
    }
    return undefined;
  }

  function getPrestationWeightDays(p: PrestationDto): number {
    const o = p as unknown as Record<string, unknown>;
    const w = pickNumber(o, ['weight_days', 'days', 'effort_days']);
    return typeof w === 'number' && w > 0 ? w : 1;
  }

  // ---- accessors Prestation
  function getPrestationName(p: PrestationDto): string {
    const o = p as unknown as Record<string, unknown>;
    return pickString(o, ['name', 'label', 'title']) ?? `Prestation #${p.id}`;
  }

  function getPrestationPrice(p: PrestationDto): number | undefined {
    const o = p as unknown as Record<string, unknown>;
    // explicit cents → euros
    const cents = pickNumber(o, ['price_cents', 'default_rate_cents']);
    if (typeof cents === 'number') return cents / 100;

    // values already in EUR (string or number)
    const eur = pickMoney(o, ['default_rate_eur', 'price_eur', 'price']);
    if (typeof eur === 'number') return eur;

    // last fallbacks
    return pickNumber(o, ['default_price', 'default_rate']);
  }

  function getPrestationTaxRate(p: PrestationDto): number | undefined {
    const o = p as unknown as Record<string, unknown>;
    return pickNumber(o, ['tax_rate', 'tax_rate_value', 'default_tax_rate']);
  }

  // Typage correct pour la fonction de submit attendu par react-hook-form
  const onSubmit: SubmitHandler<FormData> = async (values) => {
    setLoading(true);
    try {
      const validUntil =
        values.valid_until && values.valid_until.length > 0
          ? values.valid_until
          : undefined;

      // Build strongly-typed payload
      const payload: QuotePayload = {
        client: values.client,
        title: values.title,
        reference: values.reference,
        currency: values.currency,
        language: values.language,
        issue_date: values.issue_date,
        valid_until: validUntil ?? null,
        payment_terms_text: values.payment_terms_text ?? null,
        items: values.items.map((it) => ({
          prestation_id: it.prestation_id ?? undefined,
          description: it.description,
          qty: Number(it.qty),
          unit_price: Number(it.unit_price),
          tax_rate:
            it.tax_rate === undefined || it.tax_rate === null
              ? undefined
              : Number(it.tax_rate),
          discount:
            it.discount === undefined || it.discount === null
              ? 0.0
              : Number(it.discount),
          metadata: {},
        })),
      };

      const created = await quoteRepository.create(payload);
      console.log('Quote created', created);
      navigate('/dashboard', { replace: true });
    } catch (err: unknown) {
      console.error('Create quote error', err);
      if (isAxiosLikeError(err) && err.response?.data) {
        alert(
          'Impossible de créer le devis : ' +
            JSON.stringify(err.response.data, null, 2),
        );
      } else if (isAxiosLikeError(err) && err.message) {
        alert('Impossible de créer le devis : ' + err.message);
      } else {
        alert('Impossible de créer le devis : erreur inconnue');
      }
    } finally {
      setLoading(false);
    }
  };

  if (clients === 'loading' || prestations === 'loading') {
    return (
      <main className={`container mx-auto p-6 ${styles.page}`}>
        <div className={styles.skeletonHeader} />
        <div className={styles.skeletonCard} />
      </main>
    );
  }

  return (
    <main className={`container mx-auto p-6 grid gap-6 ${styles.page}`}>
      <Sidebar />
      <NavBar />
      {/* Header */}
      <header className={styles.header}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className={styles.title}>Créer un nouveau devis</h1>
            <p className={styles.meta}>
              Remplissez les informations ci-dessous pour générer un devis.
            </p>
          </div>
          <div className="flex gap-2">
            <Link to="/dashboard" className={styles.buttonGhost}>
              Annuler
            </Link>
            <button
              type="button"
              className={styles.buttonPrimary}
              onClick={handleSubmit(onSubmit)}
              disabled={isSubmitting || loading}
            >
              {isSubmitting || loading ? 'Création…' : 'Créer le devis'}
            </button>
          </div>
        </div>
      </header>

      {/* Erreurs globales */}
      {(errors.client || errors.title || errors.reference || errors.items) && (
        <div className={styles.errorBox}>
          ⚠️{' '}
          {[
            extractErrorMessage(errors.client),
            extractErrorMessage(errors.title),
            extractErrorMessage(errors.reference),
            extractErrorMessage(errors.items),
          ]
            .filter(Boolean)
            .join(' • ')}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="grid gap-6">
        {/* Bloc Client */}
        <section className={styles.card}>
          <h2 className={styles.h2}>Client</h2>
          <div className={styles.formGrid}>
            <label className={styles.label}>
              <span>Client *</span>
              {clients === null ? (
                <div className={styles.errorBox}>
                  Erreur lors du chargement des clients.
                </div>
              ) : (
                <select {...register('client')} className={styles.input}>
                  <option value="">— Sélectionner un client —</option>
                  {clients.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} {c.email ? `(${c.email})` : ''}
                    </option>
                  ))}
                </select>
              )}
              {errors.client && (
                <small className={styles.errorBox}>
                  {extractErrorMessage(errors.client)}
                </small>
              )}
            </label>
          </div>
        </section>

        {/* Bloc Devis */}
        <section className={styles.card}>
          <h2 className={styles.h2}>Informations du devis</h2>
          <div className={styles.formGrid}>
            <label className={styles.label}>
              <span>Titre *</span>
              <input
                {...register('title')}
                className={styles.input}
                placeholder="Site vitrine 5 pages"
              />
              {errors.title && (
                <small className={styles.errorBox}>
                  {extractErrorMessage(errors.title)}
                </small>
              )}
            </label>

            <label className={styles.label}>
              <span>Référence *</span>
              <input
                {...register('reference')}
                className={styles.input}
                placeholder="FS-2025-001"
              />
              {errors.reference && (
                <small className={styles.errorBox}>
                  {extractErrorMessage(errors.reference)}
                </small>
              )}
            </label>

            <label className={styles.label}>
              <span>Devise</span>
              <input
                {...register('currency')}
                className={styles.input}
                placeholder="EUR"
              />
            </label>

            <label className={styles.label}>
              <span>Langue</span>
              <input
                {...register('language')}
                className={styles.input}
                placeholder="fr"
              />
            </label>

            <label className={styles.label}>
              <span>Date d'émission *</span>
              <input
                type="date"
                {...register('issue_date')}
                className={styles.input}
              />
              {errors.issue_date && (
                <small className={styles.errorBox}>
                  {extractErrorMessage(errors.issue_date)}
                </small>
              )}
            </label>

            <label className={styles.label}>
              <span>Valable jusqu'au</span>
              <input
                type="date"
                {...register('valid_until')}
                className={styles.input}
              />
            </label>
          </div>

          <div className={styles.formGrid}>
            <label className={styles.labelCol}>
              <span>Conditions de paiement</span>
              <textarea
                {...register('payment_terms_text')}
                className={styles.textarea}
                rows={3}
                placeholder="Ex: Paiement à 30 jours fin de mois"
              />
            </label>
          </div>
        </section>

        {/* Bloc Prestations */}
        <section className={styles.card}>
          <div
            className="flex items-center justify-between"
            style={{ marginBottom: '16px' }}
          >
            <h2 className={styles.h2}>Prestations</h2>
            <button
              type="button"
              onClick={() =>
                append({
                  description: 'Nouvelle prestation',
                  qty: 1,
                  unit_price: 0.0,
                  tax_rate: 20.0,
                  discount: 0.0,
                })
              }
              className={styles.buttonAccent}
            >
              + Ajouter
            </button>
          </div>

          {fields.length === 0 ? (
            <div className={styles.empty}>Aucune prestation</div>
          ) : (
            <>
              <div style={{ display: 'grid', gap: '12px' }}>
                {fields.map((field, index) => {
                  const prestReg = register(`items.${index}.prestation_id`, {
                    valueAsNumber: true,
                  });

                  return (
                    <div
                      key={field.id}
                      style={{
                        padding: '16px',
                        border: '1px solid rgba(13,13,13,0.1)',
                        borderRadius: '8px',
                        background: '#fff',
                        display: 'grid',
                        gap: '12px',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          gap: '12px',
                          alignItems: 'center',
                        }}
                      >
                        <span
                          style={{
                            minWidth: '32px',
                            height: '32px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: '#f0f4ff',
                            borderRadius: '6px',
                            fontWeight: '600',
                            fontSize: '0.9rem',
                            color: 'var(--brand)',
                          }}
                        >
                          {index + 1}
                        </span>

                        {prestations === null ? (
                          <div className={styles.errorBox} style={{ flex: 1 }}>
                            Erreur de chargement
                          </div>
                        ) : (
                          <select
                            {...prestReg}
                            className={styles.input}
                            style={{ flex: 1 }}
                            onChange={(e) => {
                              prestReg.onChange(e);
                              const id = e.target.value
                                ? Number(e.target.value)
                                : undefined;

                              setValue(`items.${index}.prestation_id`, id, {
                                shouldValidate: true,
                                shouldDirty: true,
                              });

                              if (!id) return;

                              const p = prestations.find((pp) => pp.id === id);
                              if (!p) return;

                              const name = getPrestationName(p);
                              const taxRate = getPrestationTaxRate(p);
                              const weight = getPrestationWeightDays(p);

                              const tjm = me?.tjm_cents
                                ? me.tjm_cents / 100
                                : undefined;
                              const fallbackDayRate = getPrestationPrice(p);
                              const dayRate =
                                typeof tjm === 'number'
                                  ? tjm
                                  : typeof fallbackDayRate === 'number'
                                    ? fallbackDayRate
                                    : undefined;
                              const unit =
                                typeof dayRate === 'number'
                                  ? dayRate * weight
                                  : undefined;

                              if (name)
                                setValue(`items.${index}.description`, name, {
                                  shouldDirty: true,
                                });
                              if (typeof taxRate === 'number')
                                setValue(`items.${index}.tax_rate`, taxRate, {
                                  shouldDirty: true,
                                });
                              if (typeof unit === 'number')
                                setValue(`items.${index}.unit_price`, unit, {
                                  shouldDirty: true,
                                });
                            }}
                          >
                            <option value="">— Choisir une prestation —</option>
                            {prestations.map((p) => (
                              <option key={p.id} value={p.id}>
                                {getPrestationName(p)}
                              </option>
                            ))}
                          </select>
                        )}

                        <button
                          type="button"
                          onClick={() => remove(index)}
                          style={{
                            padding: '8px 12px',
                            border: '1px solid rgba(13,13,13,0.1)',
                            borderRadius: '6px',
                            background: '#fff',
                            cursor: 'pointer',
                            fontSize: '0.85rem',
                          }}
                        >
                          ✕
                        </button>
                      </div>

                      <input
                        {...register(`items.${index}.description`)}
                        className={styles.input}
                        placeholder="Description"
                      />

                      <div
                        style={{
                          display: 'grid',
                          gridTemplateColumns:
                            'repeat(auto-fit, minmax(100px, 1fr))',
                          gap: '12px',
                        }}
                      >
                        <label style={{ display: 'grid', gap: '4px' }}>
                          <span style={{ fontSize: '0.75rem', color: '#666' }}>
                            Quantité
                          </span>
                          <input
                            className={styles.input}
                            type="number"
                            step="0.01"
                            {...register(`items.${index}.qty`, {
                              valueAsNumber: true,
                            })}
                          />
                        </label>

                        <label style={{ display: 'grid', gap: '4px' }}>
                          <span style={{ fontSize: '0.75rem', color: '#666' }}>
                            Prix unitaire HT
                          </span>
                          <div
                            style={{ display: 'flex', alignItems: 'stretch' }}
                          >
                            <input
                              className={styles.input}
                              type="number"
                              step="0.01"
                              {...register(`items.${index}.unit_price`, {
                                valueAsNumber: true,
                              })}
                              style={{
                                borderTopRightRadius: 0,
                                borderBottomRightRadius: 0,
                                borderRight: 'none',
                              }}
                            />
                            <span
                              style={{
                                padding: '0 12px',
                                display: 'flex',
                                alignItems: 'center',
                                border: '1px solid rgba(13,13,13,0.12)',
                                borderTopRightRadius: '12px',
                                borderBottomRightRadius: '12px',
                                background: '#f8fafc',
                                fontSize: '0.9rem',
                              }}
                            >
                              €
                            </span>
                          </div>
                        </label>

                        <label style={{ display: 'grid', gap: '4px' }}>
                          <span style={{ fontSize: '0.75rem', color: '#666' }}>
                            TVA (%)
                          </span>
                          <input
                            className={styles.input}
                            type="number"
                            step="0.01"
                            {...register(`items.${index}.tax_rate`, {
                              valueAsNumber: true,
                            })}
                          />
                        </label>

                        <label style={{ display: 'grid', gap: '4px' }}>
                          <span style={{ fontSize: '0.75rem', color: '#666' }}>
                            Remise (%)
                          </span>
                          <input
                            className={styles.input}
                            type="number"
                            step="0.01"
                            {...register(`items.${index}.discount`, {
                              valueAsNumber: true,
                            })}
                          />
                        </label>
                      </div>
                    </div>
                  );
                })}
              </div>
              {/* Récapitulatif Totaux */}
              <div
                style={{
                  marginTop: '16px',
                  padding: '16px',
                  background: '#f8fafc',
                  borderRadius: '8px',
                  display: 'grid',
                  gap: '8px',
                }}
              >
                <div
                  style={{ display: 'flex', justifyContent: 'space-between' }}
                >
                  <span>Sous-total HT</span>
                  <strong>{money.format(totals.sub)}</strong>
                </div>

                <div
                  style={{ display: 'flex', justifyContent: 'space-between' }}
                >
                  <span>TVA</span>
                  <strong>{money.format(totals.tax)}</strong>
                </div>

                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    paddingTop: '8px',
                    borderTop: '2px solid rgba(13,13,13,0.1)',
                    fontSize: '1.1rem',
                  }}
                >
                  <strong>Total TTC</strong>
                  <strong>{money.format(totals.total)}</strong>
                </div>
              </div>
            </>
          )}
        </section>

        {/* Actions bas de page */}
        <div className="flex items-center gap-2">
          <button
            type="submit"
            className={styles.buttonPrimary}
            disabled={isSubmitting || loading}
          >
            {isSubmitting || loading ? 'Création…' : 'Créer le devis'}
          </button>
          <Link to="/dashboard" className={styles.buttonGhost}>
            Annuler
          </Link>
        </div>
      </form>
    </main>
  );
}
