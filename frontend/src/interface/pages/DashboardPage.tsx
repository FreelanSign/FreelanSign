import { Link } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider';
import QuotesTable from '../components/quote/QuotesTable';
import styles from './dashboard.module.css';

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="grid gap-6">
      <div className={styles.headerRow}>
        <h1 className={styles.title}>Dashboard</h1>
        <div className={styles.headerCta}>
          <Link to="/profile" className={`${styles.btn} ${styles.btnPrimary}`}>
            Mon profil
          </Link>
          <Link to="/quotes" className={`${styles.btn} ${styles.btnIndigo}`}>
            Mes devis
          </Link>
          <Link
            to="/quotes/new"
            className={`${styles.btn} ${styles.btnSuccess}`}
          >
            + Créer un devis
          </Link>
        </div>
      </div>
      <p className={styles.welcome}>
        Bienvenue {user?.profile?.first_name ?? user?.email} 👋
      </p>
      <div className={styles.card}>
        <div className={styles.containerOverride}>
          <QuotesTable />
        </div>
        <div className={styles.cardMeta}>
          Affichage limité — tu peux ajuster le widget depuis le dashboard.
        </div>
      </div>
    </div>
  );
}
