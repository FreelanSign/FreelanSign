import type { SortingState } from '@tanstack/react-table';
import { Plus, Search, X } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

import {
  createClientColumns,
  type ClientRow,
} from '@/interface/components/client/client-columns';
import {
  DataTable,
  type DataTableState,
} from '@/interface/components/data-table/DataTable';
import ClientCreateDrawer from '../../components/client/ClientCreateDrawer';

import { isAccountMissingError } from '@/domain/account/utils';
import type { ClientDto } from '../../../domain/client/types';
import {
  clientRepository,
  type PageResponse,
} from '../../../infrastructure/client/clientRepository';

/**
 * AIDEV-NOTE: Allowed ordering fields for client list (backend ordering_fields).
 * - name
 * - created_at
 */
const ALLOWED_ORDERING = new Set(['name', 'created_at'] as const);
type AllowedOrdering = 'name' | 'created_at';

function orderingToSorting(ordering: string | null): SortingState {
  const raw = ordering ?? 'name';
  const desc = raw.startsWith('-');
  const field = (desc ? raw.slice(1) : raw) as string;
  if (!ALLOWED_ORDERING.has(field as AllowedOrdering))
    return [{ id: 'name', desc: false }];
  return [{ id: field, desc }];
}

function sortingToOrdering(sorting: SortingState): string {
  const first = sorting[0];
  if (!first) return 'name';
  const field = String(first.id);
  if (!ALLOWED_ORDERING.has(field as AllowedOrdering)) return 'name';
  return `${first.desc ? '-' : ''}${field}`;
}

type ColumnPrefs = {
  email: boolean;
  phone: boolean;
};

const DEFAULT_COLUMNS: ColumnPrefs = {
  email: true,
  phone: true,
};

const STORAGE_KEY = 'freelansign_client_columns_v1';

export default function ClientsListPage() {
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
    () => searchParams.get('ordering') ?? 'name',
    [searchParams],
  );

  const search = useMemo(
    () => searchParams.get('search') ?? '',
    [searchParams],
  );
  const [searchInput, setSearchInput] = useState(search);

  // Column preferences from localStorage
  const [columnPrefs, setColumnPrefs] = useState<ColumnPrefs>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch {
        return DEFAULT_COLUMNS;
      }
    }
    return DEFAULT_COLUMNS;
  });

  // Data state
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<PageResponse<ClientDto> | null>(null);
  const [error, setError] = useState<unknown>(null);
  const navigate = useNavigate();

  // Drawer state
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Debounced search (500ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      const params = new URLSearchParams(searchParams);
      if (searchInput) {
        params.set('search', searchInput);
      } else {
        params.delete('search');
      }
      params.set('page', '1'); // Reset to page 1 on search
      setSearchParams(params, { replace: true });
    }, 500);
    return () => clearTimeout(timer);
  }, [searchInput, searchParams, setSearchParams]);

  // Fetch clients
  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await clientRepository.list({
          search: search || undefined,
          page,
          page_size: pageSize,
          ordering,
        });
        if (!active) return;
        setData(res);
      } catch (err: unknown) {
        if (!active) return;
        setError(err);
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [page, pageSize, ordering, search]);

  // DataTable state management
  const tableState: DataTableState = useMemo(
    () => ({
      pageIndex: page - 1, // 0-based
      pageSize,
      sorting: orderingToSorting(ordering),
    }),
    [page, pageSize, ordering],
  );

  const handleStateChange = (next: DataTableState) => {
    const params = new URLSearchParams(searchParams);
    params.set('page', String(next.pageIndex + 1)); // 1-based
    params.set('page_size', String(next.pageSize));
    params.set('ordering', sortingToOrdering(next.sorting));
    setSearchParams(params, { replace: true });
  };

  const toggleColumn = (col: keyof ColumnPrefs) => {
    const updated = { ...columnPrefs, [col]: !columnPrefs[col] };
    setColumnPrefs(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  };

  const handleClientCreated = async () => {
    // Refresh list
    try {
      const res = await clientRepository.list({
        search: search || undefined,
        page,
        page_size: pageSize,
        ordering,
      });
      setData(res);
    } catch {
      // Ignore error, list will refresh on next load
    }
  };

  const clearSearch = () => {
    setSearchInput('');
  };

  // Map ClientDto to ClientRow
  const rows: ClientRow[] = useMemo(() => {
    if (!data?.results) return [];
    return data.results.map((client) => ({
      id: client.id,
      name: client.name,
      email: client.email,
      phone: client.phone,
      created_at: client.created_at,
    }));
  }, [data]);

  const columns = useMemo(
    () => createClientColumns(columnPrefs),
    [columnPrefs],
  );

  // Compute error message
  const errorMsg: string | null =
    error && !isAccountMissingError(error)
      ? (() => {
          const e = error as {
            response?: { data?: unknown };
            message?: string;
          };
          const server = e.response?.data;
          return server ? JSON.stringify(server) : (e.message ?? 'Erreur');
        })()
      : null;

  return (
    <div className="container mx-auto py-6 px-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Mes clients</h1>
          <p className="text-muted-foreground mt-1">
            Gérez vos clients et leurs informations
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => setDrawerOpen(true)}
            className="bg-brand text-white hover:bg-brand-hover"
          >
            <Plus className="mr-2 h-4 w-4" />
            Nouveau client
          </Button>
        </div>
      </div>

      {/* Toolbar: Search + Column Preferences */}
      <div className="bg-white rounded-lg border border-border bg-card p-4 mb-6 space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className=" border-0 absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Rechercher par nom ou email..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="pl-10 pr-10"
          />
          {searchInput && (
            <button
              onClick={clearSearch}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Column Preferences */}
        <div className="flex items-center gap-4 flex-wrap">
          <span className="text-sm font-medium">Colonnes affichées :</span>
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm cursor-not-allowed opacity-60">
              <input
                type="checkbox"
                checked={true}
                disabled={true}
                className="rounded cursor-not-allowed"
              />
              Nom (obligatoire)
            </label>
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={columnPrefs.email}
                onChange={() => toggleColumn('email')}
                className="rounded cursor-pointer"
              />
              Email
            </label>
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={columnPrefs.phone}
                onChange={() => toggleColumn('phone')}
                className="rounded cursor-pointer"
              />
              Téléphone
            </label>
          </div>
        </div>

        {/* Active filters badge */}
        {(search ||
          Object.values(columnPrefs).filter((v) => !v).length > 0) && (
          <div className="flex items-center gap-2 flex-wrap">
            {search && (
              <Badge variant="secondary" className="gap-1">
                Recherche: {search}
                <X
                  className="h-3 w-3 cursor-pointer"
                  onClick={() => {
                    setSearchInput('');
                  }}
                />
              </Badge>
            )}
          </div>
        )}
      </div>

      {/* Message d'onboarding si erreur 403 */}
      {error && isAccountMissingError(error) ? (
        <div className="rounded-lg border border-brand/20 bg-brand/5 p-4">
          <p className="font-semibold text-brand-dark">
            Créez votre compte professionnel
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            Accédez à vos clients en complétant votre profil professionnel
          </p>
          <Button
            onClick={() => navigate('/onboarding-account')}
            className="mt-3 bg-brand hover:bg-brand-dark text-white"
          >
            Créer mon compte
          </Button>
        </div>
      ) : null}

      {/* DataTable */}
      <DataTable
        columns={columns}
        data={rows}
        rowCount={data?.count ?? 0}
        state={tableState}
        onStateChange={handleStateChange}
        isLoading={loading}
        errorMessage={errorMsg}
        emptyMessage={
          search
            ? 'Aucun client trouvé pour cette recherche.'
            : 'Aucun client. Créez votre premier client !'
        }
      />

      {/* Create Drawer */}
      <ClientCreateDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onClientCreated={handleClientCreated}
      />
    </div>
  );
}
