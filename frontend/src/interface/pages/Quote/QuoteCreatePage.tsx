// src/interface/pages/QuoteCreatePage.tsx
import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useMemo, useState } from 'react';
import {
  useFieldArray,
  useForm,
  useWatch,
  type FieldPath,
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

import { Skeleton } from '@/components/ui/skeleton';
import {
  Briefcase,
  ChevronLeft,
  Eye,
  FileText,
  List,
  PlusCircle,
  Trash2,
  User,
} from 'lucide-react';
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
  description: z.preprocess(
    (val) => (val === undefined || val === null ? '' : val),
    z.string().min(1, 'La désignation de la prestation est requise'),
  ),
  details: z.string().optional().default(''),
  qty: z.number().positive('La quantité doit être supérieure à 0'),
  unit_price: z
    .number()
    .nonnegative('Le prix unitaire doit être positif ou nul'),
  tax_rate: z.number().min(0).max(100).optional(),
  discount: z.number().nonnegative().optional(),
});

const Schema = z.object({
  client: z.preprocess(
    (val) => (val === undefined || val === null ? '' : val),
    z.string().min(1, 'Veuillez sélectionner un client'),
  ),
  title: z.preprocess(
    (val) => (val === undefined || val === null ? '' : val),
    z.string().min(1, 'Le titre du devis est requis'),
  ),
  currency: z.string().length(3).default('EUR'),
  language: z.string().min(2).max(8).default('fr'),
  issue_date: z.preprocess(
    (val) => (val === undefined || val === null ? '' : val),
    z.string().min(8, "La date d'émission est requise"),
  ),
  valid_until: z.string().optional().or(z.literal('')),
  payment_terms_text: z.string().optional().default(''),
  items: z
    .array(ItemSchema)
    .min(1, 'Ajoutez au moins une prestation à votre devis'),
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

const FIELD_LABELS: Record<string, string> = {
  client: 'Client',
  title: 'Titre du devis',
  issue_date: "Date d'émission",
  valid_until: "Valable jusqu'au",
  items: 'Prestations',
  payment_terms_text: 'Conditions de paiement',
  currency: 'Devise',
  language: 'Langue',
};

/* ---------- component ---------- */
export default function QuoteCreatePage() {
  const [previewOpen, setPreviewOpen] = useState(false);
  const [clientDrawerOpen, setClientDrawerOpen] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);
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
          details: '',
          qty: 1,
          unit_price: 0.0,
          tax_rate: 20.0,
          discount: 0.0,
        },
      ],
      payment_terms_text: '',
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
    if (!values.items || values.items.length === 0) {
      setServerError('Le devis doit contenir au moins une prestation.');
      return;
    }

    // Vérification : au moins une prestation doit être modifiée (pas juste la prestation par défaut à 0€)
    const hasModifiedItem = values.items.some(
      (it) =>
        it.unit_price > 0 ||
        it.description !== 'Nouvelle prestation' ||
        it.prestation_id,
    );

    if (!hasModifiedItem) {
      setServerError(
        'Veuillez modifier au moins une prestation (nom ou prix) avant de créer le devis.',
      );
      return;
    }

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
        payment_terms_text: values.payment_terms_text || '',
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
          metadata: { details: it.details || null },
        })),
      };

      const created = await quoteRepository.create(payload);
      console.log('Quote created', created);
      navigate('/dashboard', { replace: true });
    } catch (err: unknown) {
      console.error('Create quote error', err);
      if (isAxiosLikeError(err) && err.response?.data) {
        const data = err.response.data as Record<string, unknown>;
        if (typeof data === 'object' && !Array.isArray(data)) {
          Object.entries(data).forEach(([key, value]) => {
            const message = Array.isArray(value)
              ? value.join(' ')
              : String(value);

            if (key === 'detail' || key === 'non_field_errors') {
              setServerError(message);
            } else {
              form.setError(key as FieldPath<FormData>, {
                type: 'server',
                message: message,
              });
            }
          });
        } else {
          setServerError(JSON.stringify(data));
        }
      } else if (isAxiosLikeError(err) && err.message) {
        setServerError(err.message);
      } else {
        setServerError(
          'Une erreur inconnue est survenue lors de la création du devis.',
        );
      }
    } finally {
      setLoading(false);
    }
  };

  if (clients === 'loading' || prestations === 'loading') {
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
          <Link
            to="/dashboard"
            className="flex items-center text-xs font-bold uppercase tracking-widest text-muted-foreground hover:text-brand transition-colors mb-2 group"
          >
            <ChevronLeft className="mr-1 h-3 w-3 transition-transform group-hover:-translate-x-0.5" />
            Retour au tableau de bord
          </Link>
          <h1 className="text-3xl font-bold tracking-tight font-playfair">
            Créer un nouveau devis
          </h1>
          <p className="text-muted-foreground">
            Remplissez les informations ci-dessous pour générer un nouveau devis
            professionnel.
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
            Aperçu
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-9 px-4 font-bold text-xs uppercase tracking-wider"
            asChild
          >
            <Link to="/dashboard">Annuler</Link>
          </Button>
          <Button
            type="button"
            className="h-9 px-6 bg-brand text-white hover:bg-brand-dark shadow-sm font-bold text-xs uppercase tracking-wider"
            onClick={handleSubmit(onSubmit)}
            disabled={isSubmitting || loading}
          >
            {isSubmitting || loading ? (
              'Création…'
            ) : (
              <>
                <PlusCircle className="mr-2 h-4 w-4" />
                Créer le devis
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Erreurs globales */}
      {(Object.keys(errors).length > 0 || serverError) && (
        <div className="rounded-lg border-l-4 border-amber-500 bg-amber-50 p-4 text-sm shadow-sm">
          <div className="flex items-start gap-3">
            <svg
              className="h-5 w-5 text-amber-600 shrink-0 mt-0.5"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
            <div className="flex-1">
              <p className="font-semibold text-amber-800">
                {serverError
                  ? 'Une erreur est survenue'
                  : 'Quelques informations sont manquantes'}
              </p>
              {serverError ? (
                <p className="mt-1 text-amber-700">{serverError}</p>
              ) : (
                <>
                  <p className="mt-1 text-amber-700">
                    Complétez les champs ci-dessous pour créer votre devis :
                  </p>
                  <ul className="mt-2 space-y-1 text-amber-700 list-disc list-inside">
                    {Object.entries(errors).map(([key, error]) => {
                      const label = FIELD_LABELS[key] || key;
                      // Pour les FieldArrays, l'erreur peut être sur 'root' ou être un message direct
                      const errorObj = error as {
                        message?: string;
                        root?: { message?: string };
                      };
                      let message = errorObj?.message;

                      // Cas spécifique de l'erreur min(1) de Zod sur un tableau
                      if (!message && errorObj?.root?.message) {
                        message = errorObj.root.message;
                      }

                      // Si c'est un tableau (erreurs sur les items individuels) et qu'on n'a pas de message global
                      if (!message && key === 'items' && Array.isArray(error)) {
                        message =
                          'Veuillez vérifier les informations des prestations';
                      }

                      return (
                        <li key={key}>
                          <span className="font-semibold">{label}</span>
                          {message ? ` : ${message}` : ''}
                        </li>
                      );
                    })}
                  </ul>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      <Form {...form}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Bloc Client */}
          <Card className="shadow-none border border-border bg-white">
            <CardHeader className="border-b border-border/50 bg-muted/20 pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-md bg-brand/10 text-brand">
                    <User size={18} />
                  </div>
                  <div>
                    <CardTitle className="text-lg font-semibold">
                      Client
                    </CardTitle>
                    <p className="text-xs text-muted-foreground">
                      Sélectionnez le destinataire du devis
                    </p>
                  </div>
                </div>
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
          <Card className="shadow-none border border-border bg-white">
            <CardHeader className="border-b border-border/50 bg-muted/20">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-md bg-brand/10 text-brand">
                  <FileText size={18} />
                </div>
                <div>
                  <CardTitle className="text-lg font-semibold">
                    Informations du devis
                  </CardTitle>
                  <p className="text-xs text-muted-foreground">
                    Détails généraux et dates clés
                  </p>
                </div>
              </div>
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
          <Card className="shadow-none border border-border bg-white overflow-hidden">
            <CardHeader className="border-b border-border/50 bg-muted/20 flex flex-row items-center justify-between py-4">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-md bg-brand/10 text-brand">
                  <List size={18} />
                </div>
                <div>
                  <CardTitle className="text-lg font-semibold leading-none">
                    Prestations
                  </CardTitle>
                  <p className="text-xs text-muted-foreground mt-1">
                    Détaillez les services ou produits proposés
                  </p>
                </div>
              </div>
              <Button
                type="button"
                className="bg-brand text-white hover:bg-brand-dark h-8 text-xs font-bold"
                onClick={() =>
                  append({
                    description: 'Nouvelle prestation',
                    details: '',
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
            </CardHeader>
            <CardContent className="space-y-3">
              {fields.length === 0 ? (
                <div className="text-center py-12">
                  <Briefcase className="mx-auto h-12 w-12 text-muted-foreground/20 mb-4" />
                  <p className="text-muted-foreground text-sm font-medium">
                    Votre devis ne contient aucune ligne de prestation.
                  </p>
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
                                        // Pre-fill details from prestation description
                                        const prestationDesc =
                                          p.description ||
                                          p.short_description ||
                                          '';
                                        if (prestationDesc)
                                          setValue(
                                            `items.${idx}.details`,
                                            prestationDesc,
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

                        {/* Row 2: Désignation */}
                        <FormField
                          control={control}
                          name={`items.${idx}.description`}
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel className="text-xs text-muted-foreground">
                                Désignation
                              </FormLabel>
                              <FormControl>
                                <Input
                                  {...field}
                                  placeholder="Nom du service ou produit"
                                  className="font-semibold"
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        {/* Row 3: Détails */}
                        <FormField
                          control={control}
                          name={`items.${idx}.details`}
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel className="text-xs text-muted-foreground">
                                Détails{' '}
                                <span className="font-normal text-muted-foreground/60">
                                  (optionnel)
                                </span>
                              </FormLabel>
                              <FormControl>
                                <Textarea
                                  {...field}
                                  placeholder="Détaillez ici les spécificités de cette prestation pour ce client..."
                                  className="min-h-[60px] resize-y text-sm"
                                  rows={2}
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        {/* Row 4: Grid Qty, Prix, TVA, Remise */}
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
          <div className="flex items-center justify-end gap-3 pt-6 border-t border-border/60">
            <Button
              asChild
              variant="ghost"
              className="font-bold text-xs uppercase tracking-wider h-10 px-6"
            >
              <Link to="/dashboard">Annuler</Link>
            </Button>
            <Button
              type="submit"
              className="bg-brand text-white hover:bg-brand-dark shadow-md font-bold text-xs uppercase tracking-wider h-10 px-8"
              disabled={isSubmitting || loading}
            >
              {isSubmitting || loading ? (
                'Création…'
              ) : (
                <>
                  <PlusCircle className="mr-2 h-4 w-4" />
                  Créer le devis
                </>
              )}
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
