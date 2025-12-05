// src/interface/components/account/AccountDataForm.tsx
import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import type { AreaDto } from '../../../domain/catalog/types';

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

  const { register, handleSubmit, formState, reset, watch } =
    useForm<AccountFormValues>({
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
      // empty string -> null, otherwise parse to number (fallback to null if NaN)
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [domainIdWatched]);

  // watch whole form and notify parent on changes (draft)
  const watched = watch();
  useEffect(() => {
    if (onChange) onChange(watched as AccountFormValues);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(watched)]);

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
    <form
      onSubmit={handleSubmit(internalOnSubmit)}
      className="grid gap-3"
      noValidate
    >
      <label>
        <div className="text-sm">Nom structure</div>
        <input
          {...register('display_name')}
          className="border p-2 rounded w-full"
          placeholder="Nom de votre structure"
        />
      </label>

      <label>
        <div className="text-sm">Statut juridique</div>
        <input
          {...register('legal_form')}
          className="border p-2 rounded w-full"
          placeholder="Ex: micro, eurl, sasu..."
        />
      </label>

      <label>
        <div className="text-sm">Domaine</div>
        <select
          {...register('domain_id', {
            setValueAs: (v) => {
              if (v === '' || v === null || v === undefined) return null;
              const n = Number(v);
              return Number.isNaN(n) ? null : n;
            },
          })}
          className="border p-2 rounded w-full"
        >
          <option value="">-- Aucune --</option>
          {Array.isArray(areas) && areas.length > 0 ? (
            areas.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name ?? a.slug ?? `Area ${a.id}`}
              </option>
            ))
          ) : (
            <option value="">
              {areas == null
                ? 'Chargement impossible'
                : 'Aucune area disponible'}
            </option>
          )}
        </select>
      </label>

      <label>
        <div className="text-sm">TJM (EUR)</div>
        <input
          type="number"
          step="0.01"
          {...register('tjm_eur', { valueAsNumber: true })}
          className="border p-2 rounded w-full"
          placeholder="Ex: 450.00"
        />
      </label>

      <label>
        <div className="text-sm">Numéro pro (SIRET / TVA)</div>
        <input
          {...register('legal_id')}
          className="border p-2 rounded w-full"
        />
      </label>

      {submitError && (
        <p className="text-sm text-red-600 mt-1">Erreur: {submitError}</p>
      )}

      {showButtons && (
        <div className="flex gap-3 mt-2">
          <button
            type="submit"
            disabled={isSubmitting}
            className="bg-blue-600 text-white rounded px-3 py-2 disabled:opacity-50"
          >
            {isSubmitting ? 'En cours…' : submitLabel}
          </button>

          <button
            type="button"
            onClick={() => onCancel && onCancel()}
            className="bg-gray-200 rounded px-3 py-2"
          >
            Annuler
          </button>

          <button
            type="button"
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
            className="bg-white border rounded px-3 py-2"
          >
            Réinitialiser
          </button>
        </div>
      )}
    </form>
  );
}
