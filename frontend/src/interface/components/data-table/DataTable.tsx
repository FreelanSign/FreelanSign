import {
  type ColumnDef,
  type SortingState,
  type Updater,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { ChevronLeft, ChevronRight } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

export type DataTableState = {
  pageIndex: number; // 0-based
  pageSize: number;
  sorting: SortingState;
};

type DataTableProps<TData> = {
  columns: Array<ColumnDef<TData, unknown>>;
  data: TData[];
  rowCount: number;

  state: DataTableState;
  onStateChange: (next: DataTableState) => void;

  isLoading?: boolean;
  errorMessage?: string | null;
  emptyMessage?: string;
};

/**
 * AIDEV-NOTE: DataTable “server-driven”.
 * - manualPagination/manualSorting => le serveur est la source de vérité.
 * - Le tableau n’essaie PAS de trier/filtrer côté client.
 */
export function DataTable<TData>({
  columns,
  data,
  rowCount,
  state,
  onStateChange,
  isLoading = false,
  errorMessage = null,
  emptyMessage = 'Aucun résultat.',
}: DataTableProps<TData>) {
  const pageCount = Math.max(1, Math.ceil(rowCount / state.pageSize));

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),

    // server-driven
    manualPagination: true,
    manualSorting: true,
    pageCount,

    state: {
      pagination: { pageIndex: state.pageIndex, pageSize: state.pageSize },
      sorting: state.sorting,
    },

    onPaginationChange: (updater) => {
      const next =
        typeof updater === 'function'
          ? updater({ pageIndex: state.pageIndex, pageSize: state.pageSize })
          : updater;

      onStateChange({
        ...state,
        pageIndex: next.pageIndex,
        pageSize: next.pageSize,
      });
    },

    onSortingChange: (updater: Updater<SortingState>) => {
      const next =
        typeof updater === 'function' ? updater(state.sorting) : updater;
      // AIDEV-NOTE: On supporte 1 seul tri côté API. Si multi-tri UI un jour => adapter le contrat backend.
      onStateChange({ ...state, sorting: next });
    },
  });

  return (
    <div className="mt-6 space-y-4">
      {/* Zone d'Erreur améliorée (utilisant les couleurs destructives) */}
      {errorMessage ? (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-sm text-destructive-foreground/90">
          <p className="font-semibold text-destructive">
            Erreur de chargement des données
          </p>
          <p className="mt-1 opacity-90 text-sm">{errorMessage}</p>
        </div>
      ) : null}

      {/* Conteneur de la Table (avec une ombre douce pour la mise en évidence) */}
      <div className="rounded-lg bg-white border border-border bg-card shadow-lg overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50 border-b border-border">
            {table.getHeaderGroups().map((hg) => (
              <TableRow key={hg.id} className="hover:bg-muted/50">
                {hg.headers.map((header) => (
                  <TableHead
                    key={header.id}
                    className="text-sm font-semibold text-muted-foreground uppercase tracking-wider"
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>

          <TableBody>
            {/* État de Chargement */}
            {isLoading ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center text-base text-brand animate-pulse"
                >
                  Chargement des devis…
                </TableCell>
              </TableRow>
            ) : data.length === 0 ? (
              /* État Vide */
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center text-base text-muted-foreground"
                >
                  {emptyMessage}
                </TableCell>
              </TableRow>
            ) : (
              /* Données Normales */
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && 'selected'}
                  className="hover:bg-accent/50 transition-colors"
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between gap-4 py-2">
        <div className="text-sm text-muted-foreground flex items-center gap-1">
          {rowCount === 0 ? (
            'Aucun résultat'
          ) : (
            <>
              Affichage de l'élément{' '}
              <span className="font-semibold text-black">
                {Math.min(state.pageIndex * state.pageSize + 1, rowCount)}
              </span>
              {' à '}
              <span className="font-semibold text-black">
                {Math.min((state.pageIndex + 1) * state.pageSize, rowCount)}
              </span>
              {' sur '}
              <span className="font-semibold text-black">{rowCount}</span>
            </>
          )}
        </div>

        <div className="flex items-center gap-3">
          {/* Indicateur de page (optionnel mais utile) */}
          <div className="text-sm font-medium text-muted-foreground hidden sm:block">
            Page{' '}
            <span className="text-black font-semibold">
              {state.pageIndex + 1}
            </span>{' '}
            sur <span className="text-black font-semibold">{pageCount}</span>
          </div>

          <Button
            variant="default"
            size="sm"
            className="gap-1 border-input hover:bg-accent"
            onClick={() =>
              onStateChange({
                ...state,
                pageIndex: Math.max(0, state.pageIndex - 1),
              })
            }
            disabled={state.pageIndex <= 0 || isLoading}
          >
            <ChevronLeft className="h-4 w-4" />
            Précédent
          </Button>
          <Button
            variant="default"
            size="sm"
            className="gap-1 border-input hover:bg-accent"
            onClick={() =>
              onStateChange({
                ...state,
                pageIndex: Math.min(pageCount - 1, state.pageIndex + 1),
              })
            }
            disabled={state.pageIndex >= pageCount - 1 || isLoading}
          >
            Suivant
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
