// src/infrastructure/catalog/catalogRepository.ts
import { apiClient } from '../../infrastructure/http/apiClient';
import type { PrestationDto, AreaDto } from '../../domain/catalog/types';
import { API_ENDPOINTS } from '../../shared/endpoints';

/**
 * Repository catalogue — récupère prestations & domaines.
 *
 * - listPrestations accepts options to build query string (area, search, ordering, ids).
 * - normalizeListResponse supports DRF pagination or plain arrays.
 */

// petit cache in-memory (session) pour éviter re-fetch idem pendant la session
const prestationsCache = new Map<number, PrestationDto>();
const areasCache = new Map<number, AreaDto>();

function normalizeListResponse<T>(data: unknown): T[] {
  if (!data) return [];

  if (Array.isArray(data)) return data as T[];

  if (typeof data === 'object' && data !== null) {
    const d = data as Record<string, unknown>;
    if (Array.isArray(d.results)) return d.results as T[];
    if (Array.isArray(d.items)) return d.items as T[];
    if (Array.isArray(d.data)) return d.data as T[];
    // dernier recours : valeurs de l'objet
    return Object.values(d) as unknown as T[];
  }

  return [];
}

type ListPrestationsOpts = {
  area?: number | null;
  search?: string | null;
  ordering?: string | null;
  ids?: number[] | null; // optional batch support
};

/**
 * catalogRepository
 */
export const catalogRepository = {
  async getPrestationsByIds(ids: number[]): Promise<PrestationDto[]> {
    if (!ids || ids.length === 0) return [];

    // Reconstituer à partir du cache si possible
    const fromCache: PrestationDto[] = [];
    const missingIds: number[] = [];
    ids.forEach((id) => {
      const c = prestationsCache.get(id);
      if (c) fromCache.push(c);
      else missingIds.push(id);
    });

    if (missingIds.length === 0) return fromCache;

    // Try batch endpoint first (common pattern: ?ids=1,2,3)
    try {
      const resp = await apiClient.get(`${API_ENDPOINTS.catalogPrestation}`, {
        params: { ids: missingIds.join(',') },
      });
      const data = resp.data;
      const normalized = normalizeListResponse<PrestationDto>(data);
      normalized.forEach((p) => prestationsCache.set(p.id, p));
      return [...fromCache, ...normalized];
    } catch {
      // fallback: individual fetches
      const results = await Promise.all(
        missingIds.map(async (id) => {
          const r = await apiClient.get(
            `${API_ENDPOINTS.catalogPrestation}${id}/`,
          );
          const p = r.data as PrestationDto;
          prestationsCache.set(p.id, p);
          return p;
        }),
      );
      return [...fromCache, ...results];
    }
  },

  /**
   * List prestations with optional filters.
   * Example: listPrestations({ area: 8 }) -> GET /api/catalog/prestations/?area=8
   */
  async listPrestations(opts?: ListPrestationsOpts): Promise<PrestationDto[]> {
    const params: Record<string, string> = {};

    if (opts?.area != null) params.area = String(opts.area);
    if (opts?.search) params.search = String(opts.search);
    if (opts?.ordering) params.ordering = String(opts.ordering);
    if (opts?.ids && Array.isArray(opts.ids) && opts.ids.length > 0) {
      params.ids = opts.ids.join(',');
    }

    const resp = await apiClient.get(API_ENDPOINTS.catalogPrestation, {
      params,
    });
    const data = resp.data;
    const normalized = normalizeListResponse<PrestationDto>(data);
    // update cache
    normalized.forEach((p) => prestationsCache.set(p.id, p));
    return normalized;
  },

  async listAreas(): Promise<AreaDto[]> {
    const { data } = await apiClient.get(API_ENDPOINTS.catalogArea);
    const normalized = normalizeListResponse<AreaDto>(data);
    normalized.forEach((a) => areasCache.set(a.id, a));
    return normalized;
  },

  async getAreaById(id: number | null | undefined): Promise<AreaDto | null> {
    if (!id) return null;
    const cached = areasCache.get(id);
    if (cached) return cached;
    const resp = await apiClient.get(`${API_ENDPOINTS.catalogArea}${id}/`);
    const data: AreaDto = resp.data;
    areasCache.set(id, data);
    return data;
  },
};

