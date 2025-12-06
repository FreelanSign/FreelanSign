import { apiClient } from '../http/apiClient';
import { API_ENDPOINTS } from '../../shared/endpoints';
import type {
  LegalTermsPreviewDto,
  LegalProfileDto,
} from '../../domain/legal-terms/types';

/**
 * Repository for legal terms - read-only access
 */
export const legalTermsRepository = {
  /**
   * Get preview of legal terms with account variable substitution
   */
  async getPreview(): Promise<LegalTermsPreviewDto> {
    const { data } = await apiClient.get<LegalTermsPreviewDto>(
      API_ENDPOINTS.legalTermsPreview,
    );
    return data;
  },

  /**
   * Get current user's legal profile with clause overrides
   */
  async getProfile(): Promise<LegalProfileDto> {
    const { data } = await apiClient.get<LegalProfileDto>(
      API_ENDPOINTS.legalTermsProfile,
    );
    return data;
  },
};
