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
  }, [user, navigate]);

  return (
    <>
      <Navbar />
      <main className={styles.registerPage} data-component="RegisterPage">
        <section className={styles.card}>
          <h1 className={styles.title}>Créer un compte</h1>
          <RegisterForm />
          <p className={styles.cta}>
            Déjà inscrit ?{' '}
            <Link to="/login" className={styles.link}>
              Se connecter
            </Link>
          </p>
        </section>
      </main>
    </>
  );
}
