import { useEffect, useMemo, useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';
import QuoteEmailPreviewDialog from '../../components/email/QuoteEmailPreviewDialog';
import DeleteConfirmDialog from '../../components/common/DeleteConfirmDialog';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';

import { apiToUiQuoteDetail } from '../../../domain/quote/mappers';
import type {
  ApiQuoteResponse,
  UiQuoteDetail,
} from '../../../domain/quote/types';

function useIntlFormatters(currency: string | null | undefined) {
  const money = useMemo(
    () =>
      new Intl.NumberFormat(undefined, {
        style: 'currency',
        currency: currency ?? 'EUR',
        currencyDisplay: 'symbol',
        maximumFractionDigits: 2,
      }),
    [currency],
  );
  const date = useMemo(
    () =>
      new Intl.DateTimeFormat(undefined, {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
      }),
    [],
  );
  return { money, date };
}

export default function QuoteDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [quote, setQuote] = useState<UiQuoteDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [showEmailDialog, setShowEmailDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  async function handleDownload() {
    try {
      setDownloading(true);
      await quoteRepository.downloadPdf(id ?? '');
    } catch (err) {
      alert((err as Error).message || 'Erreur téléchargement PDF');
    } finally {
      setDownloading(false);
    }
  }

  async function handleDelete() {
    if (!id) return;
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await quoteRepository.delete(id);
      setShowDeleteDialog(false);
      navigate('/quotes');
    } catch (error: unknown) {
      const err = error as {
        response?: { data?: { detail?: string } };
        message?: string;
      };
      const errorMsg =
        err.response?.data?.detail ||
        err.message ||
        'Erreur lors de la suppression';
      setDeleteError(errorMsg);
    } finally {
      setIsDeleting(false);
    }
  }

  useEffect(() => {
    if (!id) return;
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const api: ApiQuoteResponse = await quoteRepository.retrieve(id);
        if (!active) return;
        const mapped = apiToUiQuoteDetail(api);
        setQuote(mapped);
      } catch (err) {
        const e = err as { response?: { data?: unknown }; message?: string };
        const server = e.response?.data;
        setError(server ? JSON.stringify(server) : (e.message ?? 'Erreur'));
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [id]);

  const { money, date } = useIntlFormatters(quote?.currency ?? 'EUR');

  const computed = useMemo(() => {
    if (!quote) return null;
    const lines = quote.line_items ?? [];
    const sub =
      quote.subtotal ??
      lines.reduce(
        (acc, l) => acc + (l.pre_tax_total ?? l.quantity * l.unit_price),
        0,
      );
    const taxes =
      quote.tax_total ??
      lines.reduce(
        (acc, l) =>
          acc +
          (l.tax_amount ??
            (l.pre_tax_total ?? l.quantity * l.unit_price) * (l.tax_rate ?? 0)),
        0,
      );
    const total = quote.total ?? sub + taxes - (quote.discount_total ?? 0);
    return { sub, taxes, total };
  }, [quote]);

  const Shell: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <div className="grid gap-6">{children}</div>
  );

  if (loading) {
    return (
      <Shell>
        <Skeleton className="h-32 w-full rounded-lg" />
        <Skeleton className="h-64 w-full rounded-lg" />
        <Skeleton className="h-96 w-full rounded-lg" />
      </Shell>
    );
  }

  if (error) {
    return (
      <Shell>
        <div className="text-destructive">Erreur : {error}</div>
        <Button variant="ghost" asChild>
          <Link to="/quotes">← Retour à la liste</Link>
        </Button>
      </Shell>
    );
  }

  if (!quote) {
    return (
      <Shell>
        <div>Aucun devis à afficher.</div>
        <Button variant="ghost" asChild>
          <Link to="/quotes">← Retour à la liste</Link>
        </Button>
      </Shell>
    );
  }

  const addressLines = (quote.client?.address || '')
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean);

  return (
    <Shell>
      <header className="flex items-start justify-between p-6 rounded-lg bg-gradient-to-r from-brand to-accent-orange text-white shadow-lg">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">
              {quote.reference} — {quote.title}
            </h1>
            <Badge className="bg-white/20 text-white border-white/30">
              {quote.status}
            </Badge>
          </div>
          <p className="text-sm text-white/90 mt-2">
            Émis le{' '}
            {quote.issue_date ? date.format(new Date(quote.issue_date)) : '—'}
            {quote.valid_until ? (
              <> • Valide jusqu'au {date.format(new Date(quote.valid_until))}</>
            ) : null}
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <Button
            variant="ghost"
            className="text-white hover:bg-white/20"
            asChild
          >
            <Link to="/quotes">← Retour</Link>
          </Button>
          <Button className="bg-white text-brand hover:bg-white/90" asChild>
            <Link to={`/quotes/${quote.id}/edit`}>Éditer</Link>
          </Button>
          <Button
            onClick={handleDownload}
            disabled={downloading}
            className="bg-white text-accent-orange hover:bg-white/90"
            title="Télécharger le devis (PDF)"
          >
            {downloading ? 'Téléchargement en cours...' : 'Télécharger (PDF)'}
          </Button>
          <Button
            className="bg-white text-brand hover:bg-white/90"
            onClick={() => setShowEmailDialog(true)}
          >
            Préparer email
          </Button>
        </div>
      </header>

      {/* Infos Client & Devis */}
      <Card className="shadow-sm">
        <CardContent className="pt-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h2 className="text-lg font-semibold mb-4 text-gray-900">
                Client
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Nom</span>
                  <strong className="text-gray-900">
                    {quote.client?.name || '—'}
                  </strong>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Email</span>
                  <strong className="text-gray-900">
                    {quote.client?.email ? (
                      <a
                        className="text-brand hover:underline"
                        href={`mailto:${quote.client.email}`}
                      >
                        {quote.client.email}
                      </a>
                    ) : (
                      '—'
                    )}
                  </strong>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Téléphone</span>
                  <strong className="text-gray-900">
                    {quote.client?.phone ? (
                      <a
                        className="text-brand hover:underline"
                        href={`tel:${quote.client.phone}`}
                      >
                        {quote.client.phone}
                      </a>
                    ) : (
                      '—'
                    )}
                  </strong>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">N° TVA</span>
                  <strong className="text-gray-900">
                    {quote.client?.vat_number || '—'}
                  </strong>
                </div>
                <address className="text-sm text-gray-900 not-italic">
                  {addressLines.length
                    ? addressLines.map((l, i) => <div key={i}>{l}</div>)
                    : '—'}
                </address>
              </div>
            </div>

            <div>
              <h2 className="text-lg font-semibold mb-4 text-gray-900">
                Détails
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Référence</span>
                  <strong className="text-gray-900">{quote.reference}</strong>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Statut</span>
                  <strong className="text-gray-900 capitalize">
                    {quote.status}
                  </strong>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Devise</span>
                  <strong className="text-gray-900">
                    {quote.currency ?? 'EUR'}
                  </strong>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Legal Terms Info */}
      <div className="flex gap-3 p-4 rounded-lg bg-brand/10 border border-brand/20">
        <div className="w-6 h-6 rounded-full bg-brand text-brand-foreground flex items-center justify-center flex-shrink-0">
          ✓
        </div>
        <div className="space-y-1">
          <p className="text-sm font-medium text-brand">
            Conditions générales incluses
          </p>
          <Link
            to="/legal-terms"
            className="text-xs text-brand hover:underline"
          >
            Voir mes conditions →
          </Link>
        </div>
      </div>

      {/* Lignes */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Prestations</CardTitle>
        </CardHeader>
        <CardContent>
          {!quote.line_items || quote.line_items.length === 0 ? (
            <div className="text-center py-6 text-muted-foreground">
              Aucune ligne de devis.
            </div>
          ) : (
            <div className="rounded-lg border border-border bg-card shadow-lg overflow-hidden">
              <Table>
                <TableHeader className="bg-muted/50">
                  <TableRow className="hover:bg-muted/50">
                    <TableHead>Prestation</TableHead>
                    <TableHead className="text-right">Qté</TableHead>
                    <TableHead className="text-right">PU HT</TableHead>
                    <TableHead className="text-right">TVA</TableHead>
                    <TableHead className="text-right">Total</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {quote.line_items.map((l) => {
                    const total =
                      l.total ??
                      (l.pre_tax_total ?? l.quantity * l.unit_price) +
                        (l.tax_amount ?? 0);
                    return (
                      <TableRow
                        key={String(l.id)}
                        className="hover:bg-accent/50"
                      >
                        <TableCell>
                          <div className="font-medium">{l.designation}</div>
                          {l.description ? (
                            <div className="text-xs text-muted-foreground mt-1">
                              {l.description}
                            </div>
                          ) : null}
                        </TableCell>
                        <TableCell className="text-right">
                          {l.quantity}
                        </TableCell>
                        <TableCell className="text-right">
                          {money.format(l.unit_price)}
                        </TableCell>
                        <TableCell className="text-right">
                          {((l.tax_rate ?? 0) * 100).toFixed(2)}%
                        </TableCell>
                        <TableCell className="text-right">
                          {money.format(total)}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
                <TableFooter>
                  <TableRow>
                    <TableCell colSpan={4} className="text-right">
                      Sous-total
                    </TableCell>
                    <TableCell className="text-right">
                      {money.format(computed!.sub)}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell colSpan={4} className="text-right">
                      TVA
                    </TableCell>
                    <TableCell className="text-right">
                      {money.format(computed!.taxes)}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell colSpan={4} className="text-right font-bold">
                      Total
                    </TableCell>
                    <TableCell className="text-right font-bold text-lg">
                      {money.format(computed!.total)}
                    </TableCell>
                  </TableRow>
                </TableFooter>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {!!quote.note && (
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">
              {quote.note}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Danger Zone */}
      <Card className="border-destructive/50 bg-destructive/5">
        <CardHeader>
          <CardTitle className="text-destructive">Zone dangereuse</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-destructive/80 mb-4">
            La suppression est irréversible pour les devis terminés (Payé,
            Annulé, Expiré, Refusé).
            {['DRAFT', 'SENT', 'ACCEPTED'].includes(quote.status) && (
              <strong className="block mt-2 text-destructive">
                ⚠️ La suppression est bloquée car le devis est en cours (statut:{' '}
                {quote.status}).
              </strong>
            )}
          </p>
          <Button
            variant="destructive"
            onClick={() => setShowDeleteDialog(true)}
            disabled={['DRAFT', 'SENT', 'ACCEPTED'].includes(quote.status)}
            title={
              ['DRAFT', 'SENT', 'ACCEPTED'].includes(quote.status)
                ? 'La suppression est bloquée pour les devis en cours'
                : 'Supprimer le devis'
            }
          >
            Supprimer ce devis
          </Button>
        </CardContent>
      </Card>

      <QuoteEmailPreviewDialog
        open={showEmailDialog}
        onClose={() => setShowEmailDialog(false)}
        quoteId={quote.id}
      />

      <DeleteConfirmDialog
        open={showDeleteDialog}
        onClose={() => {
          setShowDeleteDialog(false);
          setDeleteError(null);
        }}
        onConfirm={handleDelete}
        title="Supprimer le devis"
        message={`Êtes-vous sûr de vouloir supprimer définitivement le devis "${quote.reference}" ? Cette action ne peut pas être annulée.`}
        confirmText="Supprimer définitivement"
        isDeleting={isDeleting}
        errorMessage={deleteError}
      />
    </Shell>
  );
}
