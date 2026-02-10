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
        <div className={styles.heroSection}>
          <h2 className={styles.heroTitle}>
            Vos <span className="text-accent-orange">devis professionnels</span>{' '}
            en quelques <span className="text-brand">minutes</span>.
          </h2>
          <p className={styles.heroSubtitle}>
            FreelanSign simplifie votre administratif : créez, personnalisez et
            envoyez vos devis conformes à la réglementation française.
          </p>
        </div>

        <section className={styles.card}>
          <h1 className={styles.title}>Connexion</h1>
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
