import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { DashboardLatestQuotesTable } from '@/interface/components/quote/LatestQuotesTable';
import {
  Briefcase,
  CheckCircle,
  Euro,
  FileText,
  List,
  User,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider';
import { mapMetricsToUi } from '../../application/quote/metricsMapper';
import type { QuoteMetricsUi } from '../../domain/quote/metricsTypes';
import { useAccountStore } from '../../infrastructure/account/accountStore';
import { quoteRepository } from '../../infrastructure/quote/quoteRepository';
import { MetricCard } from '../components/dashboard/MetricCard';
import { MonthlyQuoteCountChart } from '../components/dashboard/MonthlyQuoteCountChart';
import { MonthlyRevenueChart } from '../components/dashboard/MonthlyRevenueChart';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const activeAccountId = useAccountStore((state) => state.activeAccountId);
  const [metrics, setMetrics] = useState<QuoteMetricsUi | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      if (!activeAccountId) {
        setLoading(false);
        return;
      }
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

  const welcomeName =
    user?.profile?.first_name || user?.email?.split('@')[0] || 'Aventurier';

  return (
    <div className="container mx-auto py-8 px-4 space-y-8 max-w-7xl animate-in fade-in duration-500">
      {/* Header Row */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-border/60">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight font-playfair">
            Tableau de bord
          </h1>
          <p className="text-muted-foreground">
            Ravi de vous revoir,{' '}
            <span className="text-brand font-semibold">{welcomeName}</span> 👋
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/profile')}
            className="h-9 px-4"
          >
            <User className="mr-2 h-4 w-4" />
            Profil
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/quotes')}
            className="h-9 px-4"
          >
            <List className="mr-2 h-4 w-4" />
            Mes devis
          </Button>
          {/* <Button
            size="sm"
            onClick={() => navigate('/quotes/new')}
            className="bg-brand text-white hover:bg-brand-dark h-9 px-4 shadow-sm"
          >
            <Plus className="mr-2 h-4 w-4" />
            Créer un devis
          </Button> */}
        </div>
      </div>

      {activeAccountId === null && !loading && (
        <Card className="border-brand/20 bg-brand/5 shadow-none overflow-hidden relative">
          <div className="absolute top-0 right-0 p-8 opacity-5">
            <Briefcase size={120} />
          </div>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-brand-dark">
              Commencez votre aventure freelance
            </CardTitle>
            <CardDescription className="text-muted-foreground/80 max-w-2xl">
              Créez votre compte professionnel en quelques minutes pour
              commencer à générer vos devis et factures professionnels.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              onClick={() => navigate('/onboarding-account')}
              className="bg-brand text-white hover:bg-brand-dark shadow-md"
            >
              Créer mon compte professionnel
            </Button>
            <p className="text-xs text-muted-foreground italic">
              * Vous pourrez modifier ces informations à tout moment depuis
              votre profil.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Métriques */}
      {activeAccountId && (
        <div className="space-y-8">
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-32 w-full rounded-xl" />
              ))}
            </div>
          ) : error ? (
            <div className="p-4 rounded-lg bg-destructive/10 text-destructive text-sm border border-destructive/20">
              {error}
            </div>
          ) : metrics ? (
            <>
              {/* Cartes métriques */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricCard
                  title="Devis émis"
                  value={metrics.totalQuotes}
                  icon={<FileText className="h-5 w-5" />}
                  subtitle="Volume total d'activité"
                />
                <MetricCard
                  title="CA estimé"
                  value={`${metrics.estimatedRevenue.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} €`}
                  icon={<Euro className="h-5 w-5" />}
                  subtitle="Sur la base des devis acceptés"
                />
                <MetricCard
                  title="Taux d'acceptation"
                  value={`${metrics.acceptanceRate.toFixed(1)}%`}
                  icon={<CheckCircle className="h-5 w-5" />}
                  subtitle="Ratio devis acceptés / envoyés"
                />
              </div>

              {/* Graphiques */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <MonthlyRevenueChart data={metrics.monthlyBreakdown} />
                <MonthlyQuoteCountChart data={metrics.monthlyBreakdown} />
              </div>
            </>
          ) : null}
        </div>
      )}

      {/* Latest Activity */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h3 className="text-lg font-semibold tracking-tight font-playfair">
              Derniers devis
            </h3>
            <p className="text-xs text-muted-foreground">
              Vos 5 activités les plus récentes
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/quotes')}
            className="h-8 text-xs font-bold uppercase tracking-wider"
          >
            Tout voir
          </Button>
        </div>

        <Card className="shadow-none border border-border overflow-hidden bg-white">
          <CardContent className="p-0">
            <DashboardLatestQuotesTable pageSize={5} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
