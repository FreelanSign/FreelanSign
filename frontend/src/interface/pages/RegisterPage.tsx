import { Link, useNavigate } from 'react-router-dom';
import RegisterForm from '@/interface/components/forms/RegisterForm';
import { useEffect } from 'react';
import { useAuth } from '@/app/providers/AuthProvider';

export default function RegisterPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate('/dashboard', { replace: true });
  }, [user, navigate]);

  return (
    <main className="container mx-auto p-6 grid gap-6">
      <h1 className="text-2xl font-semibold">Créer un compte</h1>
      <RegisterForm />
      <p>
        Déjà inscrit ?{' '}
        <Link to="/login" className="underline">Se connecter</Link>
      </p>
    </main>
  );
}
