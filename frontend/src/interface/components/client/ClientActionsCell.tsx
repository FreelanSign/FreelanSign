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
import { clientRepository } from '../../../infrastructure/client/clientRepository';
import type { ClientRow } from './client-columns';

/**
 * AIDEV-NOTE: Actions menu component for client row.
 * Uses DropdownMenu to avoid cluttering the table with multiple buttons.
 * Delete is always enabled (no status restriction like quotes).
 */
export function ClientActionsCell({ client }: { client: ClientRow }) {
  const navigate = useNavigate();
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  async function handleDelete() {
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await clientRepository.delete(client.id);
      setShowDeleteDialog(false);
      // Refresh page to update list
      window.location.reload();
    } catch (error: unknown) {
      const err = error as {
        response?: { data?: { detail?: string } };
        message?: string;
      };
      const detail = err.response?.data?.detail;

      // Check for active quotes error
      if (detail && detail.includes('devis')) {
        setDeleteError(
          "Impossible de supprimer ce client car il a des devis. Veuillez d'abord supprimer ses devis.",
        );
      } else {
        setDeleteError(
          err.response?.data?.detail ||
            err.message ||
            'Erreur lors de la suppression',
        );
      }
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
            <DropdownMenuItem onClick={() => navigate(`/clients/${client.id}`)}>
              <Eye className="mr-2 h-4 w-4" />
              Voir
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => navigate(`/clients/${client.id}/edit`)}
            >
              <Edit className="mr-2 h-4 w-4" />
              Éditer
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => setShowDeleteDialog(true)}
              className="text-destructive focus:text-destructive"
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
        title="Supprimer le client"
        message={`Êtes-vous sûr de vouloir supprimer le client "${client.name}" ? Cette action est irréversible.`}
        confirmText="Supprimer"
        isDeleting={isDeleting}
        errorMessage={deleteError}
      />
    </>
  );
}
