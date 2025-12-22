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
import { Textarea } from '@/components/ui/textarea';

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
  company?: string | null;
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  postal_code?: string | null;
  country?: string | null;
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
                company: '', // champs spécifiques à ton formulaire
                address_line1: uiBase.client.address ?? '',
                address_line2: '',
                city: '',
                postal_code: '',
                country: '',
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
      metadata: {},
      client: q.client?.id, // UUID attendu par l'API
      client_update: {
        name: q.client?.name ?? '',
        email: q.client?.email ?? '',
        // ajoute ici phone/address/vat_number/metadata si supportés côté Client
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
        metadata: {},
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
      const e = err as { response?: { data?: unknown }; message?: string };
      setError(
        e.response?.data
          ? JSON.stringify(e.response.data)
          : (e.message ?? 'Erreur'),
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading || !quote) {
    return (
      <div className="grid gap-6">
        <div className="h-32 bg-muted/50 rounded-lg animate-pulse" />
        <div className="h-96 bg-muted/50 rounded-lg animate-pulse" />
      </div>
    );
  }
  return (
    <div className="container mx-auto py-6 px-4 sm:px-6 lg:px-8 space-y-6">
      <header className="flex items-start justify-between p-6 rounded-lg bg-gradient-to-r from-brand to-accent-orange text-white shadow-lg">
        <div>
          <h1 className="text-2xl font-bold">
            Éditer le devis — {quote.reference}
          </h1>
          <p className="text-sm opacity-95 mt-1">
            Modifiez les informations puis enregistrez.
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            type="button"
            variant="ghost"
            className="text-white hover:bg-white/20"
            onClick={() => setPreviewOpen(true)}
          >
            Aperçu
          </Button>
          <Button
            variant="ghost"
            className="text-white hover:bg-white/20"
            asChild
          >
            <Link to={`/quotes/${quote.id}`}>Annuler</Link>
          </Button>
          <Button
            className="bg-white text-brand hover:bg-white/90"
            onClick={handleSubmit}
            disabled={saving}
          >
            {saving ? 'Enregistrement…' : 'Enregistrer'}
          </Button>
        </div>
      </header>

      {error && (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-sm text-destructive">
          ⚠️ {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Bloc Devis */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Devis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex flex-col gap-2">
                <Label htmlFor="reference">Référence</Label>
                <Input
                  id="reference"
                  value={quote.reference}
                  disabled
                  placeholder="FS-2025-001"
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="title">Titre</Label>
                <Input
                  id="title"
                  value={quote.title}
                  onChange={(e) => setField('title', e.target.value)}
                  placeholder="Site vitrine 5 pages"
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="status">Statut</Label>
                <Select
                  value={quote.status}
                  onValueChange={(val) => setField('status', val)}
                >
                  <SelectTrigger id="status">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="DRAFT">draft</SelectItem>
                    <SelectItem value="SENT">sent</SelectItem>
                    <SelectItem value="ACCEPTED">accepted</SelectItem>
                    <SelectItem value="REJECTED">refused</SelectItem>
                    <SelectItem value="EXPIRED">expired</SelectItem>
                    <SelectItem value="PAID">paid</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="currency">Devise</Label>
                <Input
                  id="currency"
                  value={quote.currency ?? 'EUR'}
                  onChange={(e) => setField('currency', e.target.value)}
                  placeholder="EUR"
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="issue_date">Date d'émission</Label>
                <Input
                  id="issue_date"
                  type="date"
                  value={quote.issue_date ?? ''}
                  onChange={(e) =>
                    setField('issue_date', e.target.value || null)
                  }
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="due_date">Date de validité</Label>
                <Input
                  id="due_date"
                  type="date"
                  value={quote.due_date ?? ''}
                  onChange={(e) => setField('due_date', e.target.value || null)}
                />
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex flex-col gap-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={quote.notes ?? ''}
                  onChange={(e) => setField('notes', e.target.value)}
                  rows={3}
                  placeholder="Informations complémentaires visibles par le client…"
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="terms">Conditions</Label>
                <Textarea
                  id="terms"
                  value={quote.terms ?? ''}
                  onChange={(e) => setField('terms', e.target.value)}
                  rows={3}
                  placeholder="Modalités de paiement, délais, pénalités, etc."
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Bloc Client */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Client</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex flex-col gap-2">
                <Label htmlFor="client_name">Nom</Label>
                <Input
                  id="client_name"
                  value={quote.client?.name ?? ''}
                  onChange={(e) => setClient('name', e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="client_email">Email</Label>
                <Input
                  id="client_email"
                  type="email"
                  value={quote.client?.email ?? ''}
                  onChange={(e) => setClient('email', e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="client_company">Entreprise</Label>
                <Input
                  id="client_company"
                  value={quote.client?.company ?? ''}
                  onChange={(e) => setClient('company', e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="client_address1">Adresse (ligne 1)</Label>
                <Input
                  id="client_address1"
                  value={quote.client?.address_line1 ?? ''}
                  onChange={(e) => setClient('address_line1', e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="client_address2">Adresse (ligne 2)</Label>
                <Input
                  id="client_address2"
                  value={quote.client?.address_line2 ?? ''}
                  onChange={(e) => setClient('address_line2', e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="client_city">Ville</Label>
                <Input
                  id="client_city"
                  value={quote.client?.city ?? ''}
                  onChange={(e) => setClient('city', e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="client_postal">Code postal</Label>
                <Input
                  id="client_postal"
                  value={quote.client?.postal_code ?? ''}
                  onChange={(e) => setClient('postal_code', e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="client_country">Pays</Label>
                <Input
                  id="client_country"
                  value={quote.client?.country ?? ''}
                  onChange={(e) => setClient('country', e.target.value)}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Lignes</CardTitle>
              <Button
                type="button"
                onClick={addLine}
                className="bg-accent-orange text-white hover:bg-accent-orange/90"
              >
                + Ajouter
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {quote.line_items.length === 0 ? (
              <div className="text-center py-6 text-muted-foreground">
                Aucune ligne
              </div>
            ) : (
              <>
                <div style={{ display: 'grid', gap: '12px' }}>
                  {quote.line_items.map((l, i) => {
                    const base = l.quantity * l.unit_price;
                    const tot = base * (1 + (l.tax_rate ?? 0));
                    return (
                      <div
                        key={i}
                        style={{
                          padding: '16px',
                          border: '1px solid rgba(13,13,13,0.1)',
                          borderRadius: '8px',
                          background: '#fff',
                          display: 'grid',
                          gap: '12px',
                        }}
                      >
                        <div
                          style={{
                            display: 'flex',
                            gap: '12px',
                            alignItems: 'center',
                          }}
                        >
                          <span
                            style={{
                              minWidth: '32px',
                              height: '32px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              background: '#f0f4ff',
                              borderRadius: '6px',
                              fontWeight: '600',
                              fontSize: '0.9rem',
                              color: 'var(--brand)',
                            }}
                          >
                            {i + 1}
                          </span>

                          <Input
                            value={l.designation}
                            onChange={(e) =>
                              updateLine(i, { designation: e.target.value })
                            }
                            placeholder="Prestation"
                            style={{ flex: 1 }}
                          />

                          <button
                            type="button"
                            onClick={() => removeLine(i)}
                            style={{
                              padding: '8px 12px',
                              border: '1px solid rgba(13,13,13,0.1)',
                              borderRadius: '6px',
                              background: '#fff',
                              cursor: 'pointer',
                              fontSize: '0.85rem',
                            }}
                          >
                            ✕
                          </button>
                        </div>

                        <Input
                          value={l.description ?? ''}
                          onChange={(e) =>
                            updateLine(i, { description: e.target.value })
                          }
                          placeholder="Description (optionnel)"
                        />

                        <div
                          style={{
                            display: 'grid',
                            gridTemplateColumns:
                              'repeat(auto-fit, minmax(100px, 1fr))',
                            gap: '12px',
                          }}
                        >
                          <label style={{ display: 'grid', gap: '4px' }}>
                            <span
                              style={{ fontSize: '0.75rem', color: '#666' }}
                            >
                              Quantité
                            </span>
                            <Input
                              type="number"
                              min={0}
                              step="1"
                              value={l.quantity}
                              onChange={(e) =>
                                updateLine(i, {
                                  quantity: Number(e.target.value),
                                })
                              }
                            />
                          </label>

                          <label style={{ display: 'grid', gap: '4px' }}>
                            <span
                              style={{ fontSize: '0.75rem', color: '#666' }}
                            >
                              Prix unitaire
                            </span>
                            <div
                              style={{ display: 'flex', alignItems: 'stretch' }}
                            >
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
                                style={{
                                  borderTopRightRadius: 0,
                                  borderBottomRightRadius: 0,
                                  borderRight: 'none',
                                }}
                              />
                              <span
                                style={{
                                  padding: '0 12px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  border: '1px solid rgba(13,13,13,0.12)',
                                  borderTopRightRadius: '12px',
                                  borderBottomRightRadius: '12px',
                                  background: '#f8fafc',
                                  fontSize: '0.9rem',
                                }}
                              >
                                €
                              </span>
                            </div>
                          </label>

                          <label style={{ display: 'grid', gap: '4px' }}>
                            <span
                              style={{ fontSize: '0.75rem', color: '#666' }}
                            >
                              TVA
                            </span>
                            <Select
                              value={(l.tax_rate ?? 0).toString()}
                              onValueChange={(val) =>
                                updateLine(i, {
                                  tax_rate: Number(val),
                                })
                              }
                            >
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="0">0%</SelectItem>
                                <SelectItem value="0.055">5,5%</SelectItem>
                                <SelectItem value="0.1">10%</SelectItem>
                                <SelectItem value="0.2">20%</SelectItem>
                              </SelectContent>
                            </Select>
                          </label>

                          <div style={{ display: 'grid', gap: '4px' }}>
                            <span
                              style={{ fontSize: '0.75rem', color: '#666' }}
                            >
                              Total TTC
                            </span>
                            <div
                              style={{
                                padding: '12px 16px',
                                background: '#f8fafc',
                                borderRadius: '12px',
                                fontWeight: '600',
                                fontSize: '1rem',
                              }}
                            >
                              {money.format(tot)}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div
                  style={{
                    marginTop: '16px',
                    padding: '16px',
                    background: '#f8fafc',
                    borderRadius: '8px',
                    display: 'grid',
                    gap: '8px',
                  }}
                >
                  <div
                    style={{ display: 'flex', justifyContent: 'space-between' }}
                  >
                    <span>Sous-total HT</span>
                    <strong>{money.format(totals.sub)}</strong>
                  </div>
                  <div
                    style={{ display: 'flex', justifyContent: 'space-between' }}
                  >
                    <span>TVA</span>
                    <strong>{money.format(totals.tax)}</strong>
                  </div>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      paddingTop: '8px',
                      borderTop: '2px solid rgba(13,13,13,0.1)',
                      fontSize: '1.1rem',
                    }}
                  >
                    <strong>Total TTC</strong>
                    <strong>{money.format(totals.total)}</strong>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Actions bas de page (fallback submit) */}
        <div className="flex items-center gap-2">
          <Button disabled={saving}>
            {saving ? 'Enregistrement…' : 'Enregistrer'}
          </Button>
          <Button variant="ghost" asChild>
            <Link to={`/quotes/${quote.id}`}>Annuler</Link>
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
