// src/interface/pages/QuoteEditPage.tsx
import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';
import styles from './quote-edit.module.css';

import type {
  ApiQuoteResponse,
  ApiQuoteUpdatePayload,
} from '../../../domain/quote/types';
import { apiToUiQuote } from '../../../domain/quote/mappers';

type QuoteLine = {
  id?: string | number;
  designation: string;
  description?: string | null;
  quantity: number;
  unit_price: number;
  /** 0.2 => 20% (fraction UI) */
  tax_rate?: number | null;
};

type ClientInfo = {
  id?: string; // UUID renvoyé par l'API
  name: string;
  email?: string | null;
  company?: string | null;
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  postal_code?: string | null;
  country?: string | null;
};

type Quote = {
  id: string;
  reference: string;
  title: string;
  status: string;
  issue_date?: string | null; // YYYY-MM-DD
  due_date?: string | null; // UI -> valid_until (API)
  currency?: string | null;
  notes?: string | null; // UI -> note (API)
  terms?: string | null; // UI only
  client?: ClientInfo | null;
  line_items: QuoteLine[];
};

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

export default function QuoteEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [quote, setQuote] = useState<Quote | null>(null);

  const EMPTY_CLIENT: ClientInfo = {
    id: undefined,
    name: '',
    email: '',
    company: '',
    address_line1: '',
    address_line2: '',
    city: '',
    postal_code: '',
    country: '',
  };

  // --- Load ---
  useEffect(() => {
    if (!id) return;
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const api: ApiQuoteResponse = await quoteRepository.retrieve(id);

        if (!active) return;

        // Domain API → UiQuote (générique)
        const uiBase = apiToUiQuote(api);

        // UiQuote (domain) → Quote (UI locale de la page)
        const ui: Quote = {
          id: uiBase.id,
          reference: uiBase.reference,
          title: uiBase.title,
          status: uiBase.status,
          issue_date: uiBase.issue_date ?? null,
          due_date: uiBase.due_date ?? null,
          currency: uiBase.currency ?? 'EUR',
          notes: uiBase.notes ?? '',
          terms: uiBase.terms ?? '',
          client: uiBase.client
            ? {
                id: uiBase.client.id,
                name: uiBase.client.name ?? '',
                email: uiBase.client.email ?? '',
                company: '', // champs spécifiques à ton formulaire
                address_line1: uiBase.client.address ?? '',
                address_line2: '',
                city: '',
                postal_code: '',
                country: '',
              }
            : {
                id: undefined,
                name: '',
                email: '',
                company: '',
                address_line1: '',
                address_line2: '',
                city: '',
                postal_code: '',
                country: '',
              },
          line_items: uiBase.line_items.map(
            (l, idx): QuoteLine => ({
              id: l.id ?? idx,
              designation: l.designation,
              description: l.description ?? '',
              quantity: l.quantity,
              unit_price: l.unit_price,
              tax_rate: l.tax_rate ?? 0,
            }),
          ),
        };

        setQuote(ui);
      } catch (err) {
        const e = err as { response?: { data?: unknown }; message?: string };
        setError(
          e.response?.data
            ? JSON.stringify(e.response.data)
            : (e.message ?? 'Erreur'),
        );
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [id]);

  const money = useMoneyFormatter(quote?.currency ?? 'EUR');

  // Derived totals (UI)
  const totals = useMemo(() => {
    const lines = quote?.line_items ?? [];
    const sub = lines.reduce((acc, l) => acc + l.quantity * l.unit_price, 0);
    const tax = lines.reduce((acc, l) => {
      const rate = l.tax_rate ?? 0;
      return acc + l.quantity * l.unit_price * rate;
    }, 0);
    return { sub, tax, total: sub + tax };
  }, [quote]);

  const setField = <K extends keyof Quote>(key: K, value: Quote[K]) => {
    setQuote((q) => (q ? { ...q, [key]: value } : q));
  };

  const setClient = <K extends keyof ClientInfo>(
    key: K,
    value: ClientInfo[K],
  ) => {
    setQuote((q) => {
      if (!q) return q;
      const base = q.client ?? EMPTY_CLIENT;
      return { ...q, client: { ...base, [key]: value } };
    });
  };

  const updateLine = (idx: number, patch: Partial<QuoteLine>) => {
    setQuote((q) => {
      if (!q) return q;
      const copy = [...q.line_items];
      copy[idx] = { ...copy[idx], ...patch };
      return { ...q, line_items: copy };
    });
  };

  const addLine = () => {
    setQuote((q) => {
      if (!q) return q;
      const next: QuoteLine = {
        designation: '',
        description: '',
        quantity: 1,
        unit_price: 0,
        tax_rate: 0.2,
      };
      return { ...q, line_items: [...q.line_items, next] };
    });
  };

  const removeLine = (idx: number) => {
    setQuote((q) => {
      if (!q) return q;
      const copy = q.line_items.filter((_, i) => i !== idx);
      return { ...q, line_items: copy };
    });
  };

  const validate = (): string[] => {
    const errs: string[] = [];
    if (!quote) return ['Formulaire vide'];
    if (!quote.title?.trim()) errs.push('Le titre est requis.');
    if (!quote.reference?.trim()) errs.push('La référence est requise.');
    if (!quote.status?.trim()) errs.push('Le statut est requis.');
    if (!quote.client?.name?.trim()) errs.push('Le nom du client est requis.');
    quote.line_items.forEach((l, i) => {
      if (!l.designation?.trim())
        errs.push(`Ligne #${i + 1}: désignation requise.`);
      if (!(l.quantity >= 0)) errs.push(`Ligne #${i + 1}: quantité invalide.`);
      if (!(l.unit_price >= 0)) errs.push(`Ligne #${i + 1}: PU invalide.`);
      if (!((l.tax_rate ?? 0) >= 0))
        errs.push(`Ligne #${i + 1}: TVA invalide.`);
    });
    return errs;
  };

  const toApiPayload = (q: Quote): ApiQuoteUpdatePayload => {
    const payload: ApiQuoteUpdatePayload = {
      title: q.title,
      reference: q.reference,
      status: (q.status || '').toUpperCase(),
      issue_date: q.issue_date ?? null,
      valid_until: q.due_date ?? null,
      currency: q.currency ?? 'EUR',
      note: q.notes ?? '',
      metadata: {},
      client: q.client?.id, // UUID attendu par l'API
      client_update: {
        name: q.client?.name ?? '',
        email: q.client?.email ?? '',
        // ajoute ici phone/address/vat_number/metadata si supportés côté Client
      },
    };

    if ((q.line_items?.length ?? 0) > 0) {
      payload.items = q.line_items.map((l, i) => ({
        description: l.designation,
        qty: String(l.quantity),
        unit_price: String(Number(l.unit_price).toFixed(2)),
        // 0.2 (20%) -> "20.00"
        tax_rate: String(((l.tax_rate ?? 0) * 100).toFixed(2)),
        discount: '0.00',
        order: i,
        metadata: {},
      }));
    }

    return payload;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs = validate();
    if (errs.length) {
      setError(errs.join('\n'));
      return;
    }
    if (!id || !quote) return;

    setSaving(true);
    setError(null);
    try {
      const payload = toApiPayload(quote);
      await quoteRepository.update(id, payload);
      navigate(`/quotes/${id}`);
    } catch (err) {
      const e = err as { response?: { data?: unknown }; message?: string };
      setError(
        e.response?.data
          ? JSON.stringify(e.response.data)
          : (e.message ?? 'Erreur'),
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading || !quote) {
    return (
      <main className={`container mx-auto p-6 ${styles.page}`}>
        <div className={styles.skeletonHeader} />
        <div className={styles.skeletonCard} />
      </main>
    );
  }
  return (
    <main className={`container mx-auto p-6 grid gap-6 ${styles.page}`}>
      <header className={styles.header}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className={styles.title}>
              Éditer le devis — {quote.reference}
            </h1>
            <p className={styles.meta}>
              Modifiez les informations puis enregistrez.
            </p>
          </div>
          <div className="flex gap-2">
            <Link to={`/quotes/${quote.id}`} className={styles.buttonGhost}>
              Annuler
            </Link>
            <button
              className={styles.buttonPrimary}
              onClick={handleSubmit}
              disabled={saving}
            >
              {saving ? 'Enregistrement…' : 'Enregistrer'}
            </button>
          </div>
        </div>
      </header>

      {error && <div className={styles.errorBox}>⚠️ {error}</div>}

      <form onSubmit={handleSubmit} className="grid gap-6">
        {/* Bloc Devis */}
        <section className={styles.card}>
          <h2 className={styles.h2}>Devis</h2>
          <div className={styles.formGrid}>
            <label className={styles.label}>
              <span>Référence</span>
              <input
                className={styles.input}
                value={quote.reference}
                onChange={(e) => setField('reference', e.target.value)}
                placeholder="FS-2025-001"
              />
            </label>
            <label className={styles.label}>
              <span>Titre</span>
              <input
                className={styles.input}
                value={quote.title}
                onChange={(e) => setField('title', e.target.value)}
                placeholder="Site vitrine 5 pages"
              />
            </label>
            <label className={styles.label}>
              <span>Statut</span>
              <select
                className={styles.input}
                value={quote.status}
                onChange={(e) => setField('status', e.target.value)}
              >
                <option value="DRAFT">draft</option>
                <option value="SENT">sent</option>
                <option value="ACCEPTED">accepted</option>
                <option value="REJECTED">refused</option>
                <option value="EXPIRED">expired</option>
                <option value="PAID">paid</option>
              </select>
            </label>
            <label className={styles.label}>
              <span>Devise</span>
              <input
                className={styles.input}
                value={quote.currency ?? 'EUR'}
                onChange={(e) => setField('currency', e.target.value)}
                placeholder="EUR"
              />
            </label>
            <label className={styles.label}>
              <span>Date d’émission</span>
              <input
                type="date"
                className={styles.input}
                value={quote.issue_date ?? ''}
                onChange={(e) => setField('issue_date', e.target.value || null)}
              />
            </label>
            <label className={styles.label}>
              <span>Date de validité</span>
              <input
                type="date"
                className={styles.input}
                value={quote.due_date ?? ''}
                onChange={(e) => setField('due_date', e.target.value || null)}
              />
            </label>
          </div>
          <div className={styles.formGrid}>
            <label className={styles.labelCol}>
              <span>Notes</span>
              <textarea
                className={styles.textarea}
                value={quote.notes ?? ''}
                onChange={(e) => setField('notes', e.target.value)}
                rows={3}
                placeholder="Informations complémentaires visibles par le client…"
              />
            </label>
            <label className={styles.labelCol}>
              <span>Conditions</span>
              <textarea
                className={styles.textarea}
                value={quote.terms ?? ''}
                onChange={(e) => setField('terms', e.target.value)}
                rows={3}
                placeholder="Modalités de paiement, délais, pénalités, etc."
              />
            </label>
          </div>
        </section>

        {/* Bloc Client */}
        <section className={styles.card}>
          <h2 className={styles.h2}>Client</h2>
          <div className={styles.formGrid}>
            <label className={styles.label}>
              <span>Nom</span>
              <input
                className={styles.input}
                value={quote.client?.name ?? ''}
                onChange={(e) => setClient('name', e.target.value)}
              />
            </label>
            <label className={styles.label}>
              <span>Email</span>
              <input
                type="email"
                className={styles.input}
                value={quote.client?.email ?? ''}
                onChange={(e) => setClient('email', e.target.value)}
              />
            </label>
            <label className={styles.label}>
              <span>Entreprise</span>
              <input
                className={styles.input}
                value={quote.client?.company ?? ''}
                onChange={(e) => setClient('company', e.target.value)}
              />
            </label>
            <label className={styles.label}>
              <span>Adresse (ligne 1)</span>
              <input
                className={styles.input}
                value={quote.client?.address_line1 ?? ''}
                onChange={(e) => setClient('address_line1', e.target.value)}
              />
            </label>
            <label className={styles.label}>
              <span>Adresse (ligne 2)</span>
              <input
                className={styles.input}
                value={quote.client?.address_line2 ?? ''}
                onChange={(e) => setClient('address_line2', e.target.value)}
              />
            </label>
            <label className={styles.label}>
              <span>Ville</span>
              <input
                className={styles.input}
                value={quote.client?.city ?? ''}
                onChange={(e) => setClient('city', e.target.value)}
              />
            </label>
            <label className={styles.label}>
              <span>Code postal</span>
              <input
                className={styles.input}
                value={quote.client?.postal_code ?? ''}
                onChange={(e) => setClient('postal_code', e.target.value)}
              />
            </label>
            <label className={styles.label}>
              <span>Pays</span>
              <input
                className={styles.input}
                value={quote.client?.country ?? ''}
                onChange={(e) => setClient('country', e.target.value)}
              />
            </label>
          </div>
        </section>

        {/* Bloc Lignes */}
        <section className={styles.card}>
          <div className="flex items-center justify-between">
            <h2 className={styles.h2}>Lignes</h2>
            <button
              type="button"
              onClick={addLine}
              className={styles.buttonAccent}
            >
              + Ajouter une ligne
            </button>
          </div>

          {quote.line_items.length === 0 ? (
            <div className={styles.empty}>
              Aucune ligne. Ajoutez votre première ligne.
            </div>
          ) : (
            <div className={styles.tableWrapper}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Prestation</th>
                    <th>Description</th>
                    <th className="text-right">Qté</th>
                    <th className="text-right">PU HT</th>
                    <th className="text-right">TVA</th>
                    <th className="text-right">Total</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {quote.line_items.map((l, i) => {
                    const base = l.quantity * l.unit_price;
                    const tot = base * (1 + (l.tax_rate ?? 0));
                    return (
                      <tr key={i}>
                        <td>
                          <input
                            className={styles.input}
                            value={l.designation}
                            onChange={(e) =>
                              updateLine(i, { designation: e.target.value })
                            }
                            placeholder="Ex: Maquettage UI"
                          />
                        </td>
                        <td>
                          <input
                            className={styles.input}
                            value={l.description ?? ''}
                            onChange={(e) =>
                              updateLine(i, { description: e.target.value })
                            }
                            placeholder="Détail de la prestation"
                          />
                        </td>
                        <td className="text-right">
                          <input
                            className={`${styles.input} ${styles.inputNum}`}
                            type="number"
                            min={0}
                            step="1"
                            value={l.quantity}
                            onChange={(e) =>
                              updateLine(i, {
                                quantity: Number(e.target.value),
                              })
                            }
                          />
                        </td>
                        <td className="text-right">
                          <input
                            className={`${styles.input} ${styles.inputNum}`}
                            type="number"
                            min={0}
                            step="0.01"
                            value={l.unit_price}
                            onChange={(e) =>
                              updateLine(i, {
                                unit_price: Number(e.target.value),
                              })
                            }
                          />
                        </td>
                        <td className="text-right">
                          <input
                            className={`${styles.input} ${styles.inputNum}`}
                            type="number"
                            min={0}
                            step="0.01"
                            value={l.tax_rate ?? 0}
                            onChange={(e) =>
                              updateLine(i, {
                                tax_rate: Number(e.target.value),
                              })
                            }
                          />
                          <div className={styles.help}>ex: 0.2 pour 20%</div>
                        </td>
                        <td className="text-right">{money.format(tot)}</td>
                        <td className="text-right">
                          <button
                            type="button"
                            className={styles.buttonGhost}
                            onClick={() => removeLine(i)}
                          >
                            Suppr.
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
                <tfoot>
                  <tr>
                    <td colSpan={5} className="text-right">
                      Sous-total
                    </td>
                    <td className="text-right">{money.format(totals.sub)}</td>
                    <td />
                  </tr>
                  <tr>
                    <td colSpan={5} className="text-right">
                      TVA
                    </td>
                    <td className="text-right">{money.format(totals.tax)}</td>
                    <td />
                  </tr>
                  <tr>
                    <td
                      colSpan={5}
                      className={`${styles.totalLabel} text-right`}
                    >
                      Total
                    </td>
                    <td className={`${styles.totalValue} text-right`}>
                      {money.format(totals.total)}
                    </td>
                    <td />
                  </tr>
                </tfoot>
              </table>
            </div>
          )}
        </section>

        {/* Actions bas de page (fallback submit) */}
        <div className="flex items-center gap-2">
          <button className={styles.buttonPrimary} disabled={saving}>
            {saving ? 'Enregistrement…' : 'Enregistrer'}
          </button>
          <Link to={`/quotes/${quote.id}`} className={styles.buttonGhost}>
            Annuler
          </Link>
        </div>
      </form>
    </main>
  );
}
