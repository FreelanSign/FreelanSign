import { useState } from 'react';
import toast from 'react-hot-toast';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { authRepository } from '../../../infrastructure/auth/authRepository';

export function VerificationBanner() {
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleResend() {
    setSending(true);
    try {
      await authRepository.resendVerification();
      setSent(true);
      toast.success('Email de vérification envoyé !');
    } catch {
      toast.error("Impossible d'envoyer l'email. Réessayez plus tard.");
    } finally {
      setSending(false);
    }
  }

  return (
    <Alert className="rounded-none border-x-0 border-t-0 border-amber-300 bg-amber-50 text-amber-800">
      <AlertDescription className="flex items-center justify-between gap-4">
        <span>
          Votre adresse email n&apos;est pas encore vérifiée. Vérifiez votre
          boîte de réception.
        </span>
        {!sent && (
          <button
            onClick={handleResend}
            disabled={sending}
            className="shrink-0 text-sm font-medium underline underline-offset-2 hover:text-amber-900 disabled:opacity-50"
          >
            {sending ? 'Envoi…' : "Renvoyer l'email"}
          </button>
        )}
      </AlertDescription>
    </Alert>
  );
}
