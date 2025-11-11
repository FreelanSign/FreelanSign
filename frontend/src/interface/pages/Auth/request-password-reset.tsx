// frontend/src/interface/pages/Auth/request-password-reset.tsx
import RequestPasswordResetForm from '../../components/auth/RequestPasswordResetForm';
import styles from './request-password-reset.module.css';

export default function RequestPasswordResetPage() {
  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h1 className={styles.title}>Réinitialiser le mot de passe</h1>
          <p className={styles.meta}>Recevez un lien sécurisé par email</p>
        </div>
        <div className={styles.card}>
          <RequestPasswordResetForm />
        </div>
      </div>
    </main>
  );
}
