// src/interface/components/profile/ProfessionalInfoForm.tsx
import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import type { AreaDto } from '../../../domain/catalog/types';

export const ProfessionalInfoSchema = z.object({
  name: z.string().optional().nullable(),
  status_juridique: z.string().optional().nullable(),
  domaine: z.number().nullable().optional(),
  tjm_eur: z.number().nonnegative().nullable().optional(),
  number_pro: z.string().optional().nullable(),
});

export type ProfessionalInfoValues = z.infer<typeof ProfessionalInfoSchema>;

type Props = {
  initialValues?: Partial<ProfessionalInfoValues & { tjm_cents?: number }>;
  areas?: AreaDto[] | null;
  onSave?: (payload: {
    name?: string | null;
    status_juridique?: string | null;
    domaine?: number | null;
    tjm_cents?: number | null;
    number_pro?: string | null;
  }) => Promise<void> | void;
  onDomaineChange?: (domaine: number | null) => void;
  onValuesChange?: (values: ProfessionalInfoValues) => void;
  onCancel?: () => void;
  submitLabel?: string;
};

export default function ProfessionalInfoForm({
  initialValues = {},
  areas = null,
  onSave,
  onDomaineChange,
  onValuesChange,
}: Props) {
  const init = initialValues ?? {};

  const { register, handleSubmit, watch } = useForm<ProfessionalInfoValues>({
    resolver: zodResolver(ProfessionalInfoSchema),
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
    },
  });

  // watch values to notify parent
  const watchedAll = watch();

  useEffect(() => {
    // notify parent of full values draft
    if (onValuesChange) {
      onValuesChange(watchedAll);
    }

    // also notify domaine change separately (keeps previous behavior)
    if (onDomaineChange) {
      // domaine peut être string | number | null | undefined selon le navigateur / register options
      const raw: unknown = watchedAll.domaine;

      let parsed: number | null = null;
      if (raw == null) {
        parsed = null;
      } else if (typeof raw === 'number') {
        parsed = raw;
      } else if (typeof raw === 'string') {
        // empty string -> null, otherwise try to parse number
        if (raw === '') {
          parsed = null;
        } else {
          const n = Number(raw);
          parsed = Number.isNaN(n) ? null : n;
        }
      } else {
        // valeur inattendue -> null
        parsed = null;
      }

      onDomaineChange(parsed);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    watchedAll.name,
    watchedAll.status_juridique,
    watchedAll.domaine,
    watchedAll.tjm_eur,
    watchedAll.number_pro,
  ]);
  async function internalOnSubmit(values: ProfessionalInfoValues) {
    const payload: {
      name?: string | null;
      status_juridique?: string | null;
      domaine?: number | null;
      tjm_cents?: number | null;
      number_pro?: string | null;
    } = {
      name: values.name ?? null,
      status_juridique: values.status_juridique ?? null,
      domaine: values.domaine ?? null,
      number_pro: values.number_pro ?? null,
    };

    if (typeof values.tjm_eur === 'number')
      payload.tjm_cents = Math.round(values.tjm_eur * 100);
    else payload.tjm_cents = null;

    if (onSave) await onSave(payload);
  }

  return (
    <form onSubmit={handleSubmit(internalOnSubmit)} className="grid gap-4">
      <label className="block">
        <div className="text-sm font-medium text-gray-700 mb-1">Nom structure</div>
        <input
          {...register('name')}
          className="w-full px-3.5 py-2.5 border border-gray-300 rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Nom de votre structure"
        />
      </label>

      <label className="block">
        <div className="text-sm font-medium text-gray-700 mb-1">Statut juridique</div>
        <input
          {...register('status_juridique')}
          className="w-full px-3.5 py-2.5 border border-gray-300 rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ex: micro, eurl, sasu..."
        />
      </label>

      <label className="block">
        <div className="text-sm font-medium text-gray-700 mb-1">Domaine</div>
        <select
          {...register('domaine')}
          className="w-full px-3.5 py-2.5 border border-gray-300 rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white cursor-pointer"
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

      <label className="block">
        <div className="text-sm font-medium text-gray-700 mb-1">TJM (EUR)</div>
        <input
          type="number"
          step="0.01"
          {...register('tjm_eur', { valueAsNumber: true })}
          className="w-full px-3.5 py-2.5 border border-gray-300 rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Ex: 450.00"
        />
      </label>

      <label className="block">
        <div className="text-sm font-medium text-gray-700 mb-1">Numéro pro (SIRET / TVA)</div>
        <input
          {...register('number_pro')}
          className="w-full px-3.5 py-2.5 border border-gray-300 rounded-xl text-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </label>
    </form>
  );
}
