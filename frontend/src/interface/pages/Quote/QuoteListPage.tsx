// src/interface/pages/QuotesListPage.tsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';

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

/** type pour la page renvoyée par DRF */
type PageResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

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
        // safe extraction from unknown error shape
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

  return (
    <main className="container mx-auto p-6 grid gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Mes devis</h1>
        <Link
          to="/quotes/new"
          className="bg-green-600 text-white px-3 py-2 rounded"
        >
          + Nouveau devis
        </Link>
      </div>

      {loading ? (
        <div>Chargement des devis…</div>
      ) : error ? (
        <div className="text-red-600">Erreur : {error}</div>
      ) : (
        <>
          {!data ||
          (Array.isArray(data.results) && data.results.length === 0) ? (
            <div>Aucun devis trouvé.</div>
          ) : (
            <div className="grid gap-3">
              {(data.results as QuoteItem[]).map((q) => (
                <article
                  key={q.id}
                  className="p-4 border rounded flex justify-between items-start"
                >
                  <div>
                    <div className="text-sm text-gray-500">{q.status}</div>
                    <div className="text-lg font-medium">
                      {q.reference} — {q.title}
                    </div>
                    <div className="text-sm text-gray-600">
                      Émis le: {q.issue_date ?? '—'}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold">
                      {q.total != null
                        ? `${Number(q.total).toFixed(2)} ${q.currency ?? '€'}`
                        : '—'}
                    </div>
                    <div className="mt-2 flex gap-2">
                      <Link
                        to={`/quotes/${q.id}`}
                        className="text-sm underline"
                      >
                        Voir
                      </Link>
                      <Link
                        to={`/quotes/${q.id}/edit`}
                        className="text-sm underline"
                      >
                        Éditer
                      </Link>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}

          {/* Pagination simple */}
          <div className="flex items-center justify-between mt-4">
            <div>
              Page {page} — {data?.count ?? '—'} items
            </div>
            <div className="flex gap-2">
              <button
                onClick={prev}
                disabled={!prev}
                className="px-3 py-1 bg-gray-200 rounded"
              >
                Précédent
              </button>
              <button
                onClick={next}
                disabled={!next}
                className="px-3 py-1 bg-gray-200 rounded"
              >
                Suivant
              </button>
            </div>
          </div>
        </>
      )}
    </main>
  );
}
