import { apiClient } from '../http/apiClient';
import { API_ENDPOINTS } from '../../shared/endpoints';
import type { ClientDto } from '../../domain/client/types';

/** Récupère les clients pour la liste déroulante. */
export const clientRepository = {
  /**
   * Retourne un tableau ClientDto.
   * Prend en charge une liste simple, pagination standard
   */
  async list(params?: { search?: string }): Promise<ClientDto[]> {
    const { data } = await apiClient.get(API_ENDPOINTS.clients, {
      params: {
        ordering: 'name',
        search: params?.search ?? undefined,
      },
    });
    // Si l'API renvoie un objet paginé, on prend data.results
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      if (Array.isArray((data as any).results)) {
        return (data as any).results as ClientDto[];
      }
      // Si ce n'est ni un array ni paginé
      console.warn('[clientRepository] Unexpected response format', data);
      return [];
    }
    return data as ClientDto[];
  },
};
