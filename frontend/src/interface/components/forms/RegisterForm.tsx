import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
// Update the path below to the correct relative path if needed
import { useAuth } from '../../../app/providers/AuthProvider';

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
    role: z.enum(['freelance', 'client', 'admin']),
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
  });

  return (
    <form
      onSubmit={handleSubmit(async (data) => {
        // Si registerUser attend seulement (email, password) :
        // await registerUser(data.email, data.password);
        // Sinon envoie tout l'objet :
        await registerUser(data);
      })}
      className="grid gap-3 max-w-sm"
    >
      <label className="grid gap-1">
        <span>Email</span>
        <input
          type="email"
          {...register('email')}
          className="border p-2 rounded"
        />
        {errors.email && (
          <small className="text-red-600">{errors.email.message}</small>
        )}
      </label>

      <label className="grid gap-1">
        <span>Mot de passe</span>
        <input
          type="password"
          {...register('password')}
          className="border p-2 rounded"
        />
        {errors.password && (
          <small className="text-red-600">{errors.password.message}</small>
        )}
      </label>

      <label className="grid gap-1">
        <span>Nom complet</span>
        <input
          type="text"
          {...register('full_name')}
          className="border p-2 rounded"
        />
        {errors.full_name && (
          <small className="text-red-600">{errors.full_name.message}</small>
        )}
      </label>

      <label className="grid gap-1">
        <span>Téléphone (top-level)</span>
        <input
          type="tel"
          {...register('phone')}
          className="border p-2 rounded"
        />
        {errors.phone && (
          <small className="text-red-600">{errors.phone.message}</small>
        )}
      </label>

      <fieldset className="border p-3 rounded">
        <legend className="font-medium">Profil</legend>

        <label className="grid gap-1">
          <span>Prénom</span>
          <input
            type="text"
            {...register('profile.first_name')}
            className="border p-2 rounded"
          />
          {errors.profile?.first_name && (
            <small className="text-red-600">
              {errors.profile.first_name.message}
            </small>
          )}
        </label>

        <label className="grid gap-1">
          <span>Nom</span>
          <input
            type="text"
            {...register('profile.last_name')}
            className="border p-2 rounded"
          />
          {errors.profile?.last_name && (
            <small className="text-red-600">
              {errors.profile.last_name.message}
            </small>
          )}
        </label>

        <label className="grid gap-1">
          <span>Date de naissance</span>
          <input
            type="date"
            {...register('profile.birthday')}
            className="border p-2 rounded"
          />
          {errors.profile?.birthday && (
            <small className="text-red-600">
              {errors.profile.birthday.message}
            </small>
          )}
        </label>

        <label className="grid gap-1">
          <span>Téléphone (profil)</span>
          <input
            type="tel"
            {...register('profile.phone')}
            className="border p-2 rounded"
          />
          {errors.profile?.phone && (
            <small className="text-red-600">
              {errors.profile.phone.message}
            </small>
          )}
        </label>

        <label className="grid gap-1">
          <span>Avatar URL</span>
          <input
            type="url"
            {...register('profile.avatar_url')}
            className="border p-2 rounded"
          />
          {errors.profile?.avatar_url && (
            <small className="text-red-600">
              {errors.profile.avatar_url.message}
            </small>
          )}
        </label>

        <label className="grid gap-1">
          <span>Rôle</span>
          <select
            {...register('profile.role')}
            className="border p-2 rounded"
            defaultValue="freelance"
          >
            <option value="freelance">Freelance</option>
            <option value="client">Client</option>
            <option value="admin">Admin</option>
          </select>
          {errors.profile?.role && (
            <small className="text-red-600">
              {errors.profile.role.message}
            </small>
          )}
        </label>
      </fieldset>

      <button
        disabled={isSubmitting}
        className="bg-black text-white rounded p-2"
      >
        {isSubmitting ? 'Création…' : "S'inscrire"}
      </button>
    </form>
  );
}
