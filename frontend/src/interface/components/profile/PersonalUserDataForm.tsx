// src/interface/components/profile/PersonalUserDataForm.tsx
import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

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
import AvatarUpload from './AvatarUpload';

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
  onChange?: (values: PersonalUserFormValues) => void;
  submitLabel?: string;
  showButtons?: boolean;
};

export default function PersonalUserDataForm({
  initialValues = {},
  onSave,
  onCancel,
  onChange,
  submitLabel = 'Enregistrer',
  showButtons = false,
}: Props) {
  const form = useForm<PersonalUserFormValues>({
    resolver: zodResolver(PersonalUserSchema),
    defaultValues: {
      first_name: initialValues.first_name ?? null,
      last_name: initialValues.last_name ?? null,
      phone: initialValues.phone ?? null,
      birthday: initialValues.birthday ?? null,
      avatar_url: initialValues.avatar_url ?? null,
    },
  });

  const {
    control,
    handleSubmit,
    watch,
    formState: { isSubmitting },
  } = form;

  // notify parent on every change
  const watched = watch();
  const watchedStr = JSON.stringify(watched);
  const lastWatchedStr = useRef(watchedStr);

  useEffect(() => {
    if (onChange && watchedStr !== lastWatchedStr.current) {
      lastWatchedStr.current = watchedStr;
      onChange(watched as PersonalUserFormValues);
    }
  }, [watchedStr, watched, onChange]);

  async function onSubmit(values: PersonalUserFormValues) {
    if (onSave) {
      await onSave(values);
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FormField
            control={control}
            name="first_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Prénom</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    value={field.value ?? ''}
                    placeholder="Votre prénom"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={control}
            name="last_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Nom</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    value={field.value ?? ''}
                    placeholder="Votre nom"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FormField
            control={control}
            name="phone"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Téléphone</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    value={field.value ?? ''}
                    placeholder="Ex: 06 12 34 56 78"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={control}
            name="birthday"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Date de naissance</FormLabel>
                <FormControl>
                  <Input type="date" {...field} value={field.value ?? ''} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={control}
          name="avatar_url"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Avatar</FormLabel>
              <FormControl>
                <AvatarUpload
                  currentAvatarUrl={field.value}
                  onUploadSuccess={(newUrl) => field.onChange(newUrl)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {showButtons && (
          <div className="flex gap-3 mt-4">
            <Button
              type="submit"
              disabled={isSubmitting}
              className="bg-brand text-brand-foreground hover:bg-brand/90"
            >
              {isSubmitting ? 'En cours…' : submitLabel}
            </Button>

            <Button
              type="button"
              variant="outline"
              onClick={() => onCancel && onCancel()}
            >
              Annuler
            </Button>
          </div>
        )}
      </form>
    </Form>
  );
}
