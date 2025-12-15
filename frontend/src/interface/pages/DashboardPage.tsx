import { DashboardLatestQuotesTable } from '@/interface/components/quote/LatestQuotesTable';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider';
import { mapMetricsToUi } from '../../application/quote/metricsMapper';
import type { QuoteMetricsUi } from '../../domain/quote/metricsTypes';
import { useAccountStore } from '../../infrastructure/account/accountStore';
import { quoteRepository } from '../../infrastructure/quote/quoteRepository';
import { MetricCard } from '../components/dashboard/MetricCard';
import { MonthlyQuoteCountChart } from '../components/dashboard/MonthlyQuoteCountChart';
import { MonthlyRevenueChart } from '../components/dashboard/MonthlyRevenueChart';
import styles from './dashboard.module.css';

export default function DashboardPage() {
  const { user } = useAuth();
  const activeAccountId = useAccountStore((state) => state.activeAccountId);
  const [metrics, setMetrics] = useState<QuoteMetricsUi | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      if (!activeAccountId) return;
      setLoading(true);
      setError(null);
      try {
        const data = await quoteRepository.getMetrics();
        if (!active) return;
        setMetrics(mapMetricsToUi(data));
      } catch (err) {
        console.error('Load metrics error', err);
        setError('Erreur de chargement des métriques');
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [activeAccountId]);

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
      {activeAccountId === null && (
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h2 className={styles.cardTitle}>
              Commencez votre aventure freelance
            </h2>
          </div>
          <p className={styles.cardDescription}>
            Créez votre compte professionnel en quelques minutes pour commencer
            à générer vos devis et factures.
          </p>
          <Link
            to="/onboarding-account"
            className={`${styles.btn} ${styles.btnAccent}`}
          >
            Créer mon compte
          </Link>
          <div className={styles.cardMeta}>
            Vous pourrez modifier ces informations à tout moment depuis votre
            profil.
          </div>
        </div>
      )}

      {/* Métriques */}
      {activeAccountId && (
        <>
          {loading ? (
            <div className="py-8 text-center text-gray-500">
              Chargement des métriques…
            </div>
          ) : error ? (
            <div className="text-sm text-red-600">{error}</div>
          ) : metrics ? (
            <>
              {/* Cartes métriques */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <MetricCard
                  title="Nombre total de devis"
                  value={metrics.totalQuotes}
                />
                <MetricCard
                  title="CA estimé"
                  value={`${metrics.estimatedRevenue.toFixed(2)} €`}
                />
                <MetricCard
                  title="Taux d'acceptation"
                  value={`${metrics.acceptanceRate.toFixed(1)}%`}
                  subtitle="Devis acceptés / envoyés"
                />
              </div>

              {/* Graphiques */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <MonthlyRevenueChart data={metrics.monthlyBreakdown} />
                <MonthlyQuoteCountChart data={metrics.monthlyBreakdown} />
              </div>
            </>
          ) : null}
        </>
      )}

      <div className={styles.card}>
        <div className={styles.containerOverride}>
          {/* AIDEV_NOTE : Quote latest table */}
          <DashboardLatestQuotesTable pageSize={5} />
        </div>
      </div>
    </div>
  );
}
