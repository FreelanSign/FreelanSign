// src/interface/pages/Branding/ThemesListPage.tsx
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  Clock,
  Edit2,
  Layout,
  MoreVertical,
  Palette,
  Plus,
  Power,
  Trash2,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { isAccountMissingError } from '@/domain/account/utils';
import type { ThemeListItem } from '../../../infrastructure/branding/themeRepository';
import { themeRepository } from '../../../infrastructure/branding/themeRepository';
import { useThemes } from '../../hooks/useThemes';

/** Helpers type-safe pour récupérer un message d'erreur without any */
function isErrorWithMessage(e: unknown): e is { message: string } {
  return (
    typeof e === 'object' &&
    e !== null &&
    'message' in e &&
    typeof (e as Record<string, unknown>).message === 'string'
  );
}

function getErrorMessage(
  e: unknown,
  fallback = 'Une erreur est survenue',
): string {
  if (isErrorWithMessage(e)) return e.message;
  if (typeof e === 'string') return e;
  return fallback;
}

export default function ThemesListPage() {
  const { themes, loading, error } = useThemes();
  const navigate = useNavigate();

  // état local pour pouvoir refléter l’activation sans recharger
  const [list, setList] = useState<ThemeListItem[]>([]);
  const [activatingId, setActivatingId] = useState<string | number | null>(
    null,
  );
  const [actError, setActError] = useState<string | null>(null);
  const [deactivatingId, setDeactivatingId] = useState<string | number | null>(
    null,
  );

  useEffect(() => {
    setList(themes);
  }, [themes]);

  async function handleActivate(id: string | number) {
    try {
      setActError(null);
      setActivatingId(id);
      const activated = await themeRepository.activate(String(id));
      setList((prev) =>
        prev.map((t) => ({
          ...t,
          is_active: String(t.id) === String(activated.id),
        })),
      );
    } catch (e: unknown) {
      console.error(e);
      setActError(getErrorMessage(e, 'Activation impossible'));
    } finally {
      setActivatingId(null);
    }
  }

  async function handleDeactivate(id: string | number) {
    try {
      setDeactivatingId(id);
      const deactivated = await themeRepository.deactivate(String(id));
      setList((prev) =>
        prev.map((t) =>
          String(t.id) === String(deactivated.id)
            ? { ...t, is_active: deactivated.is_active }
            : t,
        ),
      );
    } catch (e: unknown) {
      console.error(e);
    } finally {
      setDeactivatingId(null);
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto max-w-7xl py-8 space-y-8 animate-in fade-in duration-500">
        <div className="flex justify-between items-end">
          <div className="space-y-4">
            <Skeleton className="h-10 w-64" />
            <Skeleton className="h-4 w-96 opacity-60" />
          </div>
          <Skeleton className="h-10 w-40 rounded-xl" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-48 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    // Si erreur 403 (pas de compte pro), afficher CTA onboarding
    if (isAccountMissingError(error)) {
      return (
        <div className="container mx-auto max-w-xl py-20 flex flex-col items-center justify-center animate-in zoom-in-95 duration-500">
          <div className="h-20 w-20 rounded-full bg-brand/10 flex items-center justify-center mb-6">
            <Palette className="h-10 w-10 text-brand" />
          </div>
          <h2 className="text-2xl font-bold font-playfair mb-3 text-brand-dark">
            Créez votre compte professionnel
          </h2>
          <p className="text-center text-muted-foreground mb-8">
            Accédez à vos thèmes en complétant votre profil professionnel
          </p>
          <Button
            onClick={() => navigate('/onboarding-account')}
            className="rounded-xl px-8 bg-brand hover:bg-brand-dark text-white"
          >
            Créer mon compte
          </Button>
        </div>
      );
    }

    // Erreur générique
    const errorMessage =
      error instanceof Error
        ? error.message
        : (() => {
            const e = error as {
              response?: { data?: unknown };
              message?: string;
            };
            const server = e.response?.data;
            return server
              ? JSON.stringify(server)
              : (e.message ?? 'Impossible de charger vos templates.');
          })();

    return (
      <div className="container mx-auto max-w-xl py-20 flex flex-col items-center justify-center animate-in zoom-in-95 duration-500">
        <div className="h-20 w-20 rounded-full bg-destructive/10 flex items-center justify-center mb-6">
          <AlertCircle className="h-10 w-10 text-destructive" />
        </div>
        <h2 className="text-2xl font-bold font-playfair mb-3">
          Erreur de chargement
        </h2>
        <p className="text-center text-muted-foreground mb-8">{errorMessage}</p>
        <Button
          onClick={() => window.location.reload()}
          variant="outline"
          className="rounded-xl px-8"
        >
          Réessayer
        </Button>
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
              onClick={() => navigate('/dashboard')}
              className="h-8 w-8 -ml-2 rounded-full"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <span className="text-xs font-bold uppercase tracking-widest">
              Design System
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-gray-900 font-playfair">
            Templates de devis
          </h1>
          <p className="text-muted-foreground text-sm flex items-center gap-2">
            <Layout className="h-4 w-4 text-brand" />
            Personnalisez l’identité visuelle de vos documents PDF
          </p>
        </div>

        <Button
          asChild
          className="bg-brand hover:bg-brand-dark shadow-lg shadow-brand/20 rounded-xl h-11 px-6"
        >
          <Link to="/branding/themes/new/" className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Nouveau Template
          </Link>
        </Button>
      </section>

      {actError && (
        <div className="bg-destructive/10 border border-destructive/20 text-destructive text-sm p-4 rounded-xl flex items-center gap-3 animate-in slide-in-from-top-2">
          <AlertCircle className="h-5 w-5 shrink-0" />
          {actError}
        </div>
      )}

      {list.length === 0 ? (
        <div className="py-20 flex flex-col items-center justify-center bg-white border border-dashed border-gray-200 rounded-3xl">
          <div className="h-20 w-20 rounded-full bg-gray-50 flex items-center justify-center mb-6">
            <Palette className="h-10 w-10 text-gray-300" />
          </div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">
            Aucun template créé
          </h3>
          <p className="text-muted-foreground text-center max-w-md mb-8 px-6 text-balance">
            Commencez par créer un template pour définir vos couleurs, votre
            logo et la typographie de vos devis.
          </p>
          <Button
            asChild
            variant="outline"
            className="rounded-xl px-8 border-brand text-brand hover:bg-brand/5"
          >
            <Link to="/branding/themes/new/">Créer mon premier template</Link>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {list.map((t) => (
            <Card
              key={t.id}
              className={cn(
                'group relative overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-gray-200/50 rounded-2xl border-gray-100',
                t.is_active
                  ? 'ring-2 ring-brand ring-offset-4 ring-offset-gray-50/50'
                  : 'hover:border-gray-200',
              )}
            >
              {/* Preview Banner based on theme colors if available, otherwise brand */}
              <div
                className="h-24 w-full transition-all duration-500 group-hover:h-28"
                style={{
                  backgroundColor: t.colors?.primary || 'var(--brand)',
                  backgroundImage: `linear-gradient(135deg, ${t.colors?.primary || 'hsl(166, 100%, 39%)'} 0%, ${t.colors?.secondary || 'hsl(166, 100%, 25%)'} 100%)`,
                }}
              >
                <div className="absolute top-4 right-4">
                  {t.is_active ? (
                    <Badge className="bg-white/90 backdrop-blur-sm text-brand border-none font-bold py-1 px-3 shadow-sm rounded-full flex items-center gap-1.5">
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      Template Actif
                    </Badge>
                  ) : (
                    <Badge
                      variant="outline"
                      className="bg-black/10 backdrop-blur-sm text-white border-white/20 font-medium py-1 px-3 rounded-full"
                    >
                      Inactif
                    </Badge>
                  )}
                </div>
              </div>

              <CardHeader className="pt-6 pb-2">
                <div className="flex justify-between items-start gap-2">
                  <div className="space-y-1 min-w-0">
                    <CardTitle className="text-xl font-bold truncate group-hover:text-brand transition-colors">
                      {t.name}
                    </CardTitle>
                    <CardDescription className="flex items-center gap-1.5 text-xs">
                      <Clock className="h-3 w-3" />
                      Mis à jour le{' '}
                      {new Intl.DateTimeFormat('fr-FR', {
                        day: '2-digit',
                        month: 'long',
                        year: 'numeric',
                      }).format(new Date(t.updated_at))}
                    </CardDescription>
                  </div>

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 rounded-full hover:bg-gray-100"
                      >
                        <MoreVertical className="h-4 w-4 text-gray-400" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent
                      align="end"
                      className="w-52 p-2 rounded-xl shadow-xl border-gray-100 animate-in fade-in zoom-in-95 duration-100"
                    >
                      <DropdownMenuItem
                        asChild
                        className="cursor-pointer rounded-lg focus:bg-brand/5 focus:text-brand py-2.5"
                      >
                        <Link
                          to={`/branding/themes/${t.id}/edit`}
                          className="flex items-center gap-3"
                        >
                          <Edit2 className="h-4 w-4" />
                          <span className="font-semibold">Modifier</span>
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator className="my-2 bg-gray-50" />
                      {t.is_active ? (
                        <DropdownMenuItem
                          onClick={() => handleDeactivate(t.id)}
                          disabled={deactivatingId === t.id}
                          className="cursor-pointer rounded-lg focus:bg-destructive/5 focus:text-destructive py-2.5 text-destructive"
                        >
                          <Power className="mr-3 h-4 w-4" />
                          <span className="font-semibold">
                            {deactivatingId === t.id
                              ? 'Désactivation...'
                              : 'Désactiver'}
                          </span>
                        </DropdownMenuItem>
                      ) : (
                        <DropdownMenuItem
                          onClick={() => handleActivate(t.id)}
                          disabled={activatingId === t.id}
                          className="cursor-pointer rounded-lg focus:bg-brand/5 focus:text-brand py-2.5 text-brand"
                        >
                          <CheckCircle2 className="mr-3 h-4 w-4" />
                          <span className="font-semibold">
                            {activatingId === t.id
                              ? 'Activation...'
                              : 'Activer'}
                          </span>
                        </DropdownMenuItem>
                      )}
                      {/* Placeholder for Delete if needed later */}
                      <DropdownMenuSeparator className="my-2 bg-gray-50" />
                      <DropdownMenuItem className="rounded-lg focus:bg-destructive/5 focus:text-destructive py-2.5 text-gray-400 opacity-50 cursor-not-allowed">
                        <Trash2 className="mr-3 h-4 w-4" />
                        <span className="font-semibold">Supprimer</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>

              <CardContent className="pt-2 pb-6">
                <div className="flex items-center gap-4">
                  <div className="flex -space-x-2">
                    {/* Visual indicators of colors */}
                    {Object.values(t.colors as object)
                      .slice(0, 4)
                      .map((c, i) => (
                        <div
                          key={i}
                          className="h-6 w-6 rounded-full border-2 border-white shadow-sm ring-1 ring-gray-100"
                          style={{ backgroundColor: c as string }}
                        />
                      ))}
                  </div>
                  <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                    Palette de couleurs
                  </span>
                </div>

                <div className="mt-8">
                  {!t.is_active ? (
                    <Button
                      onClick={() => handleActivate(t.id)}
                      disabled={activatingId === t.id}
                      variant="outline"
                      className="w-full rounded-xl border-gray-200 hover:bg-brand hover:text-white hover:border-brand transition-all duration-300 font-bold text-xs uppercase tracking-widest"
                    >
                      {activatingId === t.id
                        ? 'Initialisation...'
                        : 'Activer ce template'}
                    </Button>
                  ) : (
                    <div className="flex items-center justify-center gap-2 py-2 px-4 bg-brand/5 rounded-xl border border-brand/10">
                      <CheckCircle2 className="h-4 w-4 text-brand" />
                      <span className="text-[11px] font-bold text-brand uppercase tracking-tighter">
                        Utilisé par défaut
                      </span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Footer Info */}
      <footer className="pt-10 flex items-center gap-4 text-xs text-muted-foreground border-t border-gray-100">
        <Palette className="h-4 w-4 shrink-0" />
        <p>
          Un template actif s'applique immédiatement à l'ensemble de vos
          documents PDF générés. Vous pouvez créer plusieurs templates pour
          tester différents styles.
        </p>
      </footer>
    </div>
  );
}
