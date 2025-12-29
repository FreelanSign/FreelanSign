// src/interface/components/account/AccountDataForm.tsx
import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useRef, useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import type { AreaDto } from '../../../domain/catalog/types';

import { Button } from '@/components/ui/button';
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

export const AccountSchema = z.object({
  display_name: z.string().optional().nullable(),
  legal_form: z.string().optional().nullable(),
  domain_id: z.number().nullable().optional(),
  tjm_eur: z.number().nonnegative().nullable().optional(),
  legal_id: z.string().optional().nullable(),
  service_types: z.array(z.number()).optional().nullable(),
});

export type AccountFormValues = z.infer<typeof AccountSchema>;

function normalizeToNumberArray(value: unknown): number[] {
  if (!value) return [];
  if (!Array.isArray(value)) return [];

  return value
    .map((v) => {
      if (v == null) return NaN;
      if (typeof v === 'number') return v;
      if (typeof v === 'string') {
        const n = Number(v);
        return Number.isNaN(n) ? NaN : n;
      }
      if (typeof v === 'object' && v !== null && 'id' in v) {
        const maybe = (v as Record<string, unknown>)['id'];
        if (typeof maybe === 'number') return maybe;
        const n = Number(String(maybe));
        return Number.isNaN(n) ? NaN : n;
      }
      return NaN;
    })
    .filter((n) => !Number.isNaN(n));
}

type Props = {
  initialValues?: Partial<AccountFormValues & { default_rate_cents?: number }>;
  areas?: AreaDto[] | null;
  onSave?: (payload: {
    display_name?: string | null;
    legal_form?: string | null;
    domain_id?: number | null;
    default_rate_cents?: number | null;
    legal_id?: string | null;
    service_types?: number[] | null;
  }) => Promise<void> | void;
  onDomainChange?: (domain_id: number | null) => void;
  onChange?: (values: AccountFormValues) => void;
  onCancel?: () => void;
  submitLabel?: string;
  showButtons?: boolean;
};

export default function AccountDataForm({
  initialValues = {},
  areas = null,
  onSave,
  onDomainChange,
  onChange,
  onCancel,
  submitLabel = 'Enregistrer',
  showButtons = false,
}: Props) {
  const init: Partial<AccountFormValues & { default_rate_cents?: number }> =
    initialValues ?? {};

  const form = useForm<AccountFormValues>({
    resolver: zodResolver(AccountSchema),
    defaultValues: {
      display_name: init.display_name ?? null,
      legal_form: init.legal_form ?? null,
      domain_id:
        typeof init.domain_id === 'number'
          ? init.domain_id
          : (init.domain_id ?? null),
      tjm_eur:
        typeof init.default_rate_cents === 'number'
          ? init.default_rate_cents / 100
          : (init.tjm_eur ?? null),
      legal_id: init.legal_id ?? null,
      service_types: normalizeToNumberArray(init.service_types),
    },
  });

  const { control, handleSubmit, watch, reset, formState } = form;
  const [submitError, setSubmitError] = useState<string | null>(null);
  const isSubmitting = formState.isSubmitting;

  // watch domain_id and notify parent on change (immediate)
  const domainIdWatched = watch('domain_id');

  useEffect(() => {
    if (!onDomainChange) return;
    const raw: unknown = domainIdWatched;

    let parsed: number | null;
    if (raw == null) {
      parsed = null;
    } else if (typeof raw === 'number') {
      parsed = Number.isNaN(raw) ? null : raw;
    } else if (typeof raw === 'string') {
      if (raw.trim() === '') {
        parsed = null;
      } else {
        const n = Number(raw);
        parsed = Number.isNaN(n) ? null : n;
      }
    } else {
      parsed = null;
    }

    onDomainChange(parsed);
  }, [domainIdWatched, onDomainChange]);

  // watch whole form and notify parent on changes (draft)
  const watched = watch();
  const watchedStr = JSON.stringify(watched);
  const lastWatchedStr = useRef(watchedStr);

  useEffect(() => {
    if (onChange && watchedStr !== lastWatchedStr.current) {
      lastWatchedStr.current = watchedStr;
      onChange(watched as AccountFormValues);
    }
  }, [watchedStr, watched, onChange]);

  async function internalOnSubmit(values: AccountFormValues) {
    setSubmitError(null);
    try {
      const payload: {
        display_name?: string | null;
        legal_form?: string | null;
        domain_id?: number | null;
        default_rate_cents?: number | null;
        legal_id?: string | null;
        service_types?: number[] | null;
      } = {
        display_name: values.display_name ?? null,
        legal_form: values.legal_form ?? null,
        domain_id: values.domain_id ?? null,
        legal_id: values.legal_id ?? null,
      };

      if (typeof values.tjm_eur === 'number') {
        payload.default_rate_cents = Math.round(values.tjm_eur * 100);
      } else {
        payload.default_rate_cents = null;
      }

      payload.service_types = normalizeToNumberArray(values.service_types);

      if (onSave) {
        await onSave(payload);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : JSON.stringify(err);
      setSubmitError(msg);
      throw err;
    }
  }

  return (
    <Form {...form}>
      <form
        onSubmit={handleSubmit(internalOnSubmit)}
        className="grid gap-4"
        noValidate
      >
        <FormField
          control={control}
          name="display_name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nom structure</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  value={field.value ?? ''}
                  placeholder="Nom de votre structure"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={control}
          name="legal_form"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Statut juridique</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  value={field.value ?? ''}
                  placeholder="Ex: micro, eurl, sasu..."
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={control}
          name="domain_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Domaine</FormLabel>
              <Select
                onValueChange={(val) =>
                  field.onChange(val ? Number(val) : null)
                }
                value={field.value ? String(field.value) : ''}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="-- Aucune --" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="null">-- Aucune --</SelectItem>
                  {Array.isArray(areas) &&
                    areas.map((a) => (
                      <SelectItem key={a.id} value={String(a.id)}>
                        {a.name ?? a.slug ?? `Area ${a.id}`}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FormField
            control={control}
            name="tjm_eur"
            render={({ field }) => (
              <FormItem>
                <FormLabel>TJM (EUR)</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    step="0.01"
                    {...field}
                    value={field.value ?? ''}
                    onChange={(e) =>
                      field.onChange(
                        e.target.value === '' ? null : Number(e.target.value),
                      )
                    }
                    placeholder="Ex: 450.00"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={control}
            name="legal_id"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Numéro pro (SIRET / TVA)</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    value={field.value ?? ''}
                    placeholder="Ex: 123 456 789 00012"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {submitError && (
          <p className="text-sm text-destructive mt-1">Erreur: {submitError}</p>
        )}

        {showButtons && (
          <div className="flex gap-3 mt-2">
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'En cours…' : submitLabel}
            </Button>

            <Button
              type="button"
              variant="outline"
              onClick={() => onCancel && onCancel()}
            >
              Annuler
            </Button>

            <Button
              type="button"
              variant="ghost"
              onClick={() =>
                reset({
                  display_name: init.display_name ?? null,
                  legal_form: init.legal_form ?? null,
                  domain_id: init.domain_id ?? null,
                  tjm_eur:
                    typeof init.default_rate_cents === 'number'
                      ? init.default_rate_cents / 100
                      : (init.tjm_eur ?? null),
                  legal_id: init.legal_id ?? null,
                  service_types: normalizeToNumberArray(init.service_types),
                })
              }
            >
              Réinitialiser
            </Button>
          </div>
        )}
      </form>
    </Form>
  );
}
