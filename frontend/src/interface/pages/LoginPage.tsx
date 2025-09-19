import { Link, useNavigate } from 'react-router-dom';
import LoginForm from '@/interface/components/forms/LoginForm';
import { useEffect } from 'react';
import { useAuth } from '@/app/providers/AuthProvider';

export default function LoginPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate('/dashboard', { replace: true });
  }, [user, navigate]);

  return (
    <main className="container mx-auto p-6 grid gap-6">
      <h1 className="text-2xl font-semibold">Connexion</h1>
      <LoginForm />
      <p>
        Pas encore de compte ?{' '}
        <Link to="/register" className="underline">
          Créer un compte
        </Link>
      </p>
    </main>
  );
}
