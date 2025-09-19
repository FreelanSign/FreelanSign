// src/infrastructure/catalog/catalogRepository.ts
import { apiClient } from '../../infrastructure/http/apiClient';
import type { PrestationDto, AreaDto } from '../../domain/catalog/types';
import { API_ENDPOINTS } from '../../shared/endpoints';

/**
 * Repository catalogue — récupère prestations & domaines.
 *
 * Strategy:
 * 1) Tente un appel batch (GET /api/catalog/prestation/?ids=1,2,3) — pratique si backend supporte.
 * 2) Si batch retourne 404 / 400 / non supporté -> fallback: Promise.all sur /api/catalog/prestation/{id}/
 *
 * NOTE: ajuste les paths si ton backend diffère (ex: '/api/catalog/prestations/' ou '/api/catalog/prestation-list/').
 */

// petit cache in-memory (session) pour éviter re-fetch idem pendant la session
const prestationsCache = new Map<number, PrestationDto>();
const areasCache = new Map<number, AreaDto>();

/**
 * Normalise la réponse côté backend en tableau.
 * - supporte : tableau direct [], DRF paginé { results: [...] }, { items: [...] }, { data: [...] }
 * - si c'est un objet clé->valeur on retourne Object.values()
 */
function normalizeListResponse<T>(data: unknown): T[] {
  if (!data) return [];

  // tableau direct
  if (Array.isArray(data)) return data as T[];

  // si c'est un objet, on regarde plusieurs clés connues (results, items, data)
  if (typeof data === 'object' && data !== null) {
    const d = data as Record<string, unknown>;

    if (Array.isArray(d.results)) return d.results as T[];
    if (Array.isArray(d.items)) return d.items as T[];
    if (Array.isArray(d.data)) return d.data as T[];

    // dernier recours : si c'est un objet map-like, on retourne ses valeurs
    return Object.values(d) as unknown as T[];
  }

  return [];
}

export const catalogRepository = {
  /**
   * Récupère une liste de prestations par ids.
   * Essaie batch, sinon fallback.
   */
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
      // fallback: individual fetches (laissons l'erreur remonter si ça échoue)
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

  async listPrestations(): Promise<PrestationDto[]> {
    const { data } = await apiClient.get(API_ENDPOINTS.catalogPrestation);
    return normalizeListResponse<PrestationDto>(data);
  },

  async listAreas(): Promise<AreaDto[]> {
    const { data } = await apiClient.get(API_ENDPOINTS.catalogArea);
    return normalizeListResponse<AreaDto>(data);
  },

  /**
   * Récupère une Area (domaine) par id (avec cache simple).
   */
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
