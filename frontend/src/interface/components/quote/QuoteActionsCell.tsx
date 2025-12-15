import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MoreVertical, Eye, Edit, Trash2 } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import DeleteConfirmDialog from '../common/DeleteConfirmDialog';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';
import type { QuoteRow } from './quotes-columns';

/**
 * AIDEV-NOTE: Actions menu component for quote row.
 * Uses DropdownMenu to avoid cluttering the table with multiple buttons.
 */
export function QuoteActionsCell({ quote }: { quote: QuoteRow }) {
  const navigate = useNavigate();
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const activeStatuses = ['DRAFT', 'SENT', 'ACCEPTED'];
  const isDeleteDisabled = activeStatuses.includes(quote.status);

  async function handleDelete() {
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await quoteRepository.delete(quote.id);
      setShowDeleteDialog(false);
      // Refresh page to update list
      window.location.reload();
    } catch (error: unknown) {
      const err = error as {
        response?: { data?: { detail?: string } };
        message?: string;
      };
      const errorMsg =
        err.response?.data?.detail ||
        err.message ||
        'Erreur lors de la suppression';
      setDeleteError(errorMsg);
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <>
      <div className="flex justify-end">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
              <span className="sr-only">Ouvrir le menu</span>
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => navigate(`/quotes/${quote.id}`)}>
              <Eye className="mr-2 h-4 w-4" />
              Voir
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => navigate(`/quotes/${quote.id}/edit`)}
            >
              <Edit className="mr-2 h-4 w-4" />
              Éditer
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => setShowDeleteDialog(true)}
              disabled={isDeleteDisabled}
              className="text-destructive focus:text-destructive"
              title={
                isDeleteDisabled
                  ? 'La suppression est bloquée pour les devis en cours (Brouillon, Envoyé, Accepté)'
                  : 'Supprimer le devis'
              }
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Supprimer
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <DeleteConfirmDialog
        open={showDeleteDialog}
        onClose={() => {
          setShowDeleteDialog(false);
          setDeleteError(null);
        }}
        onConfirm={handleDelete}
        title="Supprimer le devis"
        message={`Êtes-vous sûr de vouloir supprimer le devis "${quote.reference}" ? Cette action peut être annulée.`}
        confirmText="Supprimer"
        isDeleting={isDeleting}
        errorMessage={deleteError}
      />
    </>
  );
}
