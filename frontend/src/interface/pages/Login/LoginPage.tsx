import { useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';
import Navbar from '../../../interface/components/navbar/Navbar';
import { SITE } from '../../../lib/constants/site.config';
import LoginForm from '../../components/login/LoginForm';
import styles from './LoginPage.module.css';

export default function LoginPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate('/dashboard', { replace: true });
  }, [user, navigate]);

  return (
    <>
      <Helmet>
        <title>Connexion — {SITE.name}</title>
        <meta name="description" content={`Connexion à ${SITE.name}`} />
      </Helmet>
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
          <p className={styles.help}>
            <a href="/auth/request-password-reset" className={styles.link}>
              Mot de passe oublié ?
            </a>
          </p>
        </section>
      </main>
    </>
  );
}
