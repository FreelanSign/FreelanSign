// src/interface/components/profile/PersonalUserDataForm.tsx
import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

export const PersonalUserSchema = z.object({
  first_name: z.string().optional().nullable(),
  last_name: z.string().optional().nullable(),
  phone: z.string().optional().nullable(),
  birthday: z.string().optional().nullable(), // YYYY-MM-DD
  avatar_url: z.string().url().optional().nullable(),
});

export type PersonalUserFormValues = z.infer<typeof PersonalUserSchema>;

type Props = {
  initialValues?: Partial<PersonalUserFormValues>;
  onSave?: (values: PersonalUserFormValues) => Promise<void> | void;
  onCancel?: () => void;
  onChange?: (values: PersonalUserFormValues) => void; // NEW
  submitLabel?: string;
  showButtons?: boolean; // if false, component will not render Save/Cancel (useful if parent handles submit)
};

export default function PersonalUserDataForm({
  initialValues = {},
  onSave,
  onCancel,
  onChange,
  submitLabel = 'Enregistrer',
  showButtons = false, // parent will handle save
}: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<PersonalUserFormValues>({
    resolver: zodResolver(PersonalUserSchema),
    defaultValues: {
      first_name: initialValues.first_name ?? null,
      last_name: initialValues.last_name ?? null,
      phone: initialValues.phone ?? null,
      birthday: initialValues.birthday ?? null,
      avatar_url: initialValues.avatar_url ?? null,
    },
  });

  const [submitError, setSubmitError] = useState<string | null>(null);

  // notify parent on every change
  const watched = watch();
  useEffect(() => {
    if (onChange) onChange(watched as PersonalUserFormValues);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(watched)]);

  async function onSubmit(values: PersonalUserFormValues) {
    setSubmitError(null);
    try {
      if (onSave) {
        await onSave(values);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : JSON.stringify(err);
      setSubmitError(msg);
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="grid gap-3" noValidate>
      <label>
        <div className="text-sm">Prénom</div>
        <input
          {...register('first_name')}
          className={`border p-2 rounded w-full ${errors.first_name ? 'border-red-500' : ''}`}
        />
        {errors.first_name && (
          <p className="text-xs text-red-600 mt-1">
            {String(errors.first_name.message)}
          </p>
        )}
      </label>

      <label>
        <div className="text-sm">Nom</div>
        <input
          {...register('last_name')}
          className={`border p-2 rounded w-full ${errors.last_name ? 'border-red-500' : ''}`}
        />
        {errors.last_name && (
          <p className="text-xs text-red-600 mt-1">
            {String(errors.last_name.message)}
          </p>
        )}
      </label>

      <label>
        <div className="text-sm">Téléphone</div>
        <input
          {...register('phone')}
          className={`border p-2 rounded w-full ${errors.phone ? 'border-red-500' : ''}`}
        />
        {errors.phone && (
          <p className="text-xs text-red-600 mt-1">
            {String(errors.phone.message)}
          </p>
        )}
      </label>

      <label>
        <div className="text-sm">Date de naissance</div>
        <input
          {...register('birthday')}
          type="date"
          className={`border p-2 rounded w-full ${errors.birthday ? 'border-red-500' : ''}`}
        />
        {errors.birthday && (
          <p className="text-xs text-red-600 mt-1">
            {String(errors.birthday.message)}
          </p>
        )}
      </label>

      <label>
        <div className="text-sm">Avatar (URL)</div>
        <input
          {...register('avatar_url')}
          className={`border p-2 rounded w-full ${errors.avatar_url ? 'border-red-500' : ''}`}
        />
        {errors.avatar_url && (
          <p className="text-xs text-red-600 mt-1">
            {String(errors.avatar_url.message)}
          </p>
        )}
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
        </div>
      )}
    </form>
  );
}
