// frontend/app/pages/auth/reset-password.tsx

import { useSearchParams } from 'react-router-dom';
import ResetPasswordForm from '../../components/auth/ResetPasswordForm';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  if (!token) {
    return <p className="text-red-600">Lien invalide ou expiré.</p>;
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-[var(--paper)] px-4">
      <div className="max-w-md w-full bg-white p-6 rounded-2xl shadow-md">
        <h1 className="text-xl font-semibold text-[var(--brand)] mb-4">
          Définir un nouveau mot de passe
        </h1>
        <ResetPasswordForm token={token} />
      </div>
    </main>
  );
}
