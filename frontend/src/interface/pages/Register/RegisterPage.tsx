import { Link, useNavigate } from 'react-router-dom';
import RegisterForm from '../../components/register/RegisterForm';
import { useEffect } from 'react';
import { useAuth } from '../../../app/providers/AuthProvider';
import Navbar from '../../components/navbar/Navbar';
import styles from './RegisterPage.module.css';

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
      <Navbar />
      <main className={styles.registerPage} data-component="RegisterPage">
        <section className={styles.card} aria-labelledby="register-title">
          <h1 id="register-title" className={styles.title}>
            Créer un compte
          </h1>

          {/* (Optionnel) Sous-titre d'accroche */}
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
