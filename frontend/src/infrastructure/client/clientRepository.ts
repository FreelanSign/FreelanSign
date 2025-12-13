// src/infrastructure/client/clientRepository.ts
import { apiClient } from '../http/apiClient';
import { API_ENDPOINTS } from '../../shared/endpoints';
import type { ClientDto, ClientCreateDto } from '../../domain/client/types';

/** Paginé DRF minimal */
type Paginated<T> = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
};

/** Page response pour listes paginées */
export type PageResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

/** Type-guard : détecte une réponse paginée (has results: Array) */
function isPaginatedResponse<T>(v: unknown): v is Paginated<T> {
  if (v === null || typeof v !== 'object') return false;
  const obj = v as Record<string, unknown>;
  return Array.isArray(obj['results']);
}

/** Récupère les clients avec pagination optionnelle */
export const clientRepository = {
  async list(params?: {
    search?: string;
    page?: number;
    page_size?: number;
  }): Promise<PageResponse<ClientDto>> {
    const resp = await apiClient.get(API_ENDPOINTS.clients, {
      params: {
        ordering: 'name',
        search: params?.search ?? undefined,
        page: params?.page ?? undefined,
        page_size: params?.page_size ?? undefined,
      },
    });

    const data: unknown = resp.data;

    // Si la réponse est paginée DRF -> retourne telle quelle
    if (isPaginatedResponse<ClientDto>(data)) {
      return {
        count: data.count ?? 0,
        next: data.next ?? null,
        previous: data.previous ?? null,
        results: data.results,
      };
    }

    // Si la réponse est un tableau -> wrap dans PageResponse
    if (Array.isArray(data)) {
      return {
        count: data.length,
        next: null,
        previous: null,
        results: data as ClientDto[],
      };
    }

    // Format inattendu : log et retourne réponse vide
    console.warn(
      '[clientRepository] Unexpected response shape for GET clients',
      data,
    );
    return {
      count: 0,
      next: null,
      previous: null,
      results: [],
    };
  },

  async retrieve(id: string): Promise<ClientDto> {
    const { data } = await apiClient.get(`${API_ENDPOINTS.clients}${id}/`);
    return data as ClientDto;
  },
  async update(id: string, payload: unknown) {
    const { data } = await apiClient.patch(
      `${API_ENDPOINTS.clients}${id}/`,
      payload,
    );
    return data;
  },

  async create(payload: ClientCreateDto): Promise<ClientDto> {
    const { data } = await apiClient.post(API_ENDPOINTS.clients, payload);
    return data as ClientDto;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`${API_ENDPOINTS.clients}${id}/`);
  },
};
