import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { AlertCircle } from 'lucide-react';

interface BetaWarningDialogProps {
  open: boolean;
  onClose: () => void;
  onDismissForever: () => void;
}

export function BetaWarningDialog({
  open,
  onClose,
  onDismissForever,
}: BetaWarningDialogProps) {
  const [dontShowAgain, setDontShowAgain] = useState(false);

  const handleClose = () => {
    if (dontShowAgain) {
      onDismissForever();
    }
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-orange-500" />
            <DialogTitle>Compte Beta - Phase de Test</DialogTitle>
          </div>
        </DialogHeader>

        <div className="space-y-3 pt-2">
          <DialogDescription>
            Vous utilisez actuellement FreelanSign en version{' '}
            <strong>beta</strong>.
          </DialogDescription>

          <div className="space-y-2 text-sm text-muted-foreground">
            <p className="font-medium">Pendant cette phase:</p>
            <ul className="list-disc list-inside space-y-1 pl-2">
              <li>Aucune limitation d'usage</li>
              <li>Des pertes de données peuvent survenir</li>
              <li>La disponibilité (SLA) n'est pas garantie</li>
            </ul>
          </div>

          <p className="text-sm text-muted-foreground">
            Vos retours sont précieux ! Contactez-nous à{' '}
            <a
              href="mailto:freelansign@gmail.com"
              className="text-blue-600 hover:underline"
            >
              freelansign@gmail.com
            </a>
          </p>
        </div>

        <DialogFooter className="flex-col gap-3 sm:flex-col sm:space-x-0">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="dont-show"
              checked={dontShowAgain}
              onCheckedChange={(checked) => setDontShowAgain(checked === true)}
            />
            <Label
              htmlFor="dont-show"
              className="text-sm font-normal cursor-pointer"
            >
              Ne plus afficher ce message
            </Label>
          </div>

          <Button onClick={handleClose} className="w-full">
            J'ai compris
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
