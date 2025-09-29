import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '../../../app/providers/AuthProvider';

const schema = z.object({
  email: z.string().email('Email invalide'),
  password: z.string().min(1, 'Mot de passe requis'),
});

type FormData = z.infer<typeof schema>;

export default function LoginForm() {
  const { login } = useAuth();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  return (
    <form
      onSubmit={handleSubmit(async (data) => {
        await login(data.email, data.password);
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
      <button
        disabled={isSubmitting}
        className="bg-black text-white rounded p-2"
      >
        {isSubmitting ? 'Connexion…' : 'Se connecter'}
      </button>
    </form>
  );
}
