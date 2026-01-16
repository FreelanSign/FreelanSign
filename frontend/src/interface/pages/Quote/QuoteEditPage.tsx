// src/interface/pages/QuoteEditPage.tsx
import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { Textarea } from '@/components/ui/textarea';
import {
  Briefcase,
  Calendar,
  ChevronLeft,
  Eye,
  FileText,
  List,
  PlusCircle,
  Save,
  Trash2,
  User,
} from 'lucide-react';

import type { AccountDto } from '../../../domain/account/types';
import { apiToUiQuote } from '../../../domain/quote/mappers';
import type {
  ApiQuoteResponse,
  ApiQuoteUpdatePayload,
} from '../../../domain/quote/types';
import type { UserDto } from '../../../domain/user/types';
import { accountRepository } from '../../../infrastructure/account/accountRepository';
import { useAccountStore } from '../../../infrastructure/account/accountStore';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';
import { userRepository } from '../../../infrastructure/user/userRepository';
import Modal from '../../components/common/Modal';
import { PdfPreviewPanel } from '../../components/quote/PdfPreviewPanel';
import { useDebouncedValue } from '../../hooks/useDebouncedValue';
import { usePdfPreview, type PreviewPayload } from '../../hooks/usePdfPreview';
import { useRequireAccount } from '../../hooks/useRequireAccount';
import { openBlobUrlInNewTab, saveBlobUrlAs } from '../../utils/saveFile';

type QuoteLine = {
  id?: string | number;
  designation: string;
  description?: string | null;
  quantity: number;
  unit_price: number;
  /** 0.2 => 20% (fraction UI) */
  tax_rate?: number | null;
};

type ClientInfo = {
  id?: string; // UUID renvoyé par l'API
  name: string;
  email?: string | null;
  phone?: string | null;
  company?: string | null;
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  postal_code?: string | null;
  country?: string | null;
  vat_number?: string | null;
};

type Quote = {
  id: string;
  reference: string;
  title: string;
  status: string;
  issue_date?: string | null; // YYYY-MM-DD
  due_date?: string | null; // UI -> valid_until (API)
  currency?: string | null;
  notes?: string | null; // UI -> note (API)
  terms?: string | null; // UI only
  client?: ClientInfo | null;
  line_items: QuoteLine[];
};

function useMoneyFormatter(currency?: string | null) {
  return useMemo(
    () =>
      new Intl.NumberFormat(undefined, {
        style: 'currency',
        currency: currency ?? 'EUR',
        maximumFractionDigits: 2,
      }),
    [currency],
  );
}

const EMPTY_CLIENT_CONST: ClientInfo = {
  id: undefined,
  name: '',
  email: '',
  company: '',
  address_line1: '',
  address_line2: '',
  city: '',
  postal_code: '',
  country: '',
};

export default function QuoteEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [quote, setQuote] = useState<Quote | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [user, setUser] = useState<UserDto | null>(null);
  const [account, setAccount] = useState<AccountDto | null>(null);
  const activeAccountId = useAccountStore((state) => state.activeAccountId);

  // TODO: ajouter un message d'erreur si pas de compte
  // Redirect vers l'onboarding si aucun compte après chargement
  useRequireAccount({ loading });

  // --- Load user and account ---
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const [userData, accountData] = await Promise.all([
          userRepository.getMe(),
          activeAccountId
            ? accountRepository.retrieve(activeAccountId)
            : Promise.resolve(null),
        ]);
        if (!active) return;
        setUser(userData);
        setAccount(accountData);
      } catch (e) {
        if (!active) return;
        console.error('Erreur chargement user/account', e);
        setUser(null);
        setAccount(null);
      }
    })();
    return () => {
      active = false;
    };
  }, [activeAccountId]);

  // --- Load ---
  useEffect(() => {
    if (!id) return;
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const api: ApiQuoteResponse = await quoteRepository.retrieve(id);

        if (!active) return;

        // Domain API → UiQuote (générique)
        const uiBase = apiToUiQuote(api);

        // UiQuote (domain) → Quote (UI locale de la page)
        const ui: Quote = {
          id: uiBase.id,
          reference: uiBase.reference,
          title: uiBase.title,
          status: uiBase.status,
          issue_date: uiBase.issue_date ?? null,
          due_date: uiBase.due_date ?? null,
          currency: uiBase.currency ?? 'EUR',
          notes: uiBase.notes ?? '',
          terms: uiBase.terms ?? '',
          client: uiBase.client
            ? {
                id: uiBase.client.id,
                name: uiBase.client.name ?? '',
                email: uiBase.client.email ?? '',
                company: uiBase.client.company ?? '',
                address_line1: uiBase.client.address_line1 ?? '',
                address_line2: uiBase.client.address_line2 ?? '',
                city: uiBase.client.city ?? '',
                postal_code: uiBase.client.postal_code ?? '',
                country: uiBase.client.country ?? '',
              }
            : {
                id: undefined,
                name: '',
                email: '',
                company: '',
                address_line1: '',
                address_line2: '',
                city: '',
                postal_code: '',
                country: '',
              },
          line_items: uiBase.line_items.map(
            (l, idx): QuoteLine => ({
              id: l.id ?? idx,
              designation: l.designation,
              description: l.description ?? '',
              quantity: l.quantity,
              unit_price: l.unit_price,
              tax_rate: l.tax_rate ?? 0,
            }),
          ),
        };

        setQuote(ui);
      } catch (err) {
        const e = err as { response?: { data?: unknown }; message?: string };
        setError(
          e.response?.data
            ? JSON.stringify(e.response.data)
            : (e.message ?? 'Erreur'),
        );
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [id]);

  const money = useMoneyFormatter(quote?.currency ?? 'EUR');

  function todayISO(): string {
    const d = new Date();
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 10);
  }

  // --- Build du payload de preview ---
  const previewPayload: PreviewPayload | null = useMemo(() => {
    const seller = {
      name: account?.display_name ?? 'FreelanSign',
      email: user?.email ?? 'contact@freelansign.com',
      siret: account?.legal_id ?? '',
    };
    const client = quote?.client
      ? {
          name: quote.client.name,
          email: quote.client.email,
          company: quote.client.company,
          address_line1: quote.client.address_line1,
          address_line2: quote.client.address_line2,
          city: quote.client.city,
          postal_code: quote.client.postal_code,
        }
      : EMPTY_CLIENT_CONST;
    const meta = {
      number: quote?.reference ?? 'Undefined PREVIEW',
      date: quote?.issue_date ?? todayISO(),
      valid_until: quote?.due_date ?? todayISO(),
      payment_terms: quote?.terms ?? 'Conditions générales sur demande.',
      currency: quote?.currency ?? 'EUR',
      language: 'fr',
      title: quote?.title ?? 'Undefined Devis',
    };
    const lines = (quote?.line_items ?? []).map((l) => ({
      designation: l.designation || 'Prestation',
      description: l.description ?? null,
      quantity: Number(l.quantity),
      unit_price: Number(l.unit_price ?? 0),
      tax_rate: typeof l.tax_rate === 'number' ? l.tax_rate : null,
      discount: 0,
    }));
    const branding = { name: 'FreelanSign' };
    return { seller, client, meta, lines, branding };
  }, [quote, account?.display_name, user?.email, account?.legal_id]);

  const debouncedPreviewPayload = useDebouncedValue<PreviewPayload | null>(
    previewPayload,
    500,
  );
  const {
    url: pdfUrl,
    loading: pdfLoading,
    error: pdfError,
    refresh: refreshPdf,
  } = usePdfPreview(debouncedPreviewPayload, previewOpen);
  useEffect(() => {
    if (previewOpen) {
      refreshPdf();
    }
  }, [previewOpen, refreshPdf]);

  // Derived totals (UI)
  const totals = useMemo(() => {
    const lines = quote?.line_items ?? [];
    const sub = lines.reduce((acc, l) => acc + l.quantity * l.unit_price, 0);
    const tax = lines.reduce((acc, l) => {
      const rate = l.tax_rate ?? 0;
      return acc + l.quantity * l.unit_price * rate;
    }, 0);
    return { sub, tax, total: sub + tax };
  }, [quote]);

  const setField = <K extends keyof Quote>(key: K, value: Quote[K]) => {
    setQuote((q) => (q ? { ...q, [key]: value } : q));
  };

  const setClient = <K extends keyof ClientInfo>(
    key: K,
    value: ClientInfo[K],
  ) => {
    setQuote((q) => {
      if (!q) return q;
      const base = q.client ?? EMPTY_CLIENT_CONST;
      return { ...q, client: { ...base, [key]: value } };
    });
  };

  const updateLine = (idx: number, patch: Partial<QuoteLine>) => {
    setQuote((q) => {
      if (!q) return q;
      const copy = [...q.line_items];
      copy[idx] = { ...copy[idx], ...patch };
      return { ...q, line_items: copy };
    });
  };

  const addLine = () => {
    setQuote((q) => {
      if (!q) return q;
      const next: QuoteLine = {
        designation: '',
        description: '',
        quantity: 1,
        unit_price: 0,
        tax_rate: 0.2,
      };
      return { ...q, line_items: [...q.line_items, next] };
    });
  };

  const removeLine = (idx: number) => {
    setQuote((q) => {
      if (!q) return q;
      const copy = q.line_items.filter((_, i) => i !== idx);
      return { ...q, line_items: copy };
    });
  };

  const validate = (): string[] => {
    const errs: string[] = [];
    if (!quote) return ['Formulaire vide'];
    if (!quote.title?.trim()) errs.push('Le titre est requis.');
    if (!quote.reference?.trim()) errs.push('La référence est requise.');
    if (!quote.status?.trim()) errs.push('Le statut est requis.');
    if (!quote.client?.name?.trim()) errs.push('Le nom du client est requis.');
    quote.line_items.forEach((l, i) => {
      if (!l.designation?.trim())
        errs.push(`Ligne #${i + 1}: désignation requise.`);
      if (!(l.quantity >= 0)) errs.push(`Ligne #${i + 1}: quantité invalide.`);
      if (!(l.unit_price >= 0)) errs.push(`Ligne #${i + 1}: PU invalide.`);
      if (!((l.tax_rate ?? 0) >= 0))
        errs.push(`Ligne #${i + 1}: TVA invalide.`);
    });
    return errs;
  };

  const toApiPayload = (q: Quote): ApiQuoteUpdatePayload => {
    const payload: ApiQuoteUpdatePayload = {
      title: q.title,
      reference: q.reference,
      status: (q.status || '').toUpperCase(),
      issue_date: q.issue_date ?? null,
      valid_until: q.due_date ?? null,
      currency: q.currency ?? 'EUR',
      note: q.notes ?? '',
      payment_terms_text: q.terms ?? '',
      metadata: {},
      client: q.client?.id, // UUID attendu par l'API
      client_update: {
        name: q.client?.name ?? '',
        email: q.client?.email ?? '',
        phone: q.client?.phone ?? null,
        // Structured address fields
        address_line1: q.client?.address_line1 ?? null,
        address_line2: q.client?.address_line2 ?? null,
        city: q.client?.city ?? null,
        postal_code: q.client?.postal_code ?? null,
        country: q.client?.country ?? null,
        company: q.client?.company ?? null,
        vat_number: q.client?.vat_number ?? null,
      },
    };

    if ((q.line_items?.length ?? 0) > 0) {
      payload.items = q.line_items.map((l, i) => ({
        description: l.designation,
        qty: String(l.quantity),
        unit_price: String(Number(l.unit_price).toFixed(2)),
        // 0.2 (20%) -> "20.00"
        tax_rate: String(((l.tax_rate ?? 0) * 100).toFixed(2)),
        discount: '0.00',
        order: i,
        metadata: { details: l.description || null },
      }));
    }

    return payload;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs = validate();
    if (errs.length) {
      setError(errs.join('\n'));
      return;
    }
    if (!id || !quote) return;

    setSaving(true);
    setError(null);
    try {
      const payload = toApiPayload(quote);
      console.log('Payload PATCH envoyé', payload);
      await quoteRepository.update(id, payload);
      navigate(`/quotes/${id}`);
    } catch (err) {
      console.error('Update quote error', err);
      const e = err as {
        response?: { data?: Record<string, unknown> };
        message?: string;
      };
      if (e.response?.data) {
        const data = e.response.data;
        if (typeof data === 'object' && !Array.isArray(data)) {
          // If specific fields have errors, show them cleanly
          const messages = Object.entries(data)
            .map(
              ([key, val]) =>
                `${key}: ${Array.isArray(val) ? val.join(' ') : JSON.stringify(val)}`,
            )
            .join('\n');
          setError(messages);
        } else {
          setError(JSON.stringify(data));
        }
      } else {
        setError(e.message ?? 'Une erreur est survenue lors de la sauvegarde.');
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading || !quote) {
    return (
      <div className="container mx-auto py-8 px-4 max-w-7xl space-y-8">
        <div className="space-y-4">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid gap-6">
          <Skeleton className="h-48 w-full rounded-xl" />
          <Skeleton className="h-96 w-full rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 space-y-8 max-w-7xl animate-in fade-in duration-500">
      {/* Header Row */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-border/60">
        <div className="space-y-1">
          <button
            onClick={() => navigate(`/quotes/${id}`)}
            className="flex items-center text-xs font-bold uppercase tracking-widest text-muted-foreground hover:text-brand transition-colors mb-2 group"
          >
            <ChevronLeft className="mr-1 h-3 w-3 transition-transform group-hover:-translate-x-0.5" />
            Retour au devis
          </button>
          <h1 className="text-3xl font-bold tracking-tight font-playfair">
            Édition du devis
          </h1>
          <p className="text-muted-foreground">
            Référence{' '}
            <span className="text-brand font-semibold">{quote.reference}</span>{' '}
            — Modifiez les détails et enregistrez vos changements.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="h-9 px-4 font-bold text-xs uppercase tracking-wider"
            onClick={() => setPreviewOpen(true)}
          >
            <Eye className="mr-2 h-4 w-4" />
            Aperçu PDF
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-9 px-4 font-bold text-xs uppercase tracking-wider"
            asChild
          >
            <Link to={`/quotes/${quote.id}`}>Annuler</Link>
          </Button>
          <Button
            className="h-9 px-6 bg-brand text-white hover:bg-brand-dark shadow-sm font-bold text-xs uppercase tracking-wider"
            onClick={handleSubmit}
            disabled={saving}
          >
            {saving ? (
              <>Enregistrement…</>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Enregistrer
              </>
            )}
          </Button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-sm text-destructive">
          ⚠️ {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            {/* Bloc Devis */}
            <Card className="shadow-none border border-border bg-white">
              <CardHeader className="border-b border-border/50 bg-muted/20">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-md bg-brand/10 text-brand">
                    <FileText size={18} />
                  </div>
                  <div>
                    <CardTitle className="text-lg font-semibold">
                      Détails du devis
                    </CardTitle>
                    <p className="text-xs text-muted-foreground">
                      Informations générales et dates de validité
                    </p>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-6">
                <div className="grid gap-6">
                  <div className="grid gap-6 md:grid-cols-2">
                    <div className="space-y-1.5">
                      <Label
                        htmlFor="reference"
                        className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                      >
                        Référence (Auto)
                      </Label>
                      <Input
                        id="reference"
                        value={quote.reference}
                        disabled
                        className="bg-muted/30 font-mono text-xs"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <Label
                        htmlFor="title"
                        className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                      >
                        Titre du devis
                      </Label>
                      <Input
                        id="title"
                        value={quote.title}
                        onChange={(e) => setField('title', e.target.value)}
                        placeholder="Ex: Refonte du site web"
                        className="h-10"
                      />
                    </div>
                  </div>

                  <div className="grid gap-6 md:grid-cols-2">
                    <div className="space-y-1.5">
                      <Label
                        htmlFor="status"
                        className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                      >
                        Statut
                      </Label>
                      <Select
                        value={quote.status}
                        onValueChange={(val) => setField('status', val)}
                      >
                        <SelectTrigger id="status" className="h-10">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="DRAFT">Brouillon</SelectItem>
                          <SelectItem value="SENT">Envoyé</SelectItem>
                          <SelectItem value="ACCEPTED">Accepté</SelectItem>
                          <SelectItem value="REJECTED">Refusé</SelectItem>
                          <SelectItem value="EXPIRED">Expiré</SelectItem>
                          <SelectItem value="PAID">Payé</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1.5">
                      <Label
                        htmlFor="currency"
                        className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                      >
                        Devise
                      </Label>
                      <Input
                        id="currency"
                        value={quote.currency ?? 'EUR'}
                        onChange={(e) => setField('currency', e.target.value)}
                        placeholder="EUR"
                        className="h-10"
                      />
                    </div>
                  </div>

                  <div className="grid gap-6 md:grid-cols-2">
                    <div className="space-y-1.5">
                      <Label
                        htmlFor="issue_date"
                        className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                      >
                        Date d'émission
                      </Label>
                      <div className="relative">
                        <Calendar className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="issue_date"
                          type="date"
                          value={quote.issue_date ?? ''}
                          className="pl-9 h-10"
                          onChange={(e) =>
                            setField('issue_date', e.target.value || null)
                          }
                        />
                      </div>
                    </div>
                    <div className="space-y-1.5">
                      <Label
                        htmlFor="due_date"
                        className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                      >
                        Valable jusqu'au
                      </Label>
                      <div className="relative">
                        <Calendar className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="due_date"
                          type="date"
                          value={quote.due_date ?? ''}
                          className="pl-9 h-10"
                          onChange={(e) =>
                            setField('due_date', e.target.value || null)
                          }
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Bloc Client */}
            <Card className="shadow-none border border-border bg-white">
              <CardHeader className="border-b border-border/50 bg-muted/20">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-md bg-brand/10 text-brand">
                    <User size={18} />
                  </div>
                  <div>
                    <CardTitle className="text-lg font-semibold">
                      Client
                    </CardTitle>
                    <p className="text-xs text-muted-foreground">
                      Coordonnées du destinataire
                    </p>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-6">
                <div className="grid gap-6 md:grid-cols-2">
                  <div className="space-y-1.5">
                    <Label
                      htmlFor="client_name"
                      className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                    >
                      Nom / Raison sociale
                    </Label>
                    <Input
                      id="client_name"
                      value={quote.client?.name ?? ''}
                      onChange={(e) => setClient('name', e.target.value)}
                      className="h-10"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label
                      htmlFor="client_email"
                      className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                    >
                      Email de contact
                    </Label>
                    <Input
                      id="client_email"
                      type="email"
                      value={quote.client?.email ?? ''}
                      onChange={(e) => setClient('email', e.target.value)}
                      className="h-10"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label
                      htmlFor="client_company"
                      className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                    >
                      Entreprise (facultatif)
                    </Label>
                    <Input
                      id="client_company"
                      value={quote.client?.company ?? ''}
                      onChange={(e) => setClient('company', e.target.value)}
                      className="h-10"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label
                      htmlFor="client_address1"
                      className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                    >
                      Adresse
                    </Label>
                    <Input
                      id="client_address1"
                      value={quote.client?.address_line1 ?? ''}
                      onChange={(e) =>
                        setClient('address_line1', e.target.value)
                      }
                      className="h-10"
                    />
                  </div>
                </div>
                <div className="grid gap-6 md:grid-cols-3 mt-6">
                  <div className="space-y-1.5">
                    <Label
                      htmlFor="client_postal"
                      className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                    >
                      CP
                    </Label>
                    <Input
                      id="client_postal"
                      value={quote.client?.postal_code ?? ''}
                      onChange={(e) => setClient('postal_code', e.target.value)}
                      className="h-10"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label
                      htmlFor="client_city"
                      className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                    >
                      Ville
                    </Label>
                    <Input
                      id="client_city"
                      value={quote.client?.city ?? ''}
                      onChange={(e) => setClient('city', e.target.value)}
                      className="h-10"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label
                      htmlFor="client_country"
                      className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                    >
                      Pays
                    </Label>
                    <Input
                      id="client_country"
                      value={quote.client?.country ?? ''}
                      onChange={(e) => setClient('country', e.target.value)}
                      className="h-10"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-8">
            {/* Colonne latérale: Notes & Conditions */}
            <Card className="shadow-none border border-border bg-white h-full">
              <CardHeader className="border-b border-border/50 bg-muted/20">
                <CardTitle className="text-sm font-bold uppercase tracking-widest text-muted-foreground">
                  Informations Légales
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                <div className="space-y-1.5">
                  <Label
                    htmlFor="notes"
                    className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                  >
                    Notes publiques
                  </Label>
                  <Textarea
                    id="notes"
                    value={quote.notes ?? ''}
                    onChange={(e) => setField('notes', e.target.value)}
                    rows={6}
                    className="resize-none"
                    placeholder="Visibles par le client sur le PDF…"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label
                    htmlFor="terms"
                    className="text-xs font-bold uppercase tracking-wider text-muted-foreground"
                  >
                    Conditions de vente
                  </Label>
                  <Textarea
                    id="terms"
                    value={quote.terms ?? ''}
                    onChange={(e) => setField('terms', e.target.value)}
                    rows={6}
                    className="resize-none"
                    placeholder="Paiement, délais, pénalités…"
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Bloc Lignes */}
        <Card className="shadow-none border border-border bg-white overflow-hidden">
          <CardHeader className="border-b border-border/50 bg-muted/20 flex flex-row items-center justify-between py-4">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-md bg-brand/10 text-brand">
                <List size={18} />
              </div>
              <CardTitle className="text-lg font-semibold leading-none">
                Prestations
              </CardTitle>
            </div>
            <Button
              type="button"
              size="sm"
              onClick={addLine}
              className="bg-brand text-white hover:bg-brand-dark"
            >
              <PlusCircle className="mr-2 h-4 w-4" />
              Ajouter une ligne
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            {quote.line_items.length === 0 ? (
              <div className="text-center py-12">
                <Briefcase className="mx-auto h-12 w-12 text-muted-foreground/20 mb-4" />
                <p className="text-muted-foreground text-sm font-medium">
                  Votre devis ne contient aucune ligne de prestation.
                </p>
                <Button variant="link" onClick={addLine} className="text-brand">
                  Commencez par en ajouter une.
                </Button>
              </div>
            ) : (
              <div className="divide-y divide-border/50">
                {quote.line_items.map((l, i) => {
                  const base = l.quantity * l.unit_price;
                  const tot = base * (1 + (l.tax_rate ?? 0));
                  return (
                    <div
                      key={i}
                      className="p-6 hover:bg-muted/5 transition-colors group relative"
                    >
                      <div className="flex items-start gap-4">
                        <div className="h-8 w-8 rounded-full bg-brand/5 border border-brand/10 text-brand flex items-center justify-center text-xs font-bold shrink-0 mt-1">
                          {i + 1}
                        </div>

                        <div className="flex-1 space-y-3">
                          {/* Row 1: Désignation */}
                          <div>
                            <Label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1.5 block">
                              Désignation
                            </Label>
                            <Input
                              value={l.designation}
                              onChange={(e) =>
                                updateLine(i, { designation: e.target.value })
                              }
                              placeholder="Nom du service ou produit"
                              className="h-10 font-semibold"
                            />
                          </div>

                          {/* Row 2: Description détaillée */}
                          <div>
                            <Label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1.5 block">
                              Détails{' '}
                              <span className="font-normal text-muted-foreground/60">
                                (optionnel)
                              </span>
                            </Label>
                            <Textarea
                              value={l.description ?? ''}
                              onChange={(e) =>
                                updateLine(i, { description: e.target.value })
                              }
                              placeholder="Détaillez ici les spécificités de cette prestation pour ce client..."
                              className="min-h-[60px] text-muted-foreground resize-y text-sm"
                              rows={2}
                            />
                          </div>

                          {/* Row 3: Quantité, Prix, TVA, Total */}
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 items-end pt-2">
                            <div className="space-y-1.5">
                              <Label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                                Quantité
                              </Label>
                              <Input
                                type="number"
                                min={0}
                                value={l.quantity}
                                onChange={(e) =>
                                  updateLine(i, {
                                    quantity: Number(e.target.value),
                                  })
                                }
                                className="h-9"
                              />
                            </div>
                            <div className="space-y-1.5">
                              <Label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                                Prix unitaire HT
                              </Label>
                              <div className="relative">
                                <Input
                                  type="number"
                                  min={0}
                                  step="0.01"
                                  value={l.unit_price}
                                  onChange={(e) =>
                                    updateLine(i, {
                                      unit_price: Number(e.target.value),
                                    })
                                  }
                                  className="h-9 pr-8"
                                />
                                <span className="absolute right-3 top-2.5 text-[10px] text-muted-foreground font-bold">
                                  €
                                </span>
                              </div>
                            </div>
                            <div className="space-y-1.5">
                              <Label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                                TVA
                              </Label>
                              <Select
                                value={(l.tax_rate ?? 0).toString()}
                                onValueChange={(val) =>
                                  updateLine(i, { tax_rate: Number(val) })
                                }
                              >
                                <SelectTrigger className="h-9">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="0">
                                    0% (Exonéré)
                                  </SelectItem>
                                  <SelectItem value="0.055">5,5%</SelectItem>
                                  <SelectItem value="0.1">10%</SelectItem>
                                  <SelectItem value="0.2">20%</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                            <div className="space-y-1.5 text-right">
                              <Label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                                Total TTC
                              </Label>
                              <div className="h-9 flex items-center justify-end font-bold text-brand">
                                {money.format(tot)}
                              </div>
                            </div>
                          </div>
                        </div>

                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => removeLine(i)}
                          className="text-muted-foreground/40 hover:text-destructive hover:bg-destructive/5 shrink-0"
                        >
                          <Trash2 size={18} />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Récapitulatif Final */}
            <div className="p-6 bg-muted/20 border-t border-border/50">
              <div className="flex flex-col items-end space-y-2">
                <div className="flex justify-between w-full max-w-[300px] text-sm text-muted-foreground">
                  <span>Total HT</span>
                  <span className="font-semibold">
                    {money.format(totals.sub)}
                  </span>
                </div>
                <div className="flex justify-between w-full max-w-[300px] text-sm text-muted-foreground">
                  <span>TVA</span>
                  <span className="font-semibold">
                    {money.format(totals.tax)}
                  </span>
                </div>
                <div className="flex justify-between w-full max-w-[300px] text-xl font-bold text-brand pt-2 border-t border-border">
                  <span>Total TTC</span>
                  <span>{money.format(totals.total)}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actions bas de page flottantes ou fixes */}
        <div className="flex items-center justify-end gap-3 pt-6 border-t border-border/30">
          <Button
            variant="ghost"
            className="font-bold text-xs uppercase tracking-widest text-muted-foreground"
            asChild
          >
            <Link to={`/quotes/${quote.id}`}>Abandonner les modifications</Link>
          </Button>
          <Button
            className="bg-brand text-white hover:bg-brand-dark px-8 h-10 font-bold text-xs uppercase tracking-widest shadow-md"
            onClick={handleSubmit}
            disabled={saving}
          >
            {saving ? (
              <>Enregistrement…</>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Mettre à jour le devis
              </>
            )}
          </Button>
        </div>
      </form>
      <Modal
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        title="Aperçu du devis"
        actions={
          <>
            <button
              type="button"
              onClick={refreshPdf}
              className="fs-btn fs-btn--ghost"
            >
              Actualiser
            </button>
            {pdfUrl && (
              <>
                <button
                  type="button"
                  className="fs-btn fs-btn--ghost"
                  onClick={() => openBlobUrlInNewTab(pdfUrl)}
                >
                  Ouvrir dans un nouvel onglet
                </button>
                <button
                  type="button"
                  className="fs-btn fs-btn--primary"
                  onClick={() =>
                    saveBlobUrlAs(
                      pdfUrl,
                      `devis-${(quote?.reference || 'preview').replace(/\s+/g, '_')}.pdf`,
                    )
                  }
                >
                  Télécharger
                </button>
              </>
            )}
          </>
        }
      >
        <div className="fs-pdf-shell">
          <PdfPreviewPanel url={pdfUrl} loading={pdfLoading} error={pdfError} />
        </div>
      </Modal>
    </div>
  );
}
