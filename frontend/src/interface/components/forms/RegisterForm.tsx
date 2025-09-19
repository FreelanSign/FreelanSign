import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
// Update the path below to the correct relative path if needed
import { useAuth } from '../../../app/providers/AuthProvider';

const schema = z.object({
  email: z.string().email('Email invalide'),
  password: z.string().min(6, '6 caractères minimum'),
});

type FormData = z.infer<typeof schema>;

export default function RegisterForm() {
  const { register: registerUser } = useAuth();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  return (
    <form
      onSubmit={handleSubmit(async (data) => {
        await registerUser(data.email, data.password);
      })}
      className="grid gap-3 max-w-sm"
    >
      <label className="grid gap-1">
        <span>Email</span>
        <input type="email" {...register('email')} className="border p-2 rounded" />
        {errors.email && <small className="text-red-600">{errors.email.message}</small>}
      </label>
      <label className="grid gap-1">
        <span>Mot de passe</span>
        <input type="password" {...register('password')} className="border p-2 rounded" />
        {errors.password && <small className="text-red-600">{errors.password.message}</small>}
      </label>
      <button disabled={isSubmitting} className="bg-black text-white rounded p-2">
        {isSubmitting ? 'Création…' : "S'inscrire"}
      </button>
    </form>
  );
}
