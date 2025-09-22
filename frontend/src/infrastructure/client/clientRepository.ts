// src/infrastructure/client/clientRepository.ts
import { apiClient } from '../http/apiClient';
import { API_ENDPOINTS } from '../../shared/endpoints';
import type { ClientDto } from '../../domain/client/types';

/** Paginé DRF minimal */
type Paginated<T> = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
};

/** Type-guard : détecte une réponse paginée (has results: Array) */
function isPaginatedResponse<T>(v: unknown): v is Paginated<T> {
  if (v === null || typeof v !== 'object') return false;
  const obj = v as Record<string, unknown>;
  return Array.isArray(obj['results']);
}

/** Récupère les clients pour la liste déroulante.
 *  Retourne toujours un tableau (vide si format inattendu).
 */
export const clientRepository = {
  async list(params?: { search?: string }): Promise<ClientDto[]> {
    const resp = await apiClient.get(API_ENDPOINTS.clients, {
      params: {
        ordering: 'name',
        search: params?.search ?? undefined,
      },
    });

    const data: unknown = resp.data;

    // Si la réponse est déjà un tableau -> on cast en ClientDto[]
    if (Array.isArray(data)) {
      return data as ClientDto[];
    }

    // Si la réponse est paginée DRF -> retourne results
    if (isPaginatedResponse<ClientDto>(data)) {
      return data.results;
    }

    // Format inattendu : log et retourne tableau vide pour tolérance
    // (évite de propager `any` vers le reste de l'app)

    console.warn(
      '[clientRepository] Unexpected response shape for GET clients',
      data,
    );
    return [];
  },
};
