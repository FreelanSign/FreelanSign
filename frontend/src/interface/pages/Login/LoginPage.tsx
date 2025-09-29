import { Link, useNavigate } from 'react-router-dom';
import LoginForm from '../../components/login/LoginForm';
import Navbar from '../../../interface/components/navbar/Navbar';
import { useEffect } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import styles from './LoginPage.module.css';

export default function LoginPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate('/dashboard', { replace: true });
  }, [user, navigate]);

  return (
    <>
      <Navbar />
      <main className={styles.loginPage} data-component="LoginPage">
        <section className={styles.card}>
          <h1 className={styles.title}>Connexion</h1>

          {/* LoginForm reste séparé et peut avoir son propre LoginForm.module.css */}
          <LoginForm />

          <p className={styles.cta}>
            Pas encore de compte ?{' '}
            <Link to="/register" className={styles.link}>
              Créer un compte
            </Link>
          </p>
        </section>
      </main>
    </>
  );
}
