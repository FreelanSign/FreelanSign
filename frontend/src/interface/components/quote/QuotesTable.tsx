import React from 'react'; // <-- important
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';

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

function statusBadgeClass(status?: string) {
  const s = (status ?? '').toLowerCase();
  if (s.includes('draft') || s.includes('brouillon'))
    return 'bg-gray-100 text-gray-800';
  if (s.includes('sent') || s.includes('envoyé') || s.includes('sent'))
    return 'bg-indigo-100 text-indigo-700';
  if (s.includes('accepted') || s.includes('accept'))
    return 'bg-green-100 text-green-800';
  if (s.includes('rejected') || s.includes('refused') || s.includes('cancel'))
    return 'bg-red-100 text-red-700';
  return 'bg-gray-100 text-gray-800';
}

function formatMoney(value?: number | string | null, currency?: string | null) {
  if (value == null || value === '') return '—';
  const n = Number(value);
  if (Number.isNaN(n)) return String(value);
  return `${n.toFixed(2)} ${currency ?? '€'}`;
}

/* Composant en React.FC : plus compatible avec plusieurs configs TSX */
const QuotesTable: React.FC<{ pageSize?: number }> = ({ pageSize = 5 }) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [data, setData] = useState<PageResponse<QuoteItem> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [page] = useState<number>(1);

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
        console.error('Load latest quotes error', err);
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

  return (
    <section className="bg-white rounded-lg shadow-sm border p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-medium">Derniers devis</h2>
        <div className="text-sm">
          <Link to="/quotes" className="text-indigo-600 hover:underline">
            Voir tout
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="py-8 text-center text-gray-500">Chargement…</div>
      ) : error ? (
        <div className="text-sm text-red-600">Erreur : {error}</div>
      ) : !data ||
        (Array.isArray(data.results) && data.results.length === 0) ? (
        <div className="py-8 text-center text-gray-600">
          Aucun devis trouvé.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm divide-y divide-gray-100">
            <thead>
              <tr>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  Réf
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  Titre
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  Statut
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                  Émis le
                </th>
                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">
                  Total
                </th>
                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">
                  Actions
                </th>
              </tr>
            </thead>

            <tbody className="bg-white divide-y divide-gray-100">
              {(data!.results as QuoteItem[]).map((q) => (
                <tr key={q.id}>
                  <td className="px-3 py-3 whitespace-nowrap text-gray-700">
                    {q.reference}
                  </td>
                  <td className="px-3 py-3 whitespace-nowrap text-gray-800">
                    {q.title}
                  </td>
                  <td className="px-3 py-3 whitespace-nowrap">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${statusBadgeClass(q.status)}`}
                    >
                      {q.status ?? '—'}
                    </span>
                  </td>
                  <td className="px-3 py-3 whitespace-nowrap text-gray-600">
                    {q.issue_date
                      ? new Date(q.issue_date).toLocaleDateString()
                      : '—'}
                  </td>
                  <td className="px-3 py-3 whitespace-nowrap text-right font-medium">
                    {formatMoney(q.total, q.currency)}
                  </td>
                  <td className="px-3 py-3 whitespace-nowrap text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link
                        to={`/quotes/${q.id}`}
                        className="text-indigo-600 text-sm hover:underline"
                      >
                        Voir
                      </Link>
                      <Link
                        to={`/quotes/${q.id}/edit`}
                        className="text-gray-600 text-sm hover:underline"
                      >
                        Éditer
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="mt-3 text-xs text-gray-500">
            {data && (
              <>
                {data.results.length} sur {data.count} — affichage limité à{' '}
                {pageSize}
              </>
            )}
          </div>
        </div>
      )}
    </section>
  );
};

export default QuotesTable;
