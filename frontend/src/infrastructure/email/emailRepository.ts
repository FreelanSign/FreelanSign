// frontend/src/infrastructure/email/emailRepository.ts

import { apiClient } from '../http/apiClient';

export interface PreparedMailResponse {
  to: string;
  subject: string;
  body: string;
  template_version: string;
}

export const emailRepository = {
  async getPreparedEmail(quoteId: string): Promise<PreparedMailResponse> {
    const { data } = await apiClient.get(
      `/api/quote/${quoteId}/prepared-email`,
    );
    return data;
  },
};
