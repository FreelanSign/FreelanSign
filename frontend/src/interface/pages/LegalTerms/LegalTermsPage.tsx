import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { LegalTermsPreviewDto } from '../../../domain/legal-terms/types';
import { legalTermsRepository } from '../../../infrastructure/legal-terms/legalTermsRepository';
import { useRequireAccount } from '../../hooks/useRequireAccount';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  FileText,
  Info,
  ShieldCheck,
  UserCircle2,
} from 'lucide-react';

export default function LegalTermsPage() {
  const [preview, setPreview] = useState<LegalTermsPreviewDto | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useRequireAccount({ loading });

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        const data = await legalTermsRepository.getPreview();
        if (!mounted) return;
        setPreview(data);
      } catch (err: unknown) {
        console.error('Error loading legal terms preview', err);
        if (!mounted) return;

        const errorMsg =
          err && typeof err === 'object' && 'response' in err
            ? 'Données légales manquantes (SIRET, téléphone, etc.). Complétez votre profil.'
            : 'Erreur lors du chargement des conditions générales.';
        setError(errorMsg);
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => {
      mounted = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto max-w-5xl py-8 space-y-8 animate-in fade-in duration-500">
        <div className="space-y-4">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-4 w-96 opacity-60" />
        </div>
        <div className="grid gap-6">
          <Skeleton className="h-24 w-full rounded-2xl" />
          <Skeleton className="h-64 w-full rounded-2xl" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto max-w-xl py-20 flex flex-col items-center justify-center animate-in zoom-in-95 duration-500">
        <div className="h-20 w-20 rounded-full bg-destructive/10 flex items-center justify-center mb-6">
          <AlertCircle className="h-10 w-10 text-destructive" />
        </div>
        <h2 className="text-2xl font-bold font-playfair mb-3">
          Oups ! Action requise
        </h2>
        <p className="text-center text-muted-foreground mb-8 text-balance">
          {error}
        </p>
        <Button
          size="lg"
          onClick={() => navigate('/profile/edit')}
          className="bg-brand hover:bg-brand-dark shadow-lg shadow-brand/20 rounded-xl px-8"
        >
          <UserCircle2 className="mr-2 h-5 w-5" />
          Compléter mon profil
        </Button>
      </div>
    );
  }

  if (!preview) {
    return (
      <div className="container mx-auto max-w-xl py-20 flex flex-col items-center justify-center animate-in fade-in duration-500">
        <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center mb-6">
          <FileText className="h-10 w-10 text-muted-foreground" />
        </div>
        <p className="text-muted-foreground font-medium">
          Aucune condition générale disponible pour le moment.
        </p>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-5xl py-8 space-y-10 animate-in fade-in duration-700">
      {/* Dynamic HeaderSection */}
      <section className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-2 border-b border-gray-100">
        <div className="space-y-2">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-gray-900 font-playfair">
            Conditions Générales de Vente
          </h1>
          <p className="text-muted-foreground text-sm flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-brand" />
            Vérifiez l'aperçu dynamique de vos conditions légales
          </p>
        </div>
        <Badge
          variant="outline"
          className="w-fit h-7 border-brand/20 bg-brand/5 text-brand font-semibold px-3 rounded-full"
        >
          Version {preview.template_version}
        </Badge>
      </section>

      {/* Information Banner Card */}
      <div className="group relative overflow-hidden rounded-2xl bg-white border border-gray-100 p-6 shadow-sm transition-all hover:shadow-md">
        <div className="absolute top-0 right-0 w-32 h-32 bg-brand/5 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-110" />
        <div className="relative flex items-start gap-5">
          <div className="h-12 w-12 rounded-xl bg-brand/10 flex items-center justify-center shrink-0">
            <CheckCircle2 className="h-6 w-6 text-brand" />
          </div>
          <div className="space-y-1.5 pt-1">
            <h3 className="font-semibold text-gray-900">
              Automatisation Intelligente
            </h3>
            <p className="text-sm text-gray-600 leading-relaxed max-w-2xl">
              Ces CGV sont automatiquement générées et attachées à chacun de vos
              devis. Les variables (SIRET, coordonnées, etc.) sont extraites en
              temps réel de votre profil professionnel.
            </p>
          </div>
        </div>
      </div>

      {/* Tabs Layout */}
      <Tabs defaultValue="overview" className="space-y-8">
        <div className="flex items-center justify-between border-b border-gray-100 pb-0.5">
          <TabsList className="bg-transparent h-auto p-0 gap-8">
            <TabsTrigger
              value="overview"
              className="px-0 py-3 text-sm font-bold uppercase tracking-widest text-muted-foreground data-[state=active]:bg-transparent data-[state=active]:text-brand data-[state=active]:shadow-none border-b-2 border-transparent data-[state=active]:border-brand rounded-none transition-all"
            >
              Aperçu Complet
            </TabsTrigger>
            <TabsTrigger
              value="clauses"
              className="px-0 py-3 text-sm font-bold uppercase tracking-widest text-muted-foreground data-[state=active]:bg-transparent data-[state=active]:text-brand data-[state=active]:shadow-none border-b-2 border-transparent data-[state=active]:border-brand rounded-none transition-all"
            >
              Détail des Clauses ({preview.clauses.length})
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent
          value="overview"
          className="mt-0 focus-visible:outline-none focus-visible:ring-0"
        >
          <Card className="border-gray-100 shadow-xl shadow-gray-200/50 rounded-2xl overflow-hidden">
            <CardHeader className="bg-gray-50/50 border-b border-gray-100 px-8 py-6">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-lg bg-white border border-gray-200 flex items-center justify-center shadow-sm">
                  <FileText className="h-4 w-4 text-gray-500" />
                </div>
                <div>
                  <CardTitle className="text-lg font-bold">
                    Document Final
                  </CardTitle>
                  <CardDescription>
                    Ceci est le texte tel qu'il apparaîtra sur vos devis PDF
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="px-8 py-10">
              <div
                className="rich-text max-w-none"
                dangerouslySetInnerHTML={{ __html: preview.rendered_html }}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent
          value="clauses"
          className="mt-0 focus-visible:outline-none focus-visible:ring-0"
        >
          <div className="grid gap-6">
            {preview.clauses.map((clause, idx) => (
              <div
                key={clause.identifier}
                className="flex flex-col md:flex-row gap-6 group"
              >
                <div className="md:w-48 pt-2 flex items-center md:justify-end gap-2 text-muted-foreground shrink-0">
                  <span className="text-[10px] font-bold uppercase tracking-widest">
                    Clause {idx + 1}
                  </span>
                  <ChevronRight className="h-3 w-3 hidden md:block opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                </div>

                <Card className="flex-1 border-gray-100 shadow-sm rounded-xl transition-all hover:shadow-md hover:border-gray-200">
                  <CardHeader className="pb-3 border-b border-gray-50/50">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <CardTitle className="text-base font-bold text-gray-900">
                        {clause.title}
                      </CardTitle>
                      <div className="flex gap-2">
                        {clause.is_mandatory && (
                          <Badge
                            variant="outline"
                            className="h-5 text-[9px] font-bold uppercase tracking-tighter border-destructive/20 bg-destructive/5 text-destructive pr-2.5"
                          >
                            <AlertTriangle className="mr-1 h-2.5 w-2.5" />
                            Obligatoire
                          </Badge>
                        )}
                        {clause.was_customized && (
                          <Badge
                            variant="outline"
                            className="h-5 text-[9px] font-bold uppercase tracking-tighter border-accent-orange/20 bg-accent-orange/5 text-accent-orange pr-2.5"
                          >
                            <Info className="mr-1 h-2.5 w-2.5" />
                            Personnalisée
                          </Badge>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-5">
                    <div
                      className="rich-text"
                      dangerouslySetInnerHTML={{ __html: clause.body }}
                    />
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Footer Disclaimer */}
      <footer className="pt-10 flex items-center gap-4 text-xs text-muted-foreground border-t border-gray-100">
        <ShieldCheck className="h-4 w-4 shrink-0" />
        <p>
          En utilisant FreelanSign, vous reconnaissez que ces conditions
          générales sont fournies à titre indicatif. Nous vous recommandons de
          les faire valider par un conseil juridique selon votre activité
          spécifique.
        </p>
      </footer>
    </div>
  );
}
