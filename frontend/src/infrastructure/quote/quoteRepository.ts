import { apiClient } from '../../infrastructure/http/apiClient';
import { API_ENDPOINTS } from '../../shared/endpoints';
import type { QuoteCreatePayload } from '../../domain/quote/types';

/**
 * Crée un devis “entête” avec totaux à 0.00 (aucune ligne).
 * Le backend doit mettre owner=request.user côté ViewSet.
 */
export const quoteRepository = {
  async create(payload: QuoteCreatePayload) {
    // Assure les totaux cohérents pour passer la CheckConstraint
    const body: QuoteCreatePayload = {
      currency: 'EUR',
      language: 'fr',
      subtotal: '0.00',
      tax_total: '0.00',
      discount_total: '0.00',
      total: '0.00',
      ...payload,
    };
    const { data } = await apiClient.post(API_ENDPOINTS.quotes, body);
    return data; // renvoie l'objet Quote créé (selon ton serializer)
  },

  /**
   * List quotes for current user.
   * - params: page, page_size optional, filters (status, client, search)
   * Returns paginated response from DRF.
   */
  async list(params?: {
    page?: number;
    page_size?: number;
    status?: string;
    client?: string;
    search?: string;
  }) {
    const { data } = await apiClient.get(API_ENDPOINTS.quotes, {
      params: {
        page: params?.page,
        page_size: params?.page_size,
        status: params?.status,
        client: params?.client,
        search: params?.search,
      },
    });
    return data;
  },

  /**
   * Optional : retrieve a single quote by id (to link detail)
   */
  async get(id: string) {
    const { data } = await apiClient.get(`${API_ENDPOINTS.quotes}${id}/`);
    return data;
  },
};
