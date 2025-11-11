// frontend/components/auth/RequestPasswordResetForm.tsx

import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { authRepository } from '../../../infrastructure/auth/authRepository';
import styles from './request-password-reset-form.module.css';

const schema = z.object({
  email: z.string().min(1, 'Email requis').email('Email invalide'),
});

type FormData = z.infer<typeof schema>;

export default function RequestPasswordResetForm() {
  const [submitted, setSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = handleSubmit(async (data) => {
    await authRepository.requestPasswordReset(data.email);
    setSubmitted(true);
  });

  if (submitted) {
    return (
      <p className={styles.success}>
        Si l'email existe, un lien de réinitialisation a été envoyé.
      </p>
    );
  }

  return (
    <form onSubmit={onSubmit} className={styles.form} noValidate>
      <div className={styles.stack}>
        <label htmlFor="email" className={styles.label}>
          Email
        </label>
        <input
          id="email"
          type="email"
          placeholder="jean.dupont@example.com"
          {...register('email')}
          className={styles.input}
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <small id="email-error" className={styles.error}>
            {errors.email.message}
          </small>
        )}
      </div>

      <button type="submit" disabled={isSubmitting} className={styles.submit}>
        {isSubmitting ? 'Envoi en cours…' : 'Envoyer le lien'}
      </button>
    </form>
  );
}
