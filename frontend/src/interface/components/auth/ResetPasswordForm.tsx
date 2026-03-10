// frontend/components/auth/ResetPasswordForm.tsx

import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { z } from 'zod';
import { resetPassword } from '../../../lib/api/auth';
import styles from './reset-password-form.module.css';

const schema = z
  .object({
    token: z.string().min(1),
    new_password: z
      .string()
      .min(8, 'Le mot de passe doit contenir au moins 8 caractères')
      .regex(/[a-zA-Z]/, 'Le mot de passe doit contenir au moins une lettre')
      .regex(/[0-9]/, 'Le mot de passe doit contenir au moins un chiffre'),
    confirm_password: z.string().min(1, 'Confirmez votre mot de passe'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: 'Les mots de passe ne correspondent pas',
    path: ['confirm_password'],
  });

type FormData = z.infer<typeof schema>;

interface Props {
  token: string;
}

export default function ResetPasswordForm({ token }: Props) {
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { token },
  });

  const onSubmit = handleSubmit(async (data) => {
    setError(null);
    try {
      await resetPassword(data.token, data.new_password);
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inattendue.');
    }
  });

  if (done) {
    return (
      <div className={styles.success}>
        <p>Votre mot de passe a été réinitialisé.</p>
        <Link to="/login" className={styles.loginLink}>
          Se connecter
        </Link>
      </div>
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

      <div className={styles.stack}>
        <label htmlFor="confirm_password" className={styles.label}>
          Confirmer le mot de passe
        </label>
        <input
          id="confirm_password"
          type="password"
          autoComplete="new-password"
          placeholder="••••••••"
          {...register('confirm_password')}
          className={styles.input}
          aria-invalid={!!errors.confirm_password}
          aria-describedby={
            errors.confirm_password ? 'confirm-error' : undefined
          }
        />
        {errors.confirm_password && (
          <small id="confirm-error" className={styles.error}>
            {errors.confirm_password.message}
          </small>
        )}
      </div>

      {error && <p className={styles.error}>{error}</p>}

      <button type="submit" disabled={isSubmitting} className={styles.submit}>
        {isSubmitting ? 'Réinitialisation…' : 'Réinitialiser le mot de passe'}
      </button>
    </form>
  );
}
