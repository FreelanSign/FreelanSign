// src/interface/pages/Dashboard/components/DashboardLatestQuotesTable.tsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

import { useAccountStore } from '@/infrastructure/account/accountStore';
import { quoteRepository } from '@/infrastructure/quote/quoteRepository';

import { StatusPill } from '@/interface/components/quote/quote-column-components';
import {
  formatDate,
  formatMoney,
} from '@/interface/components/quote/quote-utils';

type QuoteItem = {
  id: string;
  reference: string;
  status: string;
  issue_date?: string | null;
  total?: number | string | null;
  currency?: string | null;
  // AIDEV-NOTE: list serializer peut renvoyer client_name OU client{name}. On gère les deux.
  client?: { id: string; name?: string | null } | null;
  client_name?: string | null;
};

type PageResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

type Props = {
  pageSize?: number;
};

export function DashboardLatestQuotesTable({ pageSize = 5 }: Props) {
  const activeAccountId = useAccountStore((s) => s.activeAccountId);

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<PageResponse<QuoteItem> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    (async () => {
      setLoading(true);
      setError(null);

      try {
        // AIDEV-NOTE: On force ordering -updated_at pour "derniers devis" (sinon dépend du backend).
        const res = await quoteRepository.list({
          page: 1,
          page_size: pageSize,
          ordering: '-updated_at',
        });

        if (!active) return;
        setData(res as PageResponse<QuoteItem>);
      } catch (err: unknown) {
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
  }, [pageSize, activeAccountId]);

  const rows = data?.results ?? [];

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Derniers devis
          </h2>
          <p className="text-sm text-muted-foreground">
            Les {pageSize} devis les plus récents
          </p>
        </div>

        <Button
          asChild
          variant="outline"
          className="border-input hover:bg-accent"
        >
          <Link to="/quotes">Voir tout</Link>
        </Button>
      </div>

      {/* Zone d'erreur (même style que DataTable) */}
      {error ? (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-sm text-destructive-foreground/90">
          <p className="font-semibold text-destructive">
            Erreur de chargement des devis
          </p>
          <p className="mt-1 opacity-90 text-sm">{error}</p>
        </div>
      ) : null}

      {/* Conteneur tableau (même look que DataTable) */}
      <div className="rounded-lg border border-border bg-card shadow-lg overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50 border-b border-border">
            <TableRow className="hover:bg-muted/50">
              <TableHead className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                Référence
              </TableHead>
              <TableHead className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                Client
              </TableHead>
              <TableHead className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                Statut
              </TableHead>
              <TableHead className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                Date
              </TableHead>
              <TableHead className="text-sm font-semibold text-muted-foreground uppercase tracking-wider text-right">
                Total
              </TableHead>
              <TableHead className="text-sm font-semibold text-muted-foreground uppercase tracking-wider text-right">
                Actions
              </TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell
                  colSpan={6}
                  className="h-24 text-center text-base text-brand animate-pulse"
                >
                  Chargement des devis…
                </TableCell>
              </TableRow>
            ) : rows.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={6}
                  className="h-24 text-center text-base text-muted-foreground"
                >
                  Aucun devis trouvé.
                </TableCell>
              </TableRow>
            ) : (
              rows.map((q) => {
                const clientName = q.client_name ?? q.client?.name ?? '—';

                return (
                  <TableRow
                    key={q.id}
                    className="hover:bg-accent/50 transition-colors"
                  >
                    <TableCell>
                      <Link
                        to={`/quotes/${q.id}`}
                        className="font-medium hover:underline hover:text-brand"
                      >
                        {q.reference || '—'}
                      </Link>
                    </TableCell>

                    <TableCell className="text-muted-foreground">
                      {clientName}
                    </TableCell>

                    <TableCell>
                      <StatusPill status={q.status} />
                    </TableCell>

                    <TableCell className="text-sm">
                      {formatDate(q.issue_date)}
                    </TableCell>

                    <TableCell className="text-right tabular-nums font-semibold">
                      {formatMoney(q.total, q.currency ?? 'EUR')}
                    </TableCell>

                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Link to={`/quotes/${q.id}`}>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            className="hover:bg-accent hover:text-accent-foreground"
                          >
                            Voir
                          </Button>
                        </Link>
                        <Link to={`/quotes/${q.id}/edit`}>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            className="hover:bg-accent hover:text-accent-foreground"
                          >
                            Éditer
                          </Button>
                        </Link>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      {/* Footer léger optionnel */}
      {!loading && !error && data ? (
        <div className="text-xs text-muted-foreground">
          Affichage : {Math.min(rows.length, pageSize)} / {data.count}
        </div>
      ) : null}
    </section>
  );
}
