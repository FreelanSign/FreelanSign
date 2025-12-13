// frontend/src/interface/components/common/DeleteConfirmDialog.tsx

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
      <DialogContent style={{ maxWidth: '500px' }}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{message}</DialogDescription>
        </DialogHeader>

        {errorMessage && (
          <div
            style={{
              padding: '12px',
              borderRadius: '6px',
              backgroundColor: '#fee',
              color: '#c33',
              fontSize: '14px',
            }}
          >
            {errorMessage}
          </div>
        )}

        <DialogFooter style={{ marginTop: '16px' }}>
          <button
            type="button"
            onClick={onClose}
            disabled={isDeleting}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              border: '1px solid #ddd',
              background: 'white',
              cursor: isDeleting ? 'not-allowed' : 'pointer',
              opacity: isDeleting ? 0.6 : 1,
            }}
          >
            Annuler
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isDeleting}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              border: 'none',
              background: '#dc2626',
              color: 'white',
              cursor: isDeleting ? 'not-allowed' : 'pointer',
              opacity: isDeleting ? 0.6 : 1,
            }}
          >
            {isDeleting ? 'Suppression...' : confirmText}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
