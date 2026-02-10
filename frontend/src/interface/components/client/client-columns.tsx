import type { ColumnDef } from '@tanstack/react-table';
import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react';
import { Link } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { ClientActionsCell } from './ClientActionsCell';

export type ClientRow = {
  id: string;
  name: string;
  email?: string | null;
  phone?: string | null;
  created_at?: string | null;
};

/**
 * AIDEV-NOTE: Column definitions for client list.
 * - Sortable columns: name, created_at (matches backend ordering_fields)
 * - Dynamic visibility controlled by columnPrefs in parent component
 */
export const createClientColumns = (columnPrefs: {
  email: boolean;
  phone: boolean;
}): Array<ColumnDef<ClientRow, unknown>> => {
  const columns: Array<ColumnDef<ClientRow, unknown>> = [
    {
      accessorKey: 'name',
      header: ({ column }) => {
        const sorted = column.getIsSorted();
        return (
          <Button
            type="button"
            variant="ghost"
            className="px-0 h-8"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Nom
            {sorted === 'asc' ? (
              <ArrowUp className="ml-2 h-4 w-4 text-brand" />
            ) : sorted === 'desc' ? (
              <ArrowDown className="ml-2 h-4 w-4 text-brand" />
            ) : (
              <ArrowUpDown className="ml-2 h-4 w-4 opacity-50 text-muted-foreground" />
            )}
          </Button>
        );
      },
      enableSorting: true,
      cell: ({ row }) => {
        const client = row.original;
        return (
          <Link
            to={`/clients/${client.id}`}
            className="font-semibold hover:underline hover:text-brand"
          >
            {client.name}
          </Link>
        );
      },
    },
  ];

  // Email column (optional)
  if (columnPrefs.email) {
    columns.push({
      accessorKey: 'email',
      header: () => <span>Email</span>,
      cell: ({ row }) => (
        <span className="text-sm text-muted-foreground">
          {row.original.email || '—'}
        </span>
      ),
    });
  }

  // Phone column (optional)
  if (columnPrefs.phone) {
    columns.push({
      accessorKey: 'phone',
      header: () => <span>Téléphone</span>,
      cell: ({ row }) => (
        <span className="text-sm text-muted-foreground">
          {row.original.phone || '—'}
        </span>
      ),
    });
  }

  // Actions column (always visible)
  columns.push({
    id: 'actions',
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => <ClientActionsCell client={row.original} />,
  });

  return columns;
};
