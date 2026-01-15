import { Link, useNavigate } from 'react-router-dom';
import RegisterForm from '../../components/register/RegisterForm';
import { useEffect } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import Navbar from '../../components/navbar/Navbar';
import styles from './RegisterPage.module.css';
import { Helmet } from 'react-helmet-async';
import { SITE } from '../../../lib/constants/site.config';

export default function RegisterPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate('/dashboard', { replace: true });
    // Petit plus SEO/accessibilité
    document.title = 'Créer un compte — FreelanSign';
  }, [user, navigate]);

  return (
    <>
      <Helmet>
        <title>Créer un compte — {SITE.name}</title>
        <meta name="description" content={`Créer un compte sur ${SITE.name}`} />
      </Helmet>
      <Navbar />
      <main className={styles.registerPage} data-component="RegisterPage">
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

        <section className={styles.card} aria-labelledby="register-title">
          <h1 id="register-title" className={styles.title}>
            Créer un compte
          </h1>
          <p className={styles.subtitle}>
            Rejoignez FreelanSign et gagnez du temps sur vos devis & factures.
          </p>
          <RegisterForm />

          <p className={styles.cta}>
            Déjà inscrit ?{' '}
            <Link
              to="/login"
              className={`${styles.link} ${styles.linkInline}`}
              aria-label="Se connecter"
            >
              Se connecter
            </Link>
          </p>
        </section>
      </main>
    </>
  );
}
