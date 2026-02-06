import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';
import DeleteConfirmDialog from '../../components/common/DeleteConfirmDialog';
import QuoteEmailPreviewDialog from '../../components/email/QuoteEmailPreviewDialog';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  AlertTriangle,
  Calendar,
  ChevronLeft,
  CreditCard,
  Download,
  Edit,
  ExternalLink,
  FileText,
  Info,
  Mail,
  MessageSquare,
  Trash2,
  User,
} from 'lucide-react';
import { StatusPill } from '../../components/quote/quote-column-components';

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
      lines.reduce((acc, l) => {
        const base = l.quantity * l.unit_price;
        const afterDiscount = base * (1 - (l.discount ?? 0) / 100);
        return acc + (l.pre_tax_total ?? Math.max(0, afterDiscount));
      }, 0);
    const taxes =
      quote.tax_total ??
      lines.reduce((acc, l) => {
        const base = l.quantity * l.unit_price;
        const preTax =
          l.pre_tax_total ?? Math.max(0, base * (1 - (l.discount ?? 0) / 100));
        return acc + (l.tax_amount ?? preTax * (l.tax_rate ?? 0));
      }, 0);
    const total = quote.total ?? sub + taxes - (quote.discount_total ?? 0);
    return { sub, taxes, total };
  }, [quote]);

  if (loading) {
    return (
      <div className="container mx-auto py-8 px-4 max-w-7xl space-y-8">
        <div className="space-y-4">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <Skeleton className="h-48 rounded-xl" />
          <Skeleton className="h-48 rounded-xl" />
        </div>
        <Skeleton className="h-96 w-full rounded-xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-12 px-4 max-w-md text-center">
        <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-destructive/10 text-destructive mb-6">
          <AlertTriangle size={32} />
        </div>
        <h1 className="text-xl font-bold mb-2 font-playfair">
          Erreur de chargement
        </h1>
        <p className="text-muted-foreground text-sm mb-6">{error}</p>
        <Button variant="outline" asChild>
          <Link to="/quotes">
            <ChevronLeft className="mr-2 h-4 w-4" />
            Retour à la liste
          </Link>
        </Button>
      </div>
    );
  }

  if (!quote) {
    return (
      <div className="container mx-auto py-12 px-4 max-w-md text-center">
        <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-muted text-muted-foreground mb-6">
          <FileText size={32} />
        </div>
        <h1 className="text-xl font-bold mb-2 font-playfair">
          Devis introuvable
        </h1>
        <p className="text-muted-foreground text-sm mb-6">
          Le devis demandé n'existe pas ou vous n'y avez pas accès.
        </p>
        <Button variant="outline" asChild>
          <Link to="/quotes">
            <ChevronLeft className="mr-2 h-4 w-4" />
            Retour à la liste
          </Link>
        </Button>
      </div>
    );
  }

  const addressLines = [
    quote.client?.company,
    quote.client?.address_line1,
    quote.client?.address_line2,
    [quote.client?.postal_code, quote.client?.city].filter(Boolean).join(' '),
    quote.client?.country,
  ].filter(Boolean);

  return (
    <div className="container mx-auto py-8 px-4 space-y-8 max-w-7xl animate-in fade-in duration-500">
      {/* Header Row */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-border/60">
        <div className="space-y-1">
          <button
            onClick={() => navigate('/quotes')}
            className="flex items-center text-xs font-bold uppercase tracking-widest text-muted-foreground hover:text-brand transition-colors mb-2 group"
          >
            <ChevronLeft className="mr-1 h-3 w-3 transition-transform group-hover:-translate-x-0.5" />
            Retour à la liste
          </button>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight font-playfair">
              {quote.reference}
            </h1>
            <StatusPill status={quote.status} />
          </div>
          <p className="text-muted-foreground">
            {quote.title} — Émis le{' '}
            <span className="font-medium">
              {quote.issue_date ? date.format(new Date(quote.issue_date)) : '—'}
            </span>
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownload}
            disabled={downloading}
            className="h-9 px-4 font-bold text-xs uppercase tracking-wider"
          >
            <Download className="mr-2 h-4 w-4" />
            {downloading ? 'Export...' : 'PDF'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="h-9 px-4 font-bold text-xs uppercase tracking-wider"
            onClick={() => setShowEmailDialog(true)}
          >
            <Mail className="mr-2 h-4 w-4" />
            Envoyer
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-9 px-4 font-bold text-xs uppercase tracking-wider text-destructive hover:text-destructive hover:bg-destructive/10"
            onClick={() => setShowDeleteDialog(true)}
            disabled={['ACCEPTED', 'PAID'].includes(quote.status)}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Supprimer
          </Button>
          {['DRAFT', 'SENT', 'ACCEPTED'].includes(quote.status) && (
            <>
              <div className="h-6 w-px bg-border/60 mx-1 hidden sm:block" />
              <Button
                className="h-9 px-6 bg-brand text-white hover:bg-brand-dark shadow-sm font-bold text-xs uppercase tracking-wider"
                asChild
                title="Modifier le devis"
              >
                <Link to={`/quotes/${quote.id}/edit`}>
                  <Edit className="mr-2 h-4 w-4" />
                  Modifier
                </Link>
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Grid Infos */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Card Client */}
          <Card className="shadow-none border border-border bg-white overflow-hidden">
            <CardHeader className="border-b border-border/50 bg-muted/20 pb-3">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-md bg-brand/10 text-brand">
                  <User size={18} />
                </div>
                <CardTitle className="text-lg font-semibold">
                  Destinataire
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              <div className="grid md:grid-cols-2 gap-8">
                <div className="space-y-4">
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1">
                      Nom du client
                    </p>
                    <p className="text-sm font-semibold">
                      {quote.client?.name || '—'}
                    </p>
                  </div>
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1">
                      Coordonnées
                    </p>
                    <div className="space-y-1">
                      {quote.client?.email && (
                        <a
                          href={`mailto:${quote.client.email}`}
                          className="text-sm text-brand hover:underline flex items-center gap-1.5"
                        >
                          <Mail size={12} />
                          {quote.client.email}
                        </a>
                      )}
                      {quote.client?.phone && (
                        <p className="text-sm text-muted-foreground flex items-center gap-1.5">
                          <ExternalLink size={12} />
                          {quote.client.phone}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1">
                      Adresse de facturation
                    </p>
                    <div className="text-sm text-muted-foreground not-italic leading-relaxed">
                      {addressLines.length
                        ? addressLines.map((l, i) => <div key={i}>{l}</div>)
                        : '—'}
                    </div>
                  </div>
                  {quote.client?.vat_number && (
                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1">
                        Numéro de TVA
                      </p>
                      <p className="text-sm font-mono text-muted-foreground bg-muted/50 inline-block px-1.5 py-0.5 rounded">
                        {quote.client.vat_number}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Table Prestations */}
          <Card className="shadow-none border border-border bg-white overflow-hidden">
            <CardHeader className="border-b border-border/50 bg-muted/20 pb-0">
              <div className="flex items-center gap-2 py-4">
                <div className="p-2 rounded-md bg-brand/10 text-brand">
                  <FileText size={18} />
                </div>
                <CardTitle className="text-lg font-semibold">
                  Prestations & Services
                </CardTitle>
              </div>
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent border-b border-border/50">
                    <TableHead className="h-10 py-3 text-[11px] font-bold text-muted-foreground uppercase tracking-wider pl-6">
                      Désignation
                    </TableHead>
                    <TableHead className="h-10 py-3 text-[11px] font-bold text-muted-foreground uppercase tracking-wider text-right">
                      Qté
                    </TableHead>
                    <TableHead className="h-10 py-3 text-[11px] font-bold text-muted-foreground uppercase tracking-wider text-right">
                      PU HT
                    </TableHead>
                    <TableHead className="h-10 py-3 text-[11px] font-bold text-muted-foreground uppercase tracking-wider text-right">
                      Remise
                    </TableHead>
                    <TableHead className="h-10 py-3 text-[11px] font-bold text-muted-foreground uppercase tracking-wider text-right">
                      TVA
                    </TableHead>
                    <TableHead className="h-10 py-3 text-[11px] font-bold text-muted-foreground uppercase tracking-wider text-right pr-6">
                      Total HT
                    </TableHead>
                  </TableRow>
                </TableHeader>
              </Table>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableBody>
                  {quote.line_items?.map((l) => (
                    <TableRow
                      key={String(l.id)}
                      className="hover:bg-muted/5 group"
                    >
                      <TableCell className="py-4 pl-6 align-top">
                        <div className="font-semibold text-sm group-hover:text-brand transition-colors">
                          {l.designation}
                        </div>
                        {l.description && (
                          <div className="text-xs text-muted-foreground mt-1.5 leading-relaxed max-w-sm">
                            {l.description}
                          </div>
                        )}
                      </TableCell>
                      <TableCell className="py-4 text-right align-top text-sm">
                        {l.quantity}
                      </TableCell>
                      <TableCell className="py-4 text-right align-top text-sm">
                        {money.format(l.unit_price)}
                      </TableCell>
                      <TableCell className="py-4 text-right align-top text-sm text-muted-foreground">
                        {l.discount && l.discount > 0 ? (
                          <span className="text-destructive font-medium whitespace-nowrap">
                            -{l.discount}%
                          </span>
                        ) : (
                          '—'
                        )}
                      </TableCell>
                      <TableCell className="py-4 text-right align-top text-sm text-muted-foreground font-medium">
                        {((l.tax_rate ?? 0) * 100).toFixed(0)}%
                      </TableCell>
                      <TableCell className="py-4 text-right align-top pr-6 font-bold text-sm">
                        {money.format(
                          l.pre_tax_total ??
                            Math.max(
                              0,
                              l.quantity *
                                l.unit_price *
                                (1 - (l.discount ?? 0) / 100),
                            ),
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Totaux Section */}
              <div className="p-6 bg-muted/20 border-t border-border/50">
                <div className="flex flex-col items-end space-y-2">
                  <div className="flex justify-between w-full max-w-[280px] text-sm text-muted-foreground">
                    <span>Sous-total HT</span>
                    <span className="font-semibold">
                      {money.format(computed!.sub)}
                    </span>
                  </div>
                  <div className="flex justify-between w-full max-w-[280px] text-sm text-muted-foreground">
                    <span>Total TVA</span>
                    <span className="font-semibold">
                      {money.format(computed!.taxes)}
                    </span>
                  </div>
                  <div className="flex justify-between w-full max-w-[280px] text-xl font-bold text-brand pt-2 border-t border-border mt-1">
                    <span>Total TTC</span>
                    <span>{money.format(computed!.total)}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-8">
          {/* Card Validity */}
          <Card className="shadow-none border border-border bg-white">
            <CardHeader className="border-b border-border/50 bg-muted/20 pb-3">
              <CardTitle className="text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
                Dates & Validité
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-brand shrink-0" />
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-0.5">
                    Émission
                  </p>
                  <p className="text-sm font-medium">
                    {quote.issue_date
                      ? date.format(new Date(quote.issue_date))
                      : '—'}
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Info className="h-5 w-5 text-brand shrink-0" />
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-0.5">
                    Validité
                  </p>
                  <p className="text-sm font-medium">
                    {quote.valid_until ? (
                      <span
                        className={
                          new Date(quote.valid_until) < new Date()
                            ? 'text-destructive'
                            : ''
                        }
                      >
                        Jusqu'au {date.format(new Date(quote.valid_until))}
                      </span>
                    ) : (
                      'Non spécifiée'
                    )}
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CreditCard className="h-5 w-5 text-brand shrink-0" />
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-0.5">
                    Devise
                  </p>
                  <p className="text-sm font-medium">
                    {quote.currency ?? 'EUR'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Notes Card */}
          {quote.note && (
            <Card className="shadow-none border border-border bg-white">
              <CardHeader className="border-b border-border/50 bg-muted/20 pb-3">
                <div className="flex items-center gap-2">
                  <MessageSquare size={16} className="text-brand" />
                  <CardTitle className="text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
                    Notes publiques
                  </CardTitle>
                </div>
              </CardHeader>
              <CardContent className="p-6">
                <p className="text-sm text-muted-foreground italic leading-relaxed">
                  "{quote.note}"
                </p>
              </CardContent>
            </Card>
          )}

          {/* Legal CTA */}
          <div className="p-6 rounded-xl border border-brand/20 bg-brand/5 space-y-3">
            <div className="flex items-center gap-2 text-brand font-bold text-xs uppercase tracking-wider">
              <Info size={14} />
              <span>Conditions Générales</span>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Ce devis est soumis à vos conditions générales de vente
              configurées dans votre profil professionnel.
            </p>
            <Button
              variant="link"
              className="p-0 h-auto text-brand text-xs font-bold uppercase tracking-widest"
              asChild
            >
              <Link to="/legal-terms">Consulter mes CGV →</Link>
            </Button>
          </div>
        </div>
      </div>

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
    </div>
  );
}
