import type { ColumnDef } from '@tanstack/react-table';
import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react';
import { Link } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { StatusPill } from './quote-column-components';
import { formatDate, formatMoney } from './quote-utils';

export type QuoteRow = {
  id: string;
  reference: string;
  title: string;
  status: string;
  issue_date?: string | null;
  total?: number | string | null;
  currency?: string | null;
  client_name?: string | null;
};

/**
 * AIDEV-NOTE: On active le sorting sur les colonnes qui matchent les champs backend:
 * - issue_date
 * - total
 * - updated_at (si tu l’ajoutes en colonne plus tard)
 */
export const quoteColumns: Array<ColumnDef<QuoteRow, unknown>> = [
  {
    accessorKey: 'reference',
    header: () => <span>Référence</span>,
    cell: ({ row }) => {
      const q = row.original;
      return (
        // Utilise text-brand pour lex lien principal
        <Link
          to={`/quotes/${q.id}`}
          className="font-medium hover:underline hover:text-brand"
        >
          {q.reference || '—'}
        </Link>
      );
    },
  },
  {
    accessorKey: 'client_name',
    header: () => <span>Client</span>,
    // Texte en gris plus discret
    cell: ({ row }) => (
      <span className="text-muted-foreground">
        {row.original.client_name ?? '—'}
      </span>
    ),
  },
  {
    accessorKey: 'status',
    header: () => <span>Statut</span>,
    cell: ({ row }) => <StatusPill status={row.original.status} />,
  },
  {
    accessorKey: 'issue_date',
    header: ({ column }) => {
      const sorted = column.getIsSorted();
      return (
        // Les boutons de tri n'ont plus de style `hover:bg-transparent` mais utilisent `ghost` par défaut
        <Button
          type="button"
          variant="ghost"
          className="px-0 h-8" // Fixe la hauteur
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        >
          Date d'émission
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
    cell: ({ row }) => (
      <span className="text-sm">{formatDate(row.original.issue_date)}</span>
    ),
  },
  {
    accessorKey: 'total',
    header: ({ column }) => {
      const sorted = column.getIsSorted();
      return (
        <Button
          type="button"
          variant="ghost"
          className="px-0 h-8"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        >
          Total
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
    cell: ({ row }) => (
      // Ajout de font-semibold pour mettre le total en valeur
      <span className="tabular-nums font-semibold">
        {formatMoney(row.original.total, row.original.currency)}
      </span>
    ),
  },
  {
    id: 'actions',
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => {
      const q = row.original;
      return (
        <div className="flex justify-end gap-2">
          {/* Boutons d'action : Utilise `outline` pour rester discret, ou `ghost` si vous voulez encore moins de visibilité */}
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
      );
    },
  },
];
