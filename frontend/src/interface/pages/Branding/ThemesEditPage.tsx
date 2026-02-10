// pages/branding/ThemeEditPage.tsx
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { ArrowLeft, Palette, Settings2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { themeRepository } from '../../../infrastructure/branding/themeRepository';
import ThemeForm, {
  type ThemeFormData,
} from '../../components/branding/ThemesForm';
import { normalizeSpacing, normalizeTypography } from '../../utils/branding';

export default function ThemeEditPage() {
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(false);
  const [loadingTheme, setLoadingTheme] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [initialData, setInitialData] = useState<ThemeFormData | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadTheme() {
      if (!id) {
        setError('ID du thème manquant');
        setLoadingTheme(false);
        return;
      }

      try {
        setLoadingTheme(true);
        const theme = await themeRepository.get(id);

        setInitialData({
          name: theme.name,
          isActive: theme.is_active,
          colors: theme.colors,
          typography: normalizeTypography(theme.typography),
          spacing: normalizeSpacing(theme.spacing),
          logo: null,
        });
      } catch (err: unknown) {
        const error = err as { message?: string };
        setError(error.message || 'Erreur lors du chargement du thème');
      } finally {
        setLoadingTheme(false);
      }
    }

    loadTheme();
  }, [id]);

  async function handleSubmit(data: ThemeFormData) {
    if (!id) {
      setError('ID du thème manquant');
      return;
    }

    if (!data.name.trim()) {
      setError('Le nom du thème est requis');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await themeRepository.update(id, {
        name: data.name,
        is_active: data.isActive,
        colors: data.colors,
        typography: normalizeTypography(data.typography),
        spacing: normalizeSpacing(data.spacing),
        ...(data.logo ? { logo: data.logo } : {}),
      });
      navigate('/branding/themes');
    } catch (err: unknown) {
      const error = err as { message?: string };
      setError(error.message || 'Erreur lors de la mise à jour du thème');
    } finally {
      setLoading(false);
    }
  }

  if (loadingTheme) {
    return (
      <div className="container mx-auto max-w-7xl py-8 space-y-10 animate-in fade-in duration-500">
        <div className="space-y-4">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-4 w-96 opacity-60" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-8 space-y-8">
            <Skeleton className="h-[400px] w-full rounded-3xl" />
          </div>
          <div className="lg:col-span-4">
            <Skeleton className="h-[400px] w-full rounded-3xl" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-7xl py-8 space-y-10 animate-in fade-in duration-700">
      {/* Header Section */}
      <section className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-2 border-b border-gray-100">
        <div className="space-y-2">
          <div className="flex items-center gap-3 text-muted-foreground mb-1">
            <Button
              variant="ghost"
              size="icon"
              asChild
              className="h-8 w-8 -ml-2 rounded-full"
            >
              <Link to="/branding/themes">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <span className="text-xs font-bold uppercase tracking-widest">
              Configuration visuelle
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-gray-900 font-playfair flex items-center gap-3">
            Modifier le template
            <Settings2 className="h-6 w-6 text-brand/40" />
          </h1>
          <p className="text-muted-foreground text-sm flex items-center gap-2">
            <Palette className="h-4 w-4 text-brand" />
            Personnalisez les réglages de votre thème existant :{' '}
            <span className="font-bold text-gray-900">{initialData?.name}</span>
          </p>
        </div>
      </section>

      {error && !initialData && (
        <Card className="border-destructive/20 bg-destructive/5 rounded-2xl">
          <CardContent className="pt-6">
            <p className="text-destructive font-bold">{error}</p>
            <Button asChild variant="outline" className="mt-4 rounded-xl">
              <Link to="/branding/themes">Retourner à la liste</Link>
            </Button>
          </CardContent>
        </Card>
      )}

      {initialData && (
        <ThemeForm
          initialData={initialData}
          onSubmit={handleSubmit}
          submitLabel="Enregistrer les modifications"
          isLoading={loading}
          error={error}
        />
      )}
    </div>
  );
}
