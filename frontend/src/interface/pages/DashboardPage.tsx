import Sidebar from '../components/sidebar/Sidebar';
import Navbar from '../components/navbar/Navbar';
import { Link } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider';
import QuotesListPage from './Quote/QuoteListPage';
import styles from './dashboard.module.css'; // <-- nouveau

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div>
      <Sidebar />
      <div className={styles.page}>
        <Navbar />
        <main className={`${styles.inner} container mx-auto grid gap-6`}>
          <div className={styles.headerRow}>
            <h1 className={styles.title}>Dashboard</h1>
            <div className={styles.headerCta}>
              <Link
                to="/profile"
                className={`${styles.btn} ${styles.btnPrimary}`}
              >
                Mon profil
              </Link>
              <Link
                to="/quotes"
                className={`${styles.btn} ${styles.btnIndigo}`}
              >
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

          {/* Card qui emballe la liste des devis (applique le style "card") */}
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <h2 style={{ margin: 0, fontWeight: 600 }}>Derniers devis</h2>
              <Link to="/quotes" className="text-indigo-600 hover:underline">
                Voir tout
              </Link>
            </div>

            {/* si QuotesListPage rend toute la page, mieux l'encapsuler dans une zone */}
            <div className={styles.containerOverride}>
              <QuotesListPage />
            </div>

            <div className={styles.cardMeta}>
              Affichage limité — tu peux ajuster le widget depuis le dashboard.
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
