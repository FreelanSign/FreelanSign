import { apiClient } from '@/infrastructure/http/apiClient';
import { API_ENDPOINTS } from '@/shared/endpoints';

export type UploadAvatarResponse = {
  avatar_url: string;
};

/**
 * Upload avatar image to Supabase Storage via backend.
 * @param file - Image file (jpeg, png, webp, gif). Max 2MB.
 * @returns Public URL of uploaded avatar
 */
export async function uploadAvatar(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<UploadAvatarResponse>(
    API_ENDPOINTS.meAvatar,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    },
  );

  return response.data.avatar_url;
}
