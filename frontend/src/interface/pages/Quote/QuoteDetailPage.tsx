import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';
import QuoteEmailPreviewDialog from '../../components/email/QuoteEmailPreviewDialog';
import Navbar from '../../components/navbar/Navbar';
import Sidebar from '../../components/sidebar/Sidebar';
import styles from './quote-detail.module.css';

import { apiToUiQuoteDetail } from '../../../domain/quote/mappers';
import type {
  ApiQuoteResponse,
  UiQuoteDetail,
} from '../../../domain/quote/types';

function useIntlFormatters(currency: string | null | undefined) {
  const money = useMemo(
    () =>
      new Intl.NumberFormat(undefined, {
        style: 'currency',
        currency: currency ?? 'EUR',
        currencyDisplay: 'symbol',
        maximumFractionDigits: 2,
      }),
    [currency],
  );
  const date = useMemo(
    () =>
      new Intl.DateTimeFormat(undefined, {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
      }),
    [],
  );
  return { money, date };
}

function StatusBadge({ status }: { status: string }) {
  const s = (status ?? '').toLowerCase();
  const map: Record<string, string> = {
    draft: styles.badgeNeutral,
    sent: styles.badgeInfo,
    accepted: styles.badgeSuccess,
    rejected: styles.badgeDanger,
    refused: styles.badgeDanger,
    expired: styles.badgeWarning,
    paid: styles.badgeSuccess,
    cancelled: styles.badgeNeutral,
    canceled: styles.badgeNeutral,
  };
  const cls = map[s] ?? styles.badgeNeutral;
  return <span className={`${styles.badge} ${cls}`}>{status}</span>;
}

export default function QuoteDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(false);
  const [quote, setQuote] = useState<UiQuoteDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [showEmailDialog, setShowEmailDialog] = useState(false);

  async function handleDownload() {
    try {
      setDownloading(true);
      await quoteRepository.downloadPdf(id ?? '');
    } catch (err) {
      alert((err as Error).message || 'Erreur téléchargement PDF');
    } finally {
      setDownloading(false);
    }
  }

  useEffect(() => {
    if (!id) return;
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const api: ApiQuoteResponse = await quoteRepository.retrieve(id);
        if (!active) return;
        const mapped = apiToUiQuoteDetail(api);
        setQuote(mapped);
      } catch (err) {
        const e = err as { response?: { data?: unknown }; message?: string };
        const server = e.response?.data;
        setError(server ? JSON.stringify(server) : (e.message ?? 'Erreur'));
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [id]);

  const { money, date } = useIntlFormatters(quote?.currency ?? 'EUR');

  const computed = useMemo(() => {
    if (!quote) return null;
    const lines = quote.line_items ?? [];
    const sub =
      quote.subtotal ??
      lines.reduce(
        (acc, l) => acc + (l.pre_tax_total ?? l.quantity * l.unit_price),
        0,
      );
    const taxes =
      quote.tax_total ??
      lines.reduce(
        (acc, l) =>
          acc +
          (l.tax_amount ??
            (l.pre_tax_total ?? l.quantity * l.unit_price) * (l.tax_rate ?? 0)),
        0,
      );
    const total = quote.total ?? sub + taxes - (quote.discount_total ?? 0);
    return { sub, taxes, total };
  }, [quote]);

  const Shell: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <div>
      <Sidebar />
      <div className={styles.page}>
        <Navbar />
        <main className={`${styles.inner} container mx-auto grid gap-6`}>
          {children}
        </main>
      </div>
    </div>
  );

  if (loading) {
    return (
      <Shell>
        <div className={styles.skeletonHeader} />
        <div className={styles.skeletonCard} />
        <div className={styles.skeletonTable} />
      </Shell>
    );
  }

  if (error) {
    return (
      <Shell>
        <div className="text-red-600">Erreur : {error}</div>
        <Link to="/quotes" className={styles.buttonGhost}>
          ← Retour à la liste
        </Link>
      </Shell>
    );
  }

  if (!quote) {
    return (
      <Shell>
        <div>Aucun devis à afficher.</div>
        <Link to="/quotes" className={styles.buttonGhost}>
          ← Retour à la liste
        </Link>
      </Shell>
    );
  }

  const addressLines = (quote.client?.address || '')
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean);

  return (
    <Shell>
      <header className={styles.header}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className={styles.title}>
                {quote.reference} — {quote.title}
              </h1>
              <StatusBadge status={quote.status} />
            </div>
            <p className={styles.meta}>
              Émis le{' '}
              {quote.issue_date ? date.format(new Date(quote.issue_date)) : '—'}
              {quote.valid_until ? (
                <>
                  {' '}
                  • Valide jusqu’au {date.format(new Date(quote.valid_until))}
                </>
              ) : null}
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Link to="/quotes" className={styles.buttonGhost}>
              ← Retour
            </Link>
            <Link
              to={`/quotes/${quote.id}/edit`}
              className={styles.buttonPrimary}
            >
              Éditer
            </Link>
            <button
              onClick={handleDownload}
              disabled={downloading}
              className={styles.buttonAccent}
              title="Télécharger le devis (PDF)"
            >
              {downloading ? 'Téléchargement en cours...' : 'Télécharger (PDF)'}
            </button>
            <button
              className={styles.buttonSuccess}
              onClick={() => setShowEmailDialog(true)}
            >
              Préparer email
            </button>
          </div>
        </div>
      </header>

      {/* Infos Client & Devis */}
      <section className={styles.card}>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h2 className={styles.h2}>Client</h2>
            <div className={styles.kv}>
              <span>Nom</span>
              <strong>{quote.client?.name || '—'}</strong>
            </div>
            <div className={styles.kv}>
              <span>Email</span>
              <strong>
                {quote.client?.email ? (
                  <a
                    className={styles.link}
                    href={`mailto:${quote.client.email}`}
                  >
                    {quote.client.email}
                  </a>
                ) : (
                  '—'
                )}
              </strong>
            </div>
            <div className={styles.kv}>
              <span>Téléphone</span>
              <strong>
                {quote.client?.phone ? (
                  <a className={styles.link} href={`tel:${quote.client.phone}`}>
                    {quote.client.phone}
                  </a>
                ) : (
                  '—'
                )}
              </strong>
            </div>
            <div className={styles.kv}>
              <span>N° TVA</span>
              <strong>{quote.client?.vat_number || '—'}</strong>
            </div>
            <address className={styles.address}>
              {addressLines.length
                ? addressLines.map((l, i) => <div key={i}>{l}</div>)
                : '—'}
            </address>
          </div>

          <div>
            <h2 className={styles.h2}>Détails</h2>
            <div className={styles.kv}>
              <span>Référence</span>
              <strong>{quote.reference}</strong>
            </div>
            <div className={styles.kv}>
              <span>Statut</span>
              <strong className="capitalize">{quote.status}</strong>
            </div>
            <div className={styles.kv}>
              <span>Devise</span>
              <strong>{quote.currency ?? 'EUR'}</strong>
            </div>
          </div>
        </div>
      </section>

      {/* Lignes */}
      <section className={styles.card}>
        <h2 className={styles.h2}>Prestations</h2>
        {!quote.line_items || quote.line_items.length === 0 ? (
          <div className={styles.empty}>Aucune ligne de devis.</div>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Prestation</th>
                  <th className="text-right">Qté</th>
                  <th className="text-right">PU HT</th>
                  <th className="text-right">TVA</th>
                  <th className="text-right">Total</th>
                </tr>
              </thead>
              <tbody>
                {quote.line_items.map((l) => {
                  const total =
                    l.total ??
                    (l.pre_tax_total ?? l.quantity * l.unit_price) +
                      (l.tax_amount ?? 0);
                  return (
                    <tr key={String(l.id)}>
                      <td>
                        <div className="font-medium">{l.designation}</div>
                        {l.description ? (
                          <div className={styles.desc}>{l.description}</div>
                        ) : null}
                      </td>
                      <td className="text-right">{l.quantity}</td>
                      <td className="text-right">
                        {money.format(l.unit_price)}
                      </td>
                      <td className="text-right">
                        {((l.tax_rate ?? 0) * 100).toFixed(2)}%
                      </td>
                      <td className="text-right">{money.format(total)}</td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr>
                  <td colSpan={4} className="text-right">
                    Sous-total
                  </td>
                  <td className="text-right">{money.format(computed!.sub)}</td>
                </tr>
                <tr>
                  <td colSpan={4} className="text-right">
                    TVA
                  </td>
                  <td className="text-right">
                    {money.format(computed!.taxes)}
                  </td>
                </tr>
                <tr>
                  <td colSpan={4} className={`${styles.totalLabel} text-right`}>
                    Total
                  </td>
                  <td className={`${styles.totalValue} text-right`}>
                    {money.format(computed!.total)}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        )}
      </section>

      {!!quote.note && (
        <section className={styles.card}>
          <h3 className={styles.h3}>Notes</h3>
          <p className={styles.prose}>{quote.note}</p>
        </section>
      )}

      <QuoteEmailPreviewDialog
        open={showEmailDialog}
        onClose={() => setShowEmailDialog(false)}
        quoteId={quote.id}
      />
    </Shell>
  );
}
