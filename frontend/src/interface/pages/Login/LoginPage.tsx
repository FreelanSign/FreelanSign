import { Link, useNavigate } from 'react-router-dom';
import LoginForm from '../../components/login/LoginForm';
import Navbar from '../../../interface/components/navbar/Navbar';
import { useEffect } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import styles from './LoginPage.module.css';
import { Helmet } from 'react-helmet-async';
import { SITE } from '../../../lib/constants/site.config';

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
        </section>
      </main>
    </>
  );
}
