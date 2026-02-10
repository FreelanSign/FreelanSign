// interface/pages/Auth/VerifyEmailPage.tsx
import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { apiClient } from '../../../infrastructure/http/apiClient';
import Navbar from '../../components/navbar/Navbar';

type VerifyState = 'loading' | 'success' | 'error';

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [state, setState] = useState<VerifyState>('loading');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (!token) {
      setState('error');
      setErrorMsg('Token de verification manquant.');
      return;
    }

    apiClient
      .post('/api/auth/verify-email/', { token })
      .then(() => setState('success'))
      .catch((err) => {
        setState('error');
        const detail = err?.response?.data?.detail;
        setErrorMsg(
          typeof detail === 'string' ? detail : 'Token invalide ou expire.',
        );
      });
  }, [token]);

  return (
    <>
      <Navbar />
      <main className="flex min-h-[60vh] items-center justify-center p-6">
        <div className="mx-auto max-w-md text-center space-y-4">
          <h1 className="text-2xl font-bold">Verification de l'email</h1>

          {state === 'loading' && (
            <p className="text-muted-foreground">Verification en cours...</p>
          )}

          {state === 'success' && (
            <div className="space-y-3">
              <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-800">
                Votre adresse email a ete verifiee avec succes !
              </div>
              <Link
                to="/login"
                className="inline-block rounded-lg bg-brand px-6 py-2 text-sm font-semibold text-white hover:opacity-90 transition"
              >
                Se connecter
              </Link>
            </div>
          )}

          {state === 'error' && (
            <div className="space-y-3">
              <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-sm text-destructive">
                {errorMsg}
              </div>
              <Link
                to="/login"
                className="inline-block text-sm text-muted-foreground hover:underline"
              >
                Retour a la connexion
              </Link>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
