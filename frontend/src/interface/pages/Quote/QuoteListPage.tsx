import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Sidebar from '../../components/sidebar/Sidebar';
import Navbar from '../../components/navbar/Navbar';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';
import styles from './quotes-list.module.css';

/**
 * Liste des devis de l'utilisateur.
 * Affiche : référence, titre, status, issue_date, total, lien détail.
 * Pagination simple (prev / next).
 */
type QuoteItem = {
  id: string;
  reference: string;
  title: string;
  status: string;
  issue_date?: string | null;
  total?: number | string | null;
  currency?: string | null;
};
type PageResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

function StatusBadge({ status }: { status: string }) {
  const s = (status ?? '').toLowerCase();
  const map: Record<string, string> = {
    draft: styles.badge,
    sent: `${styles.badge} ${styles.badgeInfo}`,
    accepted: `${styles.badge} ${styles.badgeSuccess}`,
    paid: `${styles.badge} ${styles.badgeSuccess}`,
    expired: `${styles.badge} ${styles.badgeWarning}`,
    refused: `${styles.badge} ${styles.badgeDanger}`,
    rejected: `${styles.badge} ${styles.badgeDanger}`,
    cancelled: styles.badge,
    canceled: styles.badge,
  };
  return <span className={map[s] ?? styles.badge}>{status}</span>;
}

export default function QuotesListPage() {
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(20);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<PageResponse<QuoteItem> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await quoteRepository.list({ page, page_size: pageSize });
        if (!active) return;
        setData(res as PageResponse<QuoteItem>);
      } catch (err: unknown) {
        console.error('Load quotes error', err);
        if (!active) return;
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
  }, [page, pageSize]);

  const next = data?.next ? () => setPage((p) => p + 1) : undefined;
  const prev = data?.previous
    ? () => setPage((p) => Math.max(1, p - 1))
    : undefined;

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
        <div className={styles.skel + ' ' + styles.skelHeader} />
        <div className={styles.card}>
          <div className={styles.skel + ' ' + styles.skelItem} />
          <div className={styles.skel + ' ' + styles.skelItem} />
          <div className={styles.skel + ' ' + styles.skelItem} />
        </div>
      </Shell>
    );
  }

  if (error) {
    return (
      <Shell>
        <div className={styles.headerRow}>
          <h1 className={styles.title}>Mes devis</h1>
          <Link
            to="/quotes/new"
            className={`${styles.btn} ${styles.btnPrimary}`}
          >
            + Nouveau devis
          </Link>
        </div>
        <div className={styles.error}>Erreur : {error}</div>
      </Shell>
    );
  }

  return (
    <Shell>
      <div className={styles.headerRow}>
        <h1 className={styles.title}>Mes devis</h1>
        <div className={styles.actions}>
          <Link
            to="/quotes/new"
            className={`${styles.btn} ${styles.btnPrimary}`}
          >
            + Nouveau devis
          </Link>
          <Link to="/dashboard" className={`${styles.btn} ${styles.btnGhost}`}>
            ← Dashboard
          </Link>
        </div>
      </div>

      {!data || (Array.isArray(data.results) && data.results.length === 0) ? (
        <div className={styles.empty}>Aucun devis trouvé.</div>
      ) : (
        <div className={styles.card}>
          <div className={styles.list}>
            {(data.results as QuoteItem[]).map((q) => (
              <article key={q.id} className={styles.item}>
                <div className="flex-1 itemLeft">
                  <div>
                    <small>
                      <StatusBadge status={q.status} />
                    </small>
                  </div>
                  <div className={styles.itemTitle}>
                    {q.reference} — {q.title}
                  </div>
                  <div className={styles.itemMeta}>
                    Émis le&nbsp;
                    {q.issue_date
                      ? new Intl.DateTimeFormat(undefined, {
                          year: 'numeric',
                          month: 'short',
                          day: '2-digit',
                        }).format(new Date(q.issue_date))
                      : '—'}
                  </div>
                </div>

                <div className={styles.itemActions}>
                  <div className={styles.itemTotal}>
                    {q.total != null
                      ? `${Number(q.total).toFixed(2)} ${q.currency ?? '€'}`
                      : '—'}
                  </div>
                  <div className="mt-2 flex gap-2 justify-end">
                    <Link to={`/quotes/${q.id}`} className={styles.link}>
                      Voir
                    </Link>
                    <Link to={`/quotes/${q.id}/edit`} className={styles.link}>
                      Éditer
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </div>

          {/* Pagination */}
          <div className={styles.pagination}>
            <div>
              Page {page} — {data?.count ?? '—'} items
            </div>
            <div className="flex gap-2">
              <button
                onClick={prev}
                disabled={!prev}
                className={styles.pagerBtn}
              >
                Précédent
              </button>
              <button
                onClick={next}
                disabled={!next}
                className={styles.pagerBtn}
              >
                Suivant
              </button>
            </div>
          </div>
        </div>
      )}
    </Shell>
  );
}
