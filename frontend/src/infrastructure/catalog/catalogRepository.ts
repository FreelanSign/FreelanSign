// src/infrastructure/catalog/catalogRepository.ts
import { apiClient } from '../http/apiClient';
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
      const data: PrestationDto[] = resp.data;
      data.forEach((p) => prestationsCache.set(p.id, p));
      return [...fromCache, ...data];
    } catch (err) {
      // fallback: try individual fetch for each id
      try {
        const results = await Promise.all(
          missingIds.map(async (id) => {
            const r = await apiClient.get(`${API_ENDPOINTS.catalogPrestation}${id}/`);
            const p = r.data as PrestationDto;
            prestationsCache.set(p.id, p);
            return p;
          })
        );
        return [...fromCache, ...results];
      } catch (err2) {
        // si ça échoue, on propage l'erreur (upstream pourra gérer)
        throw err2;
      }
    }
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
