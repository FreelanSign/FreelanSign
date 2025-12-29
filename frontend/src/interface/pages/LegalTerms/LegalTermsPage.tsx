import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { LegalTermsPreviewDto } from '../../../domain/legal-terms/types';
import { legalTermsRepository } from '../../../infrastructure/legal-terms/legalTermsRepository';
import { useRequireAccount } from '../../hooks/useRequireAccount';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

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
      <div className="grid gap-6">
        <Skeleton className="h-20 w-full rounded-lg" />
        <Skeleton className="h-32 w-full rounded-lg" />
        <Skeleton className="h-96 w-full rounded-lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Erreur</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">{error}</p>
            <Button onClick={() => navigate('/profile/edit')}>
              Compléter mon profil
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!preview) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <p className="text-muted-foreground">
          Aucune condition générale disponible.
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-6">
      <header className="flex items-start justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 font-playfair">
          Conditions Générales de Vente
        </h1>
        <Badge variant="secondary" className="text-xs">
          Version {preview.template_version}
        </Badge>
      </header>

      <div className="flex gap-3 p-4 rounded-lg bg-brand/10 border border-brand/20">
        <div className="w-6 h-6 rounded-full bg-brand text-brand-foreground flex items-center justify-center shrink-0">
          ✓
        </div>
        <div className="space-y-1">
          <p className="text-sm font-medium text-brand">
            Ces conditions sont automatiquement attachées à tous vos devis.
          </p>
          <p className="text-xs text-muted-foreground">
            Les variables (SIRET, adresse, etc.) sont substituées
            automatiquement.
          </p>
        </div>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Clauses ({preview.clauses.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {preview.clauses.map((clause) => (
              <Card key={clause.identifier} className="shadow-sm">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg">{clause.title}</CardTitle>
                    <div className="flex gap-2">
                      {clause.is_mandatory && (
                        <Badge className="bg-destructive/10 text-destructive">
                          Obligatoire
                        </Badge>
                      )}
                      {clause.was_customized && (
                        <Badge className="bg-accent-orange/10 text-accent-orange">
                          Personnalisée
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div
                    className="rich-text"
                    dangerouslySetInnerHTML={{ __html: clause.body }}
                  />
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Aperçu complet</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className="rich-text"
            dangerouslySetInnerHTML={{ __html: preview.rendered_html }}
          />
        </CardContent>
      </Card>
    </div>
  );
}
