import type { SortingState } from '@tanstack/react-table';
import { Filter, LayoutDashboard, Plus, Search, X } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';

import { useAccountStore } from '../../../infrastructure/account/accountStore';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';

import {
  DataTable,
  type DataTableState,
} from '@/interface/components/data-table/DataTable';
import {
  quoteColumns,
  type QuoteRow,
} from '@/interface/components/quote/quotes-columns';

// AIDEV-NOTE: champs de tri autorisés côté API (ordering_fields backend).
const ALLOWED_ORDERING = new Set([
  'updated_at',
  'issue_date',
  'total',
] as const);
type AllowedOrdering = 'updated_at' | 'issue_date' | 'total';

function orderingToSorting(ordering: string | null): SortingState {
  const raw = ordering ?? '-updated_at';
  const desc = raw.startsWith('-');
  const field = (desc ? raw.slice(1) : raw) as string;
  if (!ALLOWED_ORDERING.has(field as AllowedOrdering))
    return [{ id: 'updated_at', desc: true }];
  return [{ id: field, desc }];
}

function sortingToOrdering(sorting: SortingState): string {
  const first = sorting[0];
  if (!first) return '-updated_at';
  const field = String(first.id);
  if (!ALLOWED_ORDERING.has(field as AllowedOrdering)) return '-updated_at';
  return `${first.desc ? '-' : ''}${field}`;
}

type PageResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

type QuoteItem = {
  id: string;
  reference: string;
  title: string;
  status: string;
  issue_date?: string | null;
  total?: number | string | null;
  currency?: string | null;
  // AIDEV-NOTE: adapte selon serializer list (client_name ou client:{name})
  client?: { id: string; name?: string | null } | null;
  client_name?: string | null;
};

export default function QuotesListPage() {
  const activeAccountId = useAccountStore((s) => s.activeAccountId);
  const [searchParams, setSearchParams] = useSearchParams();

  const page = useMemo(
    () => Number(searchParams.get('page') ?? '1'),
    [searchParams],
  );
  const pageSize = useMemo(
    () => Number(searchParams.get('page_size') ?? '20'),
    [searchParams],
  );
  const ordering = useMemo(
    () => searchParams.get('ordering') ?? '-updated_at',
    [searchParams],
  );

  const search = useMemo(
    () => searchParams.get('search') ?? '',
    [searchParams],
  );
  const [searchInput, setSearchInput] = useState(search);

  const statusFilter = useMemo(() => {
    const param = searchParams.get('status');
    return param ? param.split(',') : [];
  }, [searchParams]);

  useEffect(() => setSearchInput(search), [search]);

  function updateParams(updates: Record<string, string | null>) {
    const next = new URLSearchParams(searchParams);
    for (const [k, v] of Object.entries(updates)) {
      if (v === null || v === '') next.delete(k);
      else next.set(k, v);
    }
    setSearchParams(next);
  }

  useEffect(() => {
    const t = window.setTimeout(() => {
      updateParams({
        search: searchInput.trim() ? searchInput.trim() : null,
        page: '1',
      });
    }, 350);
    return () => window.clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchInput]);

  // --- data fetch ---
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<PageResponse<QuoteItem> | null>(null);
  const [error, setError] = useState<string | null>(null);

  // --- DataTable state (0-based pagination) ---
  const tableState: DataTableState = useMemo(
    () => ({
      pageIndex: Math.max(0, (Number.isFinite(page) ? page : 1) - 1),
      pageSize: Number.isFinite(pageSize) && pageSize > 0 ? pageSize : 20,
      sorting: orderingToSorting(ordering),
    }),
    [page, pageSize, ordering],
  );

  function onTableStateChange(next: DataTableState) {
    // AIDEV-NOTE: TanStack = 0-based, API DRF = 1-based
    updateParams({
      page: String(next.pageIndex + 1),
      page_size: String(next.pageSize),
      ordering: sortingToOrdering(next.sorting),
    });
  }

  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await quoteRepository.list({
          page: tableState.pageIndex + 1,
          page_size: tableState.pageSize,
          ordering: sortingToOrdering(tableState.sorting),
          search: search || undefined,
          status: statusFilter.length > 0 ? statusFilter : undefined,
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
  }, [
    tableState.pageIndex,
    tableState.pageSize,
    tableState.sorting,
    ordering,
    search,
    statusFilter,
    activeAccountId,
  ]);

  const rows: QuoteRow[] = useMemo(() => {
    const items = data?.results ?? [];
    return items.map((q) => ({
      id: q.id,
      reference: q.reference,
      title: q.title,
      status: q.status,
      issue_date: q.issue_date ?? null,
      total: q.total ?? null,
      currency: q.currency ?? 'EUR',
      // AIDEV-NOTE: adapte selon payload backend list
      client_name: q.client_name ?? q.client?.name ?? null,
    }));
  }, [data]);

  return (
    <div className="container mx-auto py-6 px-4 sm:px-6 lg:px-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 font-playfair">
            Mes devis
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Gérez vos devis et suivez leur statut
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Bouton Dashboard - conserve un style outline sobre */}
          <Button
            asChild
            variant="outline"
            className="border-input hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            <Link to="/dashboard">
              <LayoutDashboard className="h-4 w-4 mr-2" />
              Dashboard
            </Link>
          </Button>
          {/* Bouton Nouveau devis - utilise la couleur de marque */}
          <Button
            asChild
            className="bg-brand text-brand-foreground shadow-md hover:bg-brand/90 hover:shadow-lg transition-all duration-150 ease-in-out"
          >
            <Link to="/quotes/new">
              <Plus className="h-4 w-4 mr-2" />
              Nouveau devis
            </Link>
          </Button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="bg-white flex flex-col gap-3 sm:flex-row sm:items-center bg-card rounded-lg p-4 shadow-sm border border-border">
        {/* Recherche */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchInput}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setSearchInput(e.target.value)
            }
            placeholder="Rechercher (client, référence, titre…)"
            // Utilise les couleurs par défaut pour la bordure, mais le ring de marque
            className="pl-9 border-input focus-visible:ring-1 focus-visible:ring-offset-0 ring-brand"
          />
          {searchInput && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="absolute right-1 top-1/2 h-7 w-7 -translate-y-1/2 p-0 hover:bg-accent"
              onClick={() => setSearchInput('')}
            >
              <X className="h-4 w-4 text-muted-foreground" />
            </Button>
          )}
        </div>

        {/* Filtres et Réinitialisation */}
        <div className="flex items-center gap-2">
          {/* Filtre Statut */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              {/* Le bouton de filtre utilise les couleurs d'accentuation pour rester discret mais visible */}
              <Button
                variant="outline"
                className="gap-2 border-input hover:bg-accent hover:text-accent-foreground"
              >
                <Filter className="h-4 w-4 text-primary" />
                Statut
                {statusFilter.length > 0 && (
                  <Badge
                    variant="secondary"
                    className="ml-1 rounded-full px-2 font-medium bg-brand/10 text-brand border border-brand/20 hover:bg-brand/20 transition-colors"
                  >
                    {statusFilter.length}
                  </Badge>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="">
              <DropdownMenuLabel className="bg-muted text-foreground">
                Filtrer par statut
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="" />
              {[
                { value: 'DRAFT', label: 'Brouillon' },
                { value: 'SENT', label: 'Envoyé' },
                { value: 'ACCEPTED', label: 'Accepté' },
                { value: 'REJECTED', label: 'Refusé' },
                { value: 'PAID', label: 'Payé' },
                { value: 'EXPIRED', label: 'Expiré' },
              ].map((status) => (
                <DropdownMenuCheckboxItem
                  key={status.value}
                  checked={statusFilter.includes(status.value)}
                  onCheckedChange={(checked: boolean) => {
                    const newFilter = checked
                      ? [...statusFilter, status.value]
                      : statusFilter.filter((s) => s !== status.value);
                    updateParams({
                      status: newFilter.length > 0 ? newFilter.join(',') : null,
                      page: '1',
                    });
                  }}
                >
                  {status.label}
                </DropdownMenuCheckboxItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Bouton Réinitialiser */}
          <Button
            type="button"
            variant="outline"
            className="border-input hover:bg-accent hover:text-accent-foreground disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={() =>
              updateParams({
                search: null,
                ordering: '-updated_at',
                status: null,
                page: '1',
              })
            }
            disabled={
              !search && ordering === '-updated_at' && statusFilter.length === 0
            }
          >
            Réinitialiser
          </Button>
        </div>
      </div>

      {/* Tableau de Données */}
      <DataTable<QuoteRow>
        columns={quoteColumns}
        data={rows}
        rowCount={data?.count ?? 0}
        state={tableState}
        onStateChange={onTableStateChange}
        isLoading={loading}
        errorMessage={error}
        emptyMessage={
          search ? 'Aucun devis pour cette recherche.' : 'Aucun devis trouvé.'
        }
      />
    </div>
  );
}
