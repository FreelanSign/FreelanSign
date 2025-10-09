// src/interface/pages/QuoteCreatePage.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  useForm,
  useFieldArray,
  type SubmitHandler,
  type Resolver,
} from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { clientRepository } from '../../../infrastructure/client/clientRepository';
import { catalogRepository } from '../../../infrastructure/catalog/catalogRepository';
import type { PrestationDto } from '../../../domain/catalog/types';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';
import type { ClientDto } from '../../../domain/client/types';
import { apiClient } from '../../../infrastructure/http/apiClient';

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
  const [prestations, setPrestations] = useState<PrestationDto[] | 'loading' | null>('loading');
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
        const meResp = await apiClient.get<ProfessionalMeDto>('/api/user/professional/me/');
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
  function pickString(o: Record<string, unknown>, keys: string[]): string | undefined {
    for (const k of keys) {
      const v = o[k];
      if (typeof v === 'string' && v.trim() !== '') return v;
    }
    return undefined;
  }

  function pickNumber(o: Record<string, unknown>, keys: string[]): number | undefined {
    for (const k of keys) {
      const v = o[k];
      if (typeof v === 'number' && Number.isFinite(v)) return v;
    }
    return undefined;
  }

  function pickMoney(o: Record<string, unknown>, keys: string[]): number | undefined {
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

  return (
    <main className="container mx-auto p-6 grid gap-6">
      <h1 className="text-2xl font-semibold">Nouveau devis</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4 max-w-2xl">
        {/* Client */}
        <label className="grid gap-1">
          <span>Client</span>
          {clients === 'loading' ? (
            <div>Chargement des clients…</div>
          ) : clients === null ? (
            <div className="text-red-600">
              Erreur lors du chargement des clients.
            </div>
          ) : (
            <select {...register('client')} className="border p-2 rounded">
              <option value="">— Sélectionner —</option>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} {c.email ? `— ${c.email}` : ''}
                </option>
              ))}
            </select>
          )}
          {errors.client && (
            <small className="text-red-600">
              {extractErrorMessage(errors.client)}
            </small>
          )}
        </label>

        {/* Header fields */}
        <label className="grid gap-1">
          <span>Titre</span>
          <input {...register('title')} className="border p-2 rounded" />
          {errors.title && (
            <small className="text-red-600">
              {extractErrorMessage(errors.title)}
            </small>
          )}
        </label>

        <label className="grid gap-1">
          <span>Référence</span>
          <input {...register('reference')} className="border p-2 rounded" />
          {errors.reference && (
            <small className="text-red-600">
              {extractErrorMessage(errors.reference)}
            </small>
          )}
        </label>

        <div className="grid grid-cols-2 gap-3">
          <label className="grid gap-1">
            <span>Date d’émission</span>
            <input
              type="date"
              {...register('issue_date')}
              className="border p-2 rounded"
            />
            {errors.issue_date && (
              <small className="text-red-600">
                {extractErrorMessage(errors.issue_date)}
              </small>
            )}
          </label>

          <label className="grid gap-1">
            <span>Valable jusqu’au</span>
            <input
              type="date"
              {...register('valid_until')}
              className="border p-2 rounded"
            />
          </label>
        </div>

        {/* Items list */}
        <section className="p-4 border rounded">
          <h3 className="font-medium">Prestations du devis</h3>
          {fields.map((field, index) => (
            <div
              key={field.id}
              className="grid gap-2 grid-cols-12 items-end border-b py-2"
            >
              <div className="col-span-4">
                <label className="block text-sm">Prestation</label>

                {prestations === 'loading' ? (
                  <div>Chargement des prestations…</div>
                ) : prestations === null ? (
                  <div className="text-red-600">Erreur lors du chargement des prestations.</div>
                ) : (
                  (() => {
                    // on récupère l’objet register pour pouvoir relayer onChange
                    const prestReg = register(`items.${index}.prestation_id`, { valueAsNumber: true });
                    return (
                      <select
                        {...prestReg}
                        className="border p-1 rounded w-full"
                        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                          // relayer l'événement à RHF, sinon la valeur n'est pas prise en compte
                          prestReg.onChange(e);

                          const id = e.target.value ? Number(e.target.value) : undefined;

                          setValue(`items.${index}.prestation_id`, id as number | undefined, {
                            shouldValidate: true,
                            shouldDirty: true,
                          });
                          if (!id) return;

                          const p = prestations.find((pp) => pp.id === id);
                          if (!p) return;

                          const name = getPrestationName(p);
                          const taxRate = getPrestationTaxRate(p);
                          const weight = getPrestationWeightDays(p); // nombre de jours "dans" une prestation

                          // Nouvelle règle métier:
                          // - La QUANTITÉ = nombre de prestations (laisse l'utilisateur saisir 1,2,3...)
                          // - Le PRIX UNITAIRE = (taux journalier) × (weight_days)
                          //   • taux journalier = TJM du pro si défini, sinon tarif par jour de la prestation
                          const tjm = me?.tjm_cents ? me.tjm_cents / 100 : undefined; // €/jour
                          const fallbackDayRate = getPrestationPrice(p); // €/jour si dispo via défaut catalogue
                          const dayRate = typeof tjm === 'number' ? tjm : (typeof fallbackDayRate === 'number' ? fallbackDayRate : undefined);
                          const unit = typeof dayRate === 'number' ? dayRate * weight : undefined;

                          if (name) setValue(`items.${index}.description`, name, { shouldDirty: true });
                          if (typeof taxRate === 'number') setValue(`items.${index}.tax_rate`, taxRate, { shouldDirty: true });
                          // ne PAS toucher à qty ici (c'est le nombre de prestations)
                          if (typeof unit === 'number') setValue(`items.${index}.unit_price`, unit, { shouldDirty: true });
                        }}
                      >
                        <option value="">— Choisir —</option>
                        {prestations.map((p) => (
                          <option key={p.id} value={p.id}>
                            {getPrestationName(p)}
                          </option>
                        ))}
                      </select>
                    );
                  })()
                )}
              </div>
              <div className="col-span-5">
                <label className="block text-sm">Description</label>
                <input
                  {...register(`items.${index}.description` as const)}
                  className="border p-1 rounded w-full"
                />
              </div>

              <div className="col-span-2">
                <label className="block text-sm">Quantité</label>
                <input
                  type="number"
                  step="0.01"
                  {...register(`items.${index}.qty`, { valueAsNumber: true })}
                  className="border p-1 rounded w-full"
                />
              </div>

              <div className="col-span-2">
                <label className="block text-sm">Prix unitaire</label>
                <input
                  type="number"
                  step="0.01"
                  {...register(`items.${index}.unit_price`, {
                    valueAsNumber: true,
                  })}
                  className="border p-1 rounded w-full"
                />
              </div>

              <div className="col-span-1">
                <label className="block text-sm">TVA %</label>
                <input
                  type="number"
                  step="0.01"
                  {...register(`items.${index}.tax_rate`, {
                    valueAsNumber: true,
                  })}
                  className="border p-1 rounded w-full"
                />
              </div>

              <div className="col-span-1">
                <label className="block text-sm">Remise</label>
                <input
                  type="number"
                  step="0.01"
                  {...register(`items.${index}.discount`, {
                    valueAsNumber: true,
                  })}
                  className="border p-1 rounded w-full"
                />
              </div>

              <div className="col-span-12 flex gap-2 mt-2">
                <button
                  type="button"
                  onClick={() => remove(index)}
                  className="bg-red-600 text-white px-2 py-1 rounded"
                >
                  Suppr
                </button>
              </div>
            </div>
          ))}

          <div className="mt-3">
            <button
              type="button"
              onClick={() =>
                append({
                  description: 'Nouvelle ligne',
                  qty: 1,
                  unit_price: 0.0,
                  tax_rate: 20.0,
                  discount: 0.0,
                })
              }
              className="bg-gray-800 text-white px-3 py-1 rounded"
            >
              + Ajouter une ligne
            </button>
            {errors.items && (
              <div className="text-red-600 mt-2">
                {extractErrorMessage(errors.items)}
              </div>
            )}
          </div>
        </section>

        {/* Payment terms (free text for now) */}
        <label className="grid gap-1">
          <span>Conditions de paiement</span>
          <input
            {...register('payment_terms_text')}
            className="border p-2 rounded"
          />
        </label>

        <div className="flex gap-3">
          <button
            disabled={isSubmitting || loading}
            className="bg-green-600 text-white rounded px-4 py-2"
            type="submit"
          >
            {isSubmitting || loading ? 'Création…' : 'Créer le devis'}
          </button>
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="bg-gray-200 rounded px-4 py-2"
          >
            Annuler
          </button>
        </div>
      </form>
    </main>
  );
}
