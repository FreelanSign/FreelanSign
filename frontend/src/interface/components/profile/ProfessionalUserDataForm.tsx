// src/interface/components/profile/ProfessionalUserDataForm.tsx
import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import type { AreaDto } from '../../../domain/catalog/types';

export const ProfessionalUserSchema = z.object({
  name: z.string().optional().nullable(),
  status_juridique: z.string().optional().nullable(),
  domaine: z.number().nullable().optional(),
  tjm_eur: z.number().nonnegative().nullable().optional(),
  number_pro: z.string().optional().nullable(),
  service_types: z.array(z.number()).optional().nullable(),
});

export type ProfessionalUserFormValues = z.infer<typeof ProfessionalUserSchema>;

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
  initialValues?: Partial<ProfessionalUserFormValues & { tjm_cents?: number }>;
  areas?: AreaDto[] | null;
  onSave?: (payload: {
    name?: string | null;
    status_juridique?: string | null;
    domaine?: number | null;
    tjm_cents?: number | null;
    number_pro?: string | null;
    service_types?: number[] | null;
  }) => Promise<void> | void;
  onDomaineChange?: (domaine: number | null) => void;
  onChange?: (values: ProfessionalUserFormValues) => void; // NEW
  onCancel?: () => void;
  submitLabel?: string;
  showButtons?: boolean;
};

export default function ProfessionalUserDataForm({
  initialValues = {},
  areas = null,
  onSave,
  onDomaineChange,
  onChange,
  onCancel,
  submitLabel = 'Enregistrer',
  showButtons = false, // parent handles save
}: Props) {
  const init: Partial<ProfessionalUserFormValues & { tjm_cents?: number }> =
    initialValues ?? {};

  const { register, handleSubmit, formState, reset, watch } =
    useForm<ProfessionalUserFormValues>({
      resolver: zodResolver(ProfessionalUserSchema),
      defaultValues: {
        name: init.name ?? null,
        status_juridique: init.status_juridique ?? null,
        domaine:
          typeof init.domaine === 'number'
            ? init.domaine
            : (init.domaine ?? null),
        tjm_eur:
          typeof init.tjm_cents === 'number'
            ? init.tjm_cents / 100
            : (init.tjm_eur ?? null),
        number_pro: init.number_pro ?? null,
        service_types: normalizeToNumberArray(init.service_types),
      },
    });

  const [submitError, setSubmitError] = useState<string | null>(null);
  const isSubmitting = formState.isSubmitting;

  // watch domaine and notify parent immediately (same behaviour as before)
  const domaineWatched = watch('domaine');
  useEffect(() => {
    if (onDomaineChange) {
      const d =
        domaineWatched === '' || domaineWatched == null
          ? null
          : Number(domaineWatched);
      onDomaineChange(Number.isNaN(d) ? null : d);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [domaineWatched]);

  // watch whole form and notify parent on changes (draft)
  const watched = watch();
  useEffect(() => {
    if (onChange) onChange(watched as ProfessionalUserFormValues);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(watched)]);

  async function internalOnSubmit(values: ProfessionalUserFormValues) {
    setSubmitError(null);
    try {
      const payload: {
        name?: string | null;
        status_juridique?: string | null;
        domaine?: number | null;
        tjm_cents?: number | null;
        number_pro?: string | null;
        service_types?: number[] | null;
      } = {
        name: values.name ?? null,
        status_juridique: values.status_juridique ?? null,
        domaine: values.domaine ?? null,
        number_pro: values.number_pro ?? null,
      };

      if (typeof values.tjm_eur === 'number') {
        payload.tjm_cents = Math.round(values.tjm_eur * 100);
      } else {
        payload.tjm_cents = null;
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
          {...register('name')}
          className="border p-2 rounded w-full"
          placeholder="Nom de votre structure"
        />
      </label>

      <label>
        <div className="text-sm">Statut juridique</div>
        <input
          {...register('status_juridique')}
          className="border p-2 rounded w-full"
          placeholder="Ex: micro, eurl, sasu..."
        />
      </label>

      <label>
        <div className="text-sm">Domaine</div>
        <select {...register('domaine')} className="border p-2 rounded w-full">
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
          {...register('number_pro')}
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
                name: init.name ?? null,
                status_juridique: init.status_juridique ?? null,
                domaine: init.domaine ?? null,
                tjm_eur:
                  typeof init.tjm_cents === 'number'
                    ? init.tjm_cents / 100
                    : (init.tjm_eur ?? null),
                number_pro: init.number_pro ?? null,
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
