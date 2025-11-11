// frontend/components/auth/ResetPasswordForm.tsx

import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { resetPassword } from '../../../lib/api/auth';
import styles from './reset-password-form.module.css';

const schema = z.object({
  token: z.string().min(1),
  new_password: z
    .string()
    .min(6, 'Le mot de passe doit contenir au moins 6 caractères'),
});

type FormData = z.infer<typeof schema>;

interface Props {
  token: string;
}

export default function ResetPasswordForm({ token }: Props) {
  const [done, setDone] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { token },
  });

  const onSubmit = handleSubmit(async (data) => {
    await resetPassword(data.token, data.new_password);
    setDone(true);
  });

  if (done) {
    return (
      <p className={styles.success}>Votre mot de passe a été réinitialisé.</p>
    );
  }

  return (
    <form onSubmit={onSubmit} className={styles.form} noValidate>
      <input type="hidden" value={token} {...register('token')} />

      <div className={styles.stack}>
        <label htmlFor="new_password" className={styles.label}>
          Nouveau mot de passe
        </label>
        <input
          id="new_password"
          type="password"
          autoComplete="new-password"
          placeholder="••••••••"
          {...register('new_password')}
          className={styles.input}
          aria-invalid={!!errors.new_password}
          aria-describedby={errors.new_password ? 'password-error' : undefined}
        />
        {errors.new_password && (
          <small id="password-error" className={styles.error}>
            {errors.new_password.message}
          </small>
        )}
      </div>

      <button type="submit" disabled={isSubmitting} className={styles.submit}>
        {isSubmitting ? 'Réinitialisation…' : 'Réinitialiser le mot de passe'}
      </button>
    </form>
  );
}
