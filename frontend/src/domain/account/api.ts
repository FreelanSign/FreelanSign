import { apiClient } from '@/infrastructure/http/apiClient';

export type UploadLogoResponse = {
  logo_url: string;
};

/**
 * Upload logo image to Supabase Storage via backend.
 * @param accountId - Account ID to upload logo for
 * @param file - Image file (jpeg, png, webp, gif). Max 2MB.
 * @returns Public URL of uploaded logo
 */
export async function uploadAccountLogo(
  accountId: number,
  file: File,
): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<UploadLogoResponse>(
    `/api/user/accounts/${accountId}/logo/`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    },
  );

  return response.data.logo_url;
}
