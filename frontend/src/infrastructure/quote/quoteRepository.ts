import { apiClient } from '../../infrastructure/http/apiClient';
import { API_ENDPOINTS } from '../../shared/endpoints';

import type { PageResponse } from '../../domain/common/pagination';
import type { QuoteMetricsDto } from '../../domain/quote/metricsTypes';
import type {
  ApiQuoteResponse,
  ApiQuoteUpdatePayload,
  QuoteCreatePayload, // ← déjà présent chez toi
} from '../../domain/quote/types';

/**
 * CRUD des devis — typé avec les contrats domain/*
 */
export const quoteRepository = {
  /**
   * Crée un devis “entête” avec totaux à 0.00 (aucune ligne).
   * Le backend doit mettre owner=request.user côté ViewSet.
   */
  async create(payload: QuoteCreatePayload): Promise<ApiQuoteResponse> {
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
    const { data } = await apiClient.post<ApiQuoteResponse>(
      API_ENDPOINTS.quotes,
      body,
    );
    return data;
  },

  /**
   * Liste paginée (DRF) des devis de l'utilisateur courant.
   */
  async list(params?: {
    page?: number;
    page_size?: number;

    ordering?: string;
    search?: string;
    status?: string[];
    client?: string;
    issue_date_after?: string;
    issue_date_before?: string;
  }): Promise<PageResponse<ApiQuoteResponse>> {
    const { data } = await apiClient.get<PageResponse<ApiQuoteResponse>>(
      API_ENDPOINTS.quotes,
      {
        params: {
          page: params?.page,
          page_size: params?.page_size,
          ordering: params?.ordering,
          search: params?.search?.trim() || undefined,
          client: params?.client,
          status: params?.status?.length ? params.status.join(',') : undefined,
          issue_date_after: params?.issue_date_after,
          issue_date_before: params?.issue_date_before,
        },
      },
    );
    return data;
  },

  /**
   * Récupère un devis par id.
   */
  async retrieve(id: string): Promise<ApiQuoteResponse> {
    const { data } = await apiClient.get<ApiQuoteResponse>(
      `${API_ENDPOINTS.quotes}${id}/`,
    );
    return data;
  },

  /**
   * Met à jour partiellement un devis.
   * - payload: ApiQuoteUpdatePayload (items présent => remplace les lignes)
   */
  async update(
    id: string,
    payload: Partial<ApiQuoteUpdatePayload>,
  ): Promise<ApiQuoteResponse> {
    const { data } = await apiClient.patch<ApiQuoteResponse>(
      `${API_ENDPOINTS.quotes}${id}/`,
      payload,
    );
    return data;
  },

  async downloadPdf(id: string | number): Promise<void> {
    const url = API_ENDPOINTS.quotePdf(id);
    try {
      const res = await apiClient.get(url, { responseType: 'blob' });
      const blob = res.data as Blob;
      const cd = (res.headers['content-disposition'] as string) || '';
      const match = /filename="?(.*?)"?$/.exec(cd);
      const filename = match?.[1] || `devis-${id}.pdf`;

      const urlObj = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = urlObj;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(urlObj);
    } catch (error: unknown) {
      const resp = (error as { response?: { data: Blob } | undefined })
        ?.response;
      if (resp?.data instanceof Blob) {
        const text = await resp.data.text().catch(() => null);
        throw new Error(text || 'Erreur lors du téléchargement du PDF');
      }
      throw error;
    }
  },

  /**
   * Récupère les métriques dashboard (totaux, taux acceptation, évolution mensuelle)
   */
  async getMetrics(): Promise<QuoteMetricsDto> {
    const { data } = await apiClient.get<QuoteMetricsDto>(
      API_ENDPOINTS.quoteMetrics,
    );
    return data;
  },

  /**
   * Supprime un devis (soft delete avec protection statut).
   * Bloque la suppression si statut actif (DRAFT, SENT, ACCEPTED).
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`${API_ENDPOINTS.quotes}${id}/`);
  },
};
