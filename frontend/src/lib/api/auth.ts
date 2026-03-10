// frontend/lib/api/auth.ts

import { type AxiosError } from 'axios';
import { apiClient } from '../../infrastructure/http/apiClient';

interface ApiErrorBody {
  detail?: string;
  message?: string;
}

export async function resetPassword(
  token: string,
  new_password: string,
): Promise<void> {
  try {
    await apiClient.post('/api/auth/reset-password/', { token, new_password });
  } catch (err) {
    const axiosErr = err as AxiosError<ApiErrorBody>;
    const status = axiosErr.response?.status;
    const data = axiosErr.response?.data;

    let message = 'Erreur lors de la réinitialisation.';
    if (status === 404) {
      message = 'Lien invalide ou expiré. Demandez un nouveau lien.';
    } else if (data?.detail || data?.message) {
      message = data.detail ?? data.message ?? message;
    }

    throw new Error(message);
  }
}
