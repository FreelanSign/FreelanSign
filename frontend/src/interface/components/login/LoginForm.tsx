import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '../../../app/providers/AuthProvider';
import styles from './login-form.module.css';

const schema = z.object({
  // Affiche "Email requis" si vide, sinon "Email invalide" si format KO
  email: z.string().min(1, 'Email requis').email('Email invalide'),
  password: z.string().min(1, 'Mot de passe requis'),
});

type FormData = z.infer<typeof schema>;

export default function LoginForm() {
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    mode: 'onSubmit',
    reValidateMode: 'onChange',
  });

  const onSubmit = handleSubmit(async (data) => {
    try {
      await login(data.email, data.password);
    } catch {
      // Message générique si les identifiants ne matchent pas
      setError('password', {
        type: 'manual',
        message: 'Identifiants invalides.',
      });
    }
  });

  return (
    <form onSubmit={onSubmit} className={styles.form} noValidate>
      <div className={styles.stack}>
        <div className={styles.field}>
          <label htmlFor="email" className={styles.label}>
            Email
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="jean.dupont@exemple.com"
            {...register('email')}
            className={styles.input}
            aria-invalid={!!errors.email}
            aria-describedby={errors.email ? 'email-error' : undefined}
          />
          {/* ✅ Ces messages n'apparaissent que si on a tenté de soumettre */}
          {errors.email && (
            <small id="email-error" className={styles.error}>
              {errors.email.message}
            </small>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="password" className={styles.label}>
            Mot de passe
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            placeholder="••••••••"
            {...register('password')}
            className={styles.input}
            aria-invalid={!!errors.password}
            aria-describedby={errors.password ? 'password-error' : undefined}
          />
          {errors.password && (
            <small id="password-error" className={styles.error}>
              {errors.password.message}
            </small>
          )}
        </div>
      </div>

      <div className={styles.actions}>
        <button type="submit" disabled={isSubmitting} className={styles.submit}>
          {isSubmitting ? 'Connexion…' : 'Se connecter'}
        </button>
      </div>
    </form>
  );
}
