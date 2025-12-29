// src/interface/pages/QuoteCreatePage.tsx
import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useMemo, useState } from 'react';
import {
  useFieldArray,
  useForm,
  useWatch,
  type Resolver,
  type SubmitHandler,
} from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { z } from 'zod';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';

import { PlusCircle, Trash2 } from 'lucide-react';
import type { AccountDto } from '../../../domain/account/types';
import type { PrestationDto } from '../../../domain/catalog/types';
import type { ClientDto } from '../../../domain/client/types';
import type { UserDto } from '../../../domain/user/types';
import { accountRepository } from '../../../infrastructure/account/accountRepository';
import { useAccountStore } from '../../../infrastructure/account/accountStore';
import { catalogRepository } from '../../../infrastructure/catalog/catalogRepository';
import { clientRepository } from '../../../infrastructure/client/clientRepository';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';
import { userRepository } from '../../../infrastructure/user/userRepository';
import ClientCreateDrawer from '../../components/client/ClientCreateDrawer';
import Modal from '../../components/common/Modal';
import { PdfPreviewPanel } from '../../components/quote/PdfPreviewPanel';
import { useDebouncedValue } from '../../hooks/useDebouncedValue';
import { usePdfPreview } from '../../hooks/usePdfPreview';
import { useRequireAccount } from '../../hooks/useRequireAccount';
import { openBlobUrlInNewTab, saveBlobUrlAs } from '../../utils/saveFile';

/* ---------- zod schema ---------- */
const ItemSchema = z.object({
  prestation_id: z.number().int().positive().optional(),
  description: z.string().min(1, 'Description requise'),
  qty: z.number().positive('Qty doit être > 0'),
  unit_price: z.number().nonnegative('Prix unitaire >= 0'),
  tax_rate: z.number().min(0).max(100).optional(),
  discount: z.number().nonnegative().optional(),
});

const Schema = z.object({
  client: z.string().min(1, 'Choisis un client'),
  title: z.string().min(1, 'Titre requis'),
  currency: z.string().length(3).default('EUR'),
  language: z.string().min(2).max(8).default('fr'),
  issue_date: z.string().min(8, 'Date requise (YYYY-MM-DD)'),
  valid_until: z.string().optional().or(z.literal('')),
  payment_terms_text: z.string().optional(),
  items: z.array(ItemSchema).min(1, 'Au moins une ligne est requise'),
});

type FormData = z.infer<typeof Schema>;

/* ---------- helper types for payload ---------- */
type QuoteItemPayload = {
  prestation_id?: number;
  description: string;
  qty: number;
  unit_price: number;
  tax_rate?: number;
  discount: number;
  metadata?: Record<string, unknown>;
};

type QuotePayload = {
  client: string;
  title: string;
  currency: string;
  language: string;
  issue_date: string;
  valid_until?: string | null;
  payment_terms_text?: string | null;
  items: QuoteItemPayload[];
};

/* ---------- small utility helpers ---------- */

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

function todayISO(): string {
  const d = new Date();
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 10);
}

/** Type guard minimal pour détecter un objet d'erreur axios-like */
function isAxiosLikeError(
  e: unknown,
): e is { response?: { data?: unknown }; message?: string } {
  return (
    typeof e === 'object' && e !== null && ('response' in e || 'message' in e)
  );
}

/* ---------- component ---------- */
export default function QuoteCreatePage() {
  const [previewOpen, setPreviewOpen] = useState(false);
  const [clientDrawerOpen, setClientDrawerOpen] = useState(false);
  const navigate = useNavigate();
  const [clients, setClients] = useState<ClientDto[] | 'loading' | null>(
    'loading',
  );
  const [prestations, setPrestations] = useState<
    PrestationDto[] | 'loading' | null
  >('loading');
  const [user, setUser] = useState<UserDto | null>(null);
  const [account, setAccount] = useState<AccountDto | null>(null);
  const activeAccountId = useAccountStore((state) => state.activeAccountId);
  const [loading, setLoading] = useState(false);

  // Loading initial de la page
  const pageLoading = clients === 'loading' || prestations === 'loading';
  useRequireAccount({ loading: pageLoading });

  // Remarque: on force le type Resolver<FormData> pour que zodResolver soit compatible
  const resolver = zodResolver(Schema) as unknown as Resolver<FormData>;

  const form = useForm<FormData>({
    resolver,
    defaultValues: {
      currency: 'EUR',
      language: 'fr',
      issue_date: todayISO(),
      items: [
        {
          prestation_id: undefined,
          description: 'Nouvelle prestation',
          qty: 1,
          unit_price: 0.0,
          tax_rate: 20.0,
          discount: 0.0,
        },
      ],
    },
  });

  const {
    control,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = form;
  const { fields, append, remove } = useFieldArray({ control, name: 'items' });

  const watchedItems = useWatch({ control, name: 'items' }) as
    | FormData['items']
    | undefined;
  const watchedCurrency = useWatch({ control, name: 'currency' }) || 'EUR';
  const watchedClientId = useWatch({ control, name: 'client' }) as
    | string
    | undefined;
  const watchedTitle = useWatch({ control, name: 'title' }) as
    | string
    | undefined;
  const watchedLanguage = useWatch({ control, name: 'language' }) as
    | string
    | undefined;
  const watchedIssueDate = useWatch({ control, name: 'issue_date' }) as
    | string
    | undefined;
  const watchedValidUntil = useWatch({ control, name: 'valid_until' }) as
    | string
    | undefined;
  const watchedPaymentTermsText = useWatch({
    control,
    name: 'payment_terms_text',
  }) as string | undefined;

  const money = useMoneyFormatter(watchedCurrency);

  // ----- Build du payload de preview -----
  const selectedClient: ClientDto | undefined =
    clients && clients !== 'loading'
      ? clients.find((c) => String(c.id) === String(watchedClientId || ''))
      : undefined;

  const previewPayload = useMemo(() => {
    const seller = {
      name: account?.display_name ?? 'FreelanSign',
      email: user?.email ?? 'contact@freelansign.com',
      siret: account?.legal_id ?? '',
    };
    const client = selectedClient
      ? {
          name: selectedClient.name,
          email: selectedClient.email,
          phone: selectedClient.phone,
        }
      : {
          name: 'Client non sélectionné',
        };

    const meta = {
      number: 'PREVIEW',
      date: watchedIssueDate || todayISO(),
      valid_until: watchedValidUntil || todayISO(),
      payment_terms:
        watchedPaymentTermsText || 'Conditions générales sur demande.',
      currency: watchedCurrency || 'EUR',
      language: watchedLanguage || 'fr',
      title: watchedTitle || 'Undefined Devis',
    };

    const lines =
      (watchedItems || []).map((item) => ({
        designation: item.description || 'Prestation',
        description: null,
        quantity: Number(item.qty ?? 0),
        unit_price: Number(item.unit_price ?? 0),
        tax_rate:
          typeof item.tax_rate === 'number'
            ? Number(item.tax_rate) / 100
            : null,
        discount: typeof item.discount === 'number' ? Number(item.discount) : 0,
      })) ?? [];
    const branding = { name: 'FreelanSign' };
    return { seller, client, meta, lines, branding };
  }, [
    account?.display_name,
    user?.email,
    account?.legal_id,
    selectedClient,
    watchedItems,
    watchedIssueDate,
    watchedValidUntil,
    watchedPaymentTermsText,
    watchedCurrency,
    watchedLanguage,
    watchedTitle,
  ]);

  // On évite de spammer l'API : debounce 500ms
  const debouncedPreviewPayload = useDebouncedValue(previewPayload, 500);
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

  const totals = useMemo(() => {
    const lines = watchedItems ?? [];
    let sub = 0;
    let tax = 0;
    for (const line of lines) {
      const qty = Number(line?.qty ?? 0);
      const unit = Number(line?.unit_price ?? 0);
      const discount = Number(line?.discount ?? 0);
      const taxRate = Number(line?.tax_rate ?? 0);

      const base = qty * unit;
      const afterDiscount = base * (1 - discount / 100);
      const lineTax = afterDiscount * (taxRate / 100);

      sub += afterDiscount;
      tax += lineTax;
    }
    return { sub, tax, total: sub + tax };
  }, [watchedItems]);

  // Charger clients
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const response = await clientRepository.list();
        if (!active) return;
        setClients(response.results);
      } catch (e) {
        console.error('Erreur chargement clients', e);
        if (!active) return;
        setClients(null);
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  // Charger les prestations liées au compte professionnel
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

        const ids = accountData?.service_type_ids ?? [];

        if (!ids.length) {
          if (active) setPrestations([]);
          return;
        }

        const list = await catalogRepository.listPrestations({ ids });
        if (!active) return;
        setPrestations(list);
      } catch (e) {
        console.error('Erreur chargement prestations liées', e);
        if (!active) return;
        setPrestations(null);
      }
    })();
    return () => {
      active = false;
    };
  }, [activeAccountId]);

  // ---- helpers de narrowing sûrs
  function pickString(
    o: Record<string, unknown>,
    keys: string[],
  ): string | undefined {
    for (const k of keys) {
      const v = o[k];
      if (typeof v === 'string' && v.trim() !== '') return v;
    }
    return undefined;
  }

  function pickNumber(
    o: Record<string, unknown>,
    keys: string[],
  ): number | undefined {
    for (const k of keys) {
      const v = o[k];
      if (typeof v === 'number' && Number.isFinite(v)) return v;
    }
    return undefined;
  }

  function pickMoney(
    o: Record<string, unknown>,
    keys: string[],
  ): number | undefined {
    for (const k of keys) {
      const v = o[k];
      if (typeof v === 'number' && Number.isFinite(v)) return v;
      if (typeof v === 'string') {
        const n = Number(v);
        if (Number.isFinite(n)) return n;
      }
    }
    return undefined;
  }

  function getPrestationWeightDays(p: PrestationDto): number {
    const o = p as unknown as Record<string, unknown>;
    const w = pickNumber(o, ['weight_days', 'days', 'effort_days']);
    return typeof w === 'number' && w > 0 ? w : 1;
  }

  function getPrestationName(p: PrestationDto): string {
    const o = p as unknown as Record<string, unknown>;
    return pickString(o, ['name', 'label', 'title']) ?? `Prestation #${p.id}`;
  }

  function getPrestationPrice(p: PrestationDto): number | undefined {
    const o = p as unknown as Record<string, unknown>;
    const cents = pickNumber(o, ['price_cents', 'default_rate_cents']);
    if (typeof cents === 'number') return cents / 100;

    const eur = pickMoney(o, ['default_rate_eur', 'price_eur', 'price']);
    if (typeof eur === 'number') return eur;

    return pickNumber(o, ['default_price', 'default_rate']);
  }

  function getPrestationTaxRate(p: PrestationDto): number | undefined {
    const o = p as unknown as Record<string, unknown>;
    return pickNumber(o, ['tax_rate', 'tax_rate_value', 'default_tax_rate']);
  }

  // Handle new client creation: refresh list + auto-select
  const handleClientCreated = async (newClient: ClientDto) => {
    try {
      const response = await clientRepository.list();
      setClients(response.results);
      setValue('client', String(newClient.id), {
        shouldValidate: true,
        shouldDirty: true,
      });
    } catch (e) {
      console.error('Erreur rafraîchissement clients', e);
    }
  };

  const onSubmit: SubmitHandler<FormData> = async (values) => {
    setLoading(true);
    try {
      const validUntil =
        values.valid_until && values.valid_until.length > 0
          ? values.valid_until
          : undefined;

      const payload: QuotePayload = {
        client: values.client,
        title: values.title,
        currency: values.currency,
        language: values.language,
        issue_date: values.issue_date,
        valid_until: validUntil ?? null,
        payment_terms_text: values.payment_terms_text ?? null,
        items: values.items.map((it) => ({
          prestation_id: it.prestation_id ?? undefined,
          description: it.description,
          qty: Number(it.qty),
          unit_price: Number(it.unit_price),
          tax_rate:
            it.tax_rate === undefined || it.tax_rate === null
              ? undefined
              : Number(it.tax_rate),
          discount:
            it.discount === undefined || it.discount === null
              ? 0.0
              : Number(it.discount),
          metadata: {},
        })),
      };

      const created = await quoteRepository.create(payload);
      console.log('Quote created', created);
      navigate('/dashboard', { replace: true });
    } catch (err: unknown) {
      console.error('Create quote error', err);
      if (isAxiosLikeError(err) && err.response?.data) {
        alert(
          'Impossible de créer le devis : ' +
            JSON.stringify(err.response.data, null, 2),
        );
      } else if (isAxiosLikeError(err) && err.message) {
        alert('Impossible de créer le devis : ' + err.message);
      } else {
        alert('Impossible de créer le devis : erreur inconnue');
      }
    } finally {
      setLoading(false);
    }
  };

  if (clients === 'loading' || prestations === 'loading') {
    return (
      <div className="container mx-auto py-6 px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="h-32 bg-muted/50 rounded-lg animate-pulse" />
        <div className="h-96 bg-muted/50 rounded-lg animate-pulse" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 px-4 sm:px-6 lg:px-8 space-y-6">
      {/* Header gradient avec actions */}
      <header className="flex flex-col sm:flex-row items-start justify-between gap-4 p-6 rounded-lg bg-[#e86c1d] from-brand to-accent-orange text-white shadow-lg">
        <div>
          <h1 className="text-2xl font-bold">Créer un nouveau devis</h1>
          <p className="text-sm opacity-95 mt-1">
            Remplissez les informations ci-dessous pour générer un devis.
          </p>
        </div>
        <div className="flex gap-2">
          <Button asChild variant="cancel" className="">
            <Link to="/dashboard">Annuler</Link>
          </Button>
          <Button
            type="button"
            variant="preview"
            onClick={() => setPreviewOpen(true)}
          >
            Aperçu
          </Button>
          <Button
            type="button"
            className=""
            variant="create"
            onClick={handleSubmit(onSubmit)}
            disabled={isSubmitting || loading}
          >
            {isSubmitting || loading ? 'Création…' : 'Créer le devis'}
          </Button>
        </div>
      </header>

      {/* Erreurs globales */}
      {(errors.client || errors.title || errors.items) && (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-sm text-destructive">
          <p className="font-semibold">⚠️ Erreurs de validation</p>
          <ul className="mt-2 space-y-1 text-sm">
            {errors.client && <li>{String(errors.client.message)}</li>}
            {errors.title && <li>{String(errors.title.message)}</li>}
            {errors.items && <li>{String(errors.items.message)}</li>}
          </ul>
        </div>
      )}

      <Form {...form}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Bloc Client */}
          <Card className="shadow-sm border border-border">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-semibold">Client</CardTitle>
                <Button
                  type="button"
                  className="btn-add-client hover:btn-add-client-hover h-8 text-xs px-3 flex items-center gap-2"
                  onClick={() => setClientDrawerOpen(true)}
                >
                  <PlusCircle className="h-3.5 w-3.5" />
                  Nouveau client
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <FormField
                control={control}
                name="client"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Client *</FormLabel>
                    <FormControl>
                      {clients === null ? (
                        <div className="rounded-lg border border-destructive bg-destructive/10 p-3 text-sm text-destructive">
                          Erreur lors du chargement des clients
                        </div>
                      ) : (
                        <Select
                          onValueChange={field.onChange}
                          defaultValue={field.value}
                        >
                          <SelectTrigger className="border-input focus:ring-2 focus:ring-brand/50 focus:border-brand transition-all">
                            <SelectValue placeholder="— Sélectionner un client —" />
                          </SelectTrigger>
                          <SelectContent>
                            {clients.map((c) => (
                              <SelectItem key={c.id} value={c.id}>
                                {c.name} {c.email ? `(${c.email})` : ''}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      )}
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Bloc Devis */}
          <Card className="shadow-sm border border-border">
            <CardHeader>
              <CardTitle>Informations du devis</CardTitle>
            </CardHeader>
            <CardContent className="grid md:grid-cols-2 gap-4">
              <FormField
                control={control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Titre *</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="Site vitrine 5 pages" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={control}
                name="currency"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Devise</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="EUR" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={control}
                name="language"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Langue</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="fr" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={control}
                name="issue_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Date d'émission *</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={control}
                name="valid_until"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Valable jusqu'au</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="md:col-span-2">
                <FormField
                  control={control}
                  name="payment_terms_text"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Conditions de paiement</FormLabel>
                      <FormControl>
                        <Textarea
                          {...field}
                          rows={3}
                          placeholder="Ex: Paiement à 30 jours fin de mois"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </CardContent>
          </Card>

          {/* Bloc Prestations */}
          <Card className="shadow-sm border border-border">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-semibold">
                  Prestations
                </CardTitle>
                <Button
                  type="button"
                  className="btn-add-item"
                  onClick={() =>
                    append({
                      description: 'Nouvelle prestation',
                      qty: 1,
                      unit_price: 0.0,
                      tax_rate: 20.0,
                      discount: 0.0,
                    })
                  }
                >
                  <PlusCircle className="mr-1.5 h-3.5 w-3.5" />
                  Ajouter
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {fields.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  Aucune prestation
                </div>
              ) : (
                <>
                  {fields.map((field, idx) => (
                    <Card key={field.id} className="border border-border/50">
                      <CardContent className="p-4 space-y-3">
                        {/* Row 1: Index + Select + Remove */}
                        <div className="flex items-center gap-3">
                          <Badge className="badge-index text-xs">
                            {idx + 1}
                          </Badge>

                          <FormField
                            control={control}
                            name={`items.${idx}.prestation_id`}
                            render={({ field: prestField }) => (
                              <FormItem className="flex-1">
                                <FormControl>
                                  {prestations === null ? (
                                    <div className="rounded-lg border border-destructive bg-destructive/10 p-2 text-sm text-destructive">
                                      Erreur chargement
                                    </div>
                                  ) : (
                                    <Select
                                      value={prestField.value?.toString() ?? ''}
                                      onValueChange={(val) => {
                                        const id = val
                                          ? Number(val)
                                          : undefined;
                                        prestField.onChange(id);
                                        setValue(
                                          `items.${idx}.prestation_id`,
                                          id,
                                          {
                                            shouldValidate: true,
                                            shouldDirty: true,
                                          },
                                        );

                                        if (!id) return;

                                        const p = prestations.find(
                                          (pp) => pp.id === id,
                                        );
                                        if (!p) return;

                                        const name = getPrestationName(p);
                                        const taxRate = getPrestationTaxRate(p);
                                        const weight =
                                          getPrestationWeightDays(p);

                                        const tjm = account?.default_rate_cents
                                          ? account.default_rate_cents / 100
                                          : undefined;
                                        const fallbackDayRate =
                                          getPrestationPrice(p);
                                        const dayRate =
                                          typeof tjm === 'number'
                                            ? tjm
                                            : typeof fallbackDayRate ===
                                                'number'
                                              ? fallbackDayRate
                                              : undefined;
                                        const unit =
                                          typeof dayRate === 'number'
                                            ? dayRate * weight
                                            : undefined;

                                        if (name)
                                          setValue(
                                            `items.${idx}.description`,
                                            name,
                                            {
                                              shouldDirty: true,
                                            },
                                          );
                                        if (typeof taxRate === 'number')
                                          setValue(
                                            `items.${idx}.tax_rate`,
                                            taxRate,
                                            {
                                              shouldDirty: true,
                                            },
                                          );
                                        if (typeof unit === 'number')
                                          setValue(
                                            `items.${idx}.unit_price`,
                                            unit,
                                            {
                                              shouldDirty: true,
                                            },
                                          );
                                      }}
                                    >
                                      <SelectTrigger className="focus:ring-brand/50 focus:border-brand">
                                        <SelectValue placeholder="— Choisir une prestation —" />
                                      </SelectTrigger>
                                      <SelectContent>
                                        {prestations.map((p) => (
                                          <SelectItem
                                            key={p.id}
                                            value={p.id.toString()}
                                          >
                                            {getPrestationName(p)}
                                          </SelectItem>
                                        ))}
                                      </SelectContent>
                                    </Select>
                                  )}
                                </FormControl>
                              </FormItem>
                            )}
                          />

                          {/* Bouton supprimer stylisé */}
                          <Button
                            type="button"
                            size="icon"
                            className="btn-remove-item" // Utilitaire personnalisé
                            onClick={() => remove(idx)}
                          >
                            <Trash2 className="h-4 w-4" />{' '}
                          </Button>
                        </div>

                        {/* Row 2: Description */}
                        <FormField
                          control={control}
                          name={`items.${idx}.description`}
                          render={({ field }) => (
                            <FormItem>
                              <FormControl>
                                <Input {...field} placeholder="Description" />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        {/* Row 3: Grid Qty, Prix, TVA, Remise */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                          <FormField
                            control={control}
                            name={`items.${idx}.qty`}
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel className="text-xs">
                                  Quantité
                                </FormLabel>
                                <FormControl>
                                  <Input
                                    type="number"
                                    step="0.01"
                                    {...field}
                                    onChange={(e) =>
                                      field.onChange(Number(e.target.value))
                                    }
                                  />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />

                          <FormField
                            control={control}
                            name={`items.${idx}.unit_price`}
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel className="text-xs">
                                  Prix HT
                                </FormLabel>
                                <FormControl>
                                  <div className="relative">
                                    <Input
                                      type="number"
                                      step="0.01"
                                      {...field}
                                      className="pr-8"
                                      onChange={(e) =>
                                        field.onChange(Number(e.target.value))
                                      }
                                    />
                                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">
                                      €
                                    </span>
                                  </div>
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />

                          <FormField
                            control={control}
                            name={`items.${idx}.tax_rate`}
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel className="text-xs">
                                  TVA (%)
                                </FormLabel>
                                <FormControl>
                                  <Input
                                    type="number"
                                    step="0.01"
                                    {...field}
                                    onChange={(e) => {
                                      const val = e.target.value;
                                      field.onChange(
                                        val === '' ? undefined : Number(val),
                                      );
                                    }}
                                  />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />

                          <FormField
                            control={control}
                            name={`items.${idx}.discount`}
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel className="text-xs">
                                  Remise (%)
                                </FormLabel>
                                <FormControl>
                                  <Input
                                    type="number"
                                    step="0.01"
                                    {...field}
                                    onChange={(e) => {
                                      const val = e.target.value;
                                      field.onChange(
                                        val === '' ? undefined : Number(val),
                                      );
                                    }}
                                  />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                        </div>
                      </CardContent>
                    </Card>
                  ))}

                  {/* Totaux */}
                  <div className="mt-4 p-4 rounded-lg bg-muted/50 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Sous-total HT</span>
                      <strong>{money.format(totals.sub)}</strong>
                    </div>

                    <div className="flex justify-between text-sm">
                      <span>TVA</span>
                      <strong>{money.format(totals.tax)}</strong>
                    </div>

                    <div className="flex justify-between pt-2 border-t border-border text-base font-semibold">
                      <span>Total TTC</span>
                      <strong>{money.format(totals.total)}</strong>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Actions bas de page */}
          <div className="flex items-center gap-2">
            <Button
              type="submit"
              className="bg-brand text-brand-foreground hover:bg-brand/90"
              disabled={isSubmitting || loading}
            >
              {isSubmitting || loading ? 'Création…' : 'Créer le devis'}
            </Button>
            <Button asChild variant="outline">
              <Link to="/dashboard">Annuler</Link>
            </Button>
          </div>
        </form>
      </Form>

      {/* Modal Preview PDF (garder existant) */}
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
                      `devis-${'preview'.replace(/\s+/g, '_')}.pdf`,
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

      {/* Client Drawer (garder existant) */}
      <ClientCreateDrawer
        open={clientDrawerOpen}
        onClose={() => setClientDrawerOpen(false)}
        onClientCreated={handleClientCreated}
      />
    </div>
  );
}
