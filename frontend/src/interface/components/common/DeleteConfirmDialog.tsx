// frontend/src/interface/components/common/DeleteConfirmDialog.tsx

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../../../components/ui/dialog';

interface DeleteConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  isDeleting?: boolean;
  errorMessage?: string | null;
}

export default function DeleteConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Supprimer',
  isDeleting = false,
  errorMessage = null,
}: DeleteConfirmDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription className="pt-4 pb-4">{message}</DialogDescription>
        </DialogHeader>

        {errorMessage && (
          <div className="p-3 rounded-md bg-red-50 text-red-800 text-sm">
            {errorMessage}
          </div>
        )}

        <DialogFooter className="mt-4">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isDeleting}
          >
            Annuler
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={onConfirm}
            disabled={isDeleting}
          >
            {isDeleting ? 'Suppression...' : confirmText}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
