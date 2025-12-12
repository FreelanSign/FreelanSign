import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '../../../app/providers/AuthProvider';
import styles from './register-form.module.css';

const schema = z.object({
  email: z.string().email('Email invalide'),
  password: z.string().min(6, '6 caractères minimum'),
  full_name: z.string().optional(),
  phone: z
    .string()
    .optional()
    .refine((v) => !v || v.length >= 6, 'Numéro trop court'),
  profile: z.object({
    first_name: z.string().min(1, 'Prénom requis'),
    last_name: z.string().min(1, 'Nom requis'),
    birthday: z
      .string()
      .regex(/^\d{4}-\d{2}-\d{2}$/, 'Date invalide (YYYY-MM-DD)')
      .optional(),
    phone: z.string().optional(),
    avatar_url: z
      .string()
      .optional()
      .refine((v) => !v || /^https?:\/\//.test(v), "URL d'avatar invalide"),
    role: z.literal('freelance'),
  }),
});

type FormData = z.infer<typeof schema>;

export default function RegisterForm() {
  const { register: registerUser } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      profile: { role: 'freelance' },
    },
    mode: 'onBlur',
  });

  const onSubmit = handleSubmit(async (data) => {
    await registerUser(data);
  });

  return (
    <form onSubmit={onSubmit} className={styles.form} noValidate>
      <div className={styles.fields}>
        <div className={styles.field}>
          <label htmlFor="email" className={styles.label}>
            Email
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            {...register('email')}
            className={styles.input}
            aria-invalid={!!errors.email}
            aria-describedby={errors.email ? 'email-error' : undefined}
            placeholder="ex. jean.dupont@exemple.com"
          />
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
            autoComplete="new-password"
            {...register('password')}
            className={styles.input}
            aria-invalid={!!errors.password}
            aria-describedby={errors.password ? 'password-error' : undefined}
            placeholder="Minimum 6 caractères"
          />
          {errors.password && (
            <small id="password-error" className={styles.error}>
              {errors.password.message}
            </small>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="full_name" className={styles.label}>
            Nom complet (optionnel)
          </label>
          <input
            id="full_name"
            type="text"
            autoComplete="name"
            {...register('full_name')}
            className={styles.input}
            aria-invalid={!!errors.full_name}
            aria-describedby={errors.full_name ? 'full-name-error' : undefined}
            placeholder="Jean Dupont"
          />
          {errors.full_name && (
            <small id="full-name-error" className={styles.error}>
              {errors.full_name.message}
            </small>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="phone" className={styles.label}>
            Téléphone (optionnel)
          </label>
          <input
            id="phone"
            type="tel"
            autoComplete="tel"
            {...register('phone')}
            className={styles.input}
            aria-invalid={!!errors.phone}
            aria-describedby={errors.phone ? 'phone-error' : undefined}
            placeholder="+33 6 12 34 56 78"
          />
          {errors.phone && (
            <small id="phone-error" className={styles.error}>
              {errors.phone.message}
            </small>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="first_name" className={styles.label}>
            Prénom
          </label>
          <input
            id="first_name"
            type="text"
            autoComplete="given-name"
            {...register('profile.first_name')}
            className={styles.input}
            aria-invalid={!!errors.profile?.first_name}
            aria-describedby={
              errors.profile?.first_name ? 'first-name-error' : undefined
            }
            placeholder="Prénom"
          />
          {errors.profile?.first_name && (
            <small id="first-name-error" className={styles.error}>
              {errors.profile.first_name.message}
            </small>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="last_name" className={styles.label}>
            Nom
          </label>
          <input
            id="last_name"
            type="text"
            autoComplete="family-name"
            {...register('profile.last_name')}
            className={styles.input}
            aria-invalid={!!errors.profile?.last_name}
            aria-describedby={
              errors.profile?.last_name ? 'last-name-error' : undefined
            }
            placeholder="Nom"
          />
          {errors.profile?.last_name && (
            <small id="last-name-error" className={styles.error}>
              {errors.profile.last_name.message}
            </small>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="birthday" className={styles.label}>
            Date de naissance
          </label>
          <input
            id="birthday"
            type="date"
            {...register('profile.birthday')}
            className={styles.input}
            aria-invalid={!!errors.profile?.birthday}
            aria-describedby={
              errors.profile?.birthday ? 'birthday-error' : undefined
            }
          />
          {errors.profile?.birthday && (
            <small id="birthday-error" className={styles.error}>
              {errors.profile.birthday.message}
            </small>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="profile_phone" className={styles.label}>
            Téléphone (profil)
          </label>
          <input
            id="profile_phone"
            type="tel"
            autoComplete="tel"
            {...register('profile.phone')}
            className={styles.input}
            aria-invalid={!!errors.profile?.phone}
            aria-describedby={
              errors.profile?.phone ? 'profile-phone-error' : undefined
            }
            placeholder="+33 6 12 34 56 78"
          />
          {errors.profile?.phone && (
            <small id="profile-phone-error" className={styles.error}>
              {errors.profile.phone.message}
            </small>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="avatar_url" className={styles.label}>
            Avatar URL
          </label>
          <input
            id="avatar_url"
            type="url"
            inputMode="url"
            placeholder="https://…"
            {...register('profile.avatar_url')}
            className={styles.input}
            aria-invalid={!!errors.profile?.avatar_url}
            aria-describedby={
              errors.profile?.avatar_url ? 'avatar-error' : undefined
            }
          />
          {errors.profile?.avatar_url && (
            <small id="avatar-error" className={styles.error}>
              {errors.profile.avatar_url.message}
            </small>
          )}
          <p className={styles.help}>
            Tu pourras importer un fichier plus tard (upload côté app).
          </p>
        </div>
      </div>

      <footer className={styles.actions}>
        <button type="submit" disabled={isSubmitting} className={styles.submit}>
          {isSubmitting ? 'Création…' : "S'inscrire"}
        </button>
        <button type="button" disabled={isSubmitting} className={styles.ghost}>
          Annuler
        </button>
      </footer>
    </form>
  );
}
