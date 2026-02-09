// components/feedback/FeedbackModal.tsx
import emailjs from '@emailjs/browser';
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../app/providers/AuthProvider';
import {
  feedbackSchema,
  type FeedbackFormData,
} from '../../domain/feedback/schema';
import { feedbackRepository } from '../../infrastructure/feedback/feedbackRepository';
import {
  EMAILJS_PUBLIC_KEY,
  EMAILJS_SERVICE_ID,
  EMAILJS_TEMPLATE_ID,
} from '../../lib/constants/emailjs';
import { SITE } from '../../lib/constants/site.config';
import { Button } from '../ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Label } from '../ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { Textarea } from '../ui/textarea';

interface FeedbackModalProps {
  open: boolean;
  onClose: () => void;
}

const CATEGORY_LABELS: Record<string, string> = {
  BUG: 'Bug',
  SUGGESTION: 'Suggestion',
  QUESTION: 'Question',
  KUDOS: 'Bravo !',
};

export function FeedbackModal({ open, onClose }: FeedbackModalProps) {
  const { user } = useAuth();
  const [submitted, setSubmitted] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    handleSubmit,
    setValue,
    watch,
    register,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FeedbackFormData>({
    resolver: zodResolver(feedbackSchema),
  });

  const category = watch('category');

  const onSubmit = handleSubmit(async (data) => {
    setServerError(null);
    try {
      await feedbackRepository.create({
        category: data.category,
        message: data.message,
      });
      // Non-blocking: feedback already saved to DB
      emailjs
        .send(
          EMAILJS_SERVICE_ID,
          EMAILJS_TEMPLATE_ID,
          {
            from_name:
              [user?.profile?.first_name, user?.profile?.last_name]
                .filter(Boolean)
                .join(' ') || 'Unknown',
            name:
              [user?.profile?.first_name, user?.profile?.last_name]
                .filter(Boolean)
                .join(' ') || 'Unknown',
            reply_to: user?.email ?? 'unknown',
            category: data.category,
            message: data.message,
            page_url: window.location.href,
          },
          EMAILJS_PUBLIC_KEY,
        )
        .catch(() => {});
      setSubmitted(true);
    } catch {
      setServerError("Erreur lors de l'envoi. Reessayez.");
    }
  });

  const handleClose = () => {
    reset();
    setSubmitted(false);
    setServerError(null);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Envoyer un feedback</DialogTitle>
          <DialogDescription>
            Aidez-nous a ameliorer {SITE.name} en partageant votre retour.
          </DialogDescription>
        </DialogHeader>

        {submitted ? (
          <div className="space-y-4 py-4">
            <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-800">
              Merci pour votre feedback ! Nous le prendrons en compte.
            </div>
            <DialogFooter>
              <Button onClick={handleClose}>Fermer</Button>
            </DialogFooter>
          </div>
        ) : (
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="fb-category">Categorie</Label>
              <Select
                value={category}
                onValueChange={(val) =>
                  setValue('category', val as FeedbackFormData['category'], {
                    shouldValidate: true,
                  })
                }
              >
                <SelectTrigger id="fb-category">
                  <SelectValue placeholder="Choisir une categorie" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.category && (
                <p className="text-sm text-destructive">
                  {errors.category.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="fb-message">Message</Label>
              <Textarea
                id="fb-message"
                rows={5}
                placeholder="Decrivez votre retour (min. 10 caracteres)..."
                {...register('message')}
              />
              {errors.message && (
                <p className="text-sm text-destructive">
                  {errors.message.message}
                </p>
              )}
            </div>

            {user?.email && (
              <div className="space-y-1">
                <Label className="text-muted-foreground text-xs">Email</Label>
                <p className="text-sm text-muted-foreground">{user.email}</p>
              </div>
            )}

            {serverError && (
              <div className="rounded-lg border border-destructive bg-destructive/10 p-3 text-sm text-destructive">
                {serverError}
              </div>
            )}

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={isSubmitting}
              >
                Annuler
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Envoi...' : 'Envoyer'}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
