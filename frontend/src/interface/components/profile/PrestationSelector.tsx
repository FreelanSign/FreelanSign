// src/interface/components/profile/PrestationsSelector.tsx
import axios from 'axios';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { PrestationDto } from '../../../domain/catalog/types';
import { catalogRepository } from '../../../infrastructure/catalog/catalogRepository';

// --- helpers ---------------------------------------------------------------
function getStringField(obj: PrestationDto, ...keys: string[]): string | null {
  const map = obj as unknown as Record<string, unknown>;
  for (const k of keys) {
    const v = map[k];
    if (typeof v === 'string' && v.trim() !== '') return v.trim();
  }
  return null;
}
function getNumberField(obj: PrestationDto, ...keys: string[]): number | null {
  const map = obj as unknown as Record<string, unknown>;
  for (const k of keys) {
    const v = map[k];
    if (typeof v === 'number') return v;
    if (typeof v === 'string') {
      const n = Number(v);
      if (!Number.isNaN(n)) return n;
    }
  }
  return null;
}

function isCanceledError(err: unknown): boolean {
  if (axios.isAxiosError(err) && err.code === 'ERR_CANCELED') return true;
  if (err instanceof DOMException && err.name === 'AbortError') return true;
  if (typeof err === 'object' && err !== null && 'name' in err) {
    const n = (err as { name?: unknown }).name;
    if (n === 'CanceledError') return true;
  }
  return false;
}

function getPrestationAreaId(p: unknown): number | null {
  if (!p || typeof p !== 'object') return null;
  const obj = p as Record<string, unknown>;

  // number form
  if (typeof obj.area === 'number') return obj.area;
  if (typeof obj.area_id === 'number') return obj.area_id;

  // nested object with id
  const area = obj.area;
  if (area && typeof area === 'object') {
    const a = area as Record<string, unknown>;
    if (typeof a.id === 'number') return a.id;
    if (typeof a.id === 'string') {
      const n = Number(a.id);
      return Number.isNaN(n) ? null : n;
    }
  }
  return null;
}

// --- props -----------------------------------------------------------------
type Props = {
  professionalId?: number | null;
  domaine?: number | null;
  /** liste contrôlée par le parent */
  selected: number[];
  /** notify parent (appelé seulement depuis handlers/effets, JAMAIS pendant render) */
  onChange: (ids: number[]) => void;
};

// Type étendu pour inclure l'info "hors domaine"
type PrestationWithWarning = PrestationDto & {
  isOutOfDomain?: boolean;
  areaId?: number | null;
};

// --- component -------------------------------------------------------------
export default function PrestationsSelector({
  domaine = null,
  selected,
  onChange,
}: Props) {
  const [prestations, setPrestations] = useState<PrestationDto[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [search, setSearch] = useState<string>('');
  const [applyDomaineFilter, setApplyDomaineFilter] = useState<boolean>(true);

  const abortRef = useRef<AbortController | null>(null);

  // Charger les prestations (avec AbortController)
  const loadPrestations = useCallback(async () => {
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;

    setLoading(true);
    try {
      const params: Record<string, unknown> = {};
      if (applyDomaineFilter && domaine != null) params.area = domaine;
      if (search.trim() !== '') params.search = search.trim();

      try {
        const lista = await catalogRepository.listPrestations({
          ...params,
          signal: ctrl.signal,
        });
        if (!ctrl.signal.aborted) setPrestations(lista);
      } catch (err) {
        // Annulations → silencieux
        if (isCanceledError(err)) {
          return;
        }
        // Fallback sans params + filtre client
        const all = await catalogRepository.listPrestations({
          signal: ctrl.signal,
        });
        if (ctrl.signal.aborted) return;
        const filtered = (all || []).filter((p) => {
          if (applyDomaineFilter && domaine != null) {
            const areaId =
              getNumberField(p, 'area', 'area_id') ?? getPrestationAreaId(p);
            if (areaId !== domaine) return false;
          }
          if (search.trim() !== '') {
            const name = getStringField(p, 'name', 'title') ?? '';
            if (!name.toLowerCase().includes(search.trim().toLowerCase()))
              return false;
          }
          return true;
        });
        setPrestations(filtered);
      }
    } catch (err) {
      // Annulations → silencieux
      if (isCanceledError(err)) {
        return;
      }
      console.warn('Prestations load failed', err);
      setPrestations(null);
    } finally {
      if (!ctrl.signal.aborted) setLoading(false);
    }
  }, [applyDomaineFilter, domaine, search]);

  useEffect(() => {
    loadPrestations();
    return () => abortRef.current?.abort();
  }, [loadPrestations]);

  // ❌ SUPPRIMÉ : le useEffect qui nettoyait les sélections hors domaine
  // On laisse l'utilisateur gérer ses sélections librement

  // Toggle: calcule le prochain tableau et notifie le parent (handler utilisateur -> safe)
  const toggleSelect = useCallback(
    (id: number) => {
      const next = selected.includes(id)
        ? selected.filter((x) => x !== id)
        : [...selected, id];
      onChange(next);
    },
    [selected, onChange],
  );

  // Enrichir les prestations avec l'info "hors domaine"
  const displayedWithWarnings = useMemo((): PrestationWithWarning[] => {
    if (!prestations) return [];

    return prestations
      .filter((p) => {
        // Filtrer uniquement les prestations actives en base
        const status = getStringField(p, 'status');
        return status === 'ACTIVE';
      })
      .map((p) => {
        const areaId =
          getNumberField(p, 'area', 'area_id') ?? getPrestationAreaId(p);
        const isOutOfDomain = domaine != null && areaId !== domaine;
        return {
          ...p,
          areaId,
          isOutOfDomain,
        };
      });
  }, [prestations, domaine]);

  // Compter les prestations sélectionnées hors domaine
  const outOfDomainCount = useMemo(() => {
    if (!domaine) return 0;
    return selected.filter((id) => {
      const prestation = displayedWithWarnings.find((p) => p.id === id);
      return prestation?.isOutOfDomain;
    }).length;
  }, [selected, displayedWithWarnings, domaine]);

  return (
    <div className="grid gap-4">
      {/* Barre de recherche */}
      <div>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Rechercher un service..."
          className="w-full px-3.5 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          aria-label="Rechercher une prestation"
        />
      </div>

      {/* Filtre par domaine */}
      <div className="flex items-center gap-3 pb-2 border-b border-gray-200">
        <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
          <input
            type="checkbox"
            checked={applyDomaineFilter}
            onChange={(e) => setApplyDomaineFilter(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
          />
          <span className="font-medium">Filtrer par domaine professionnel</span>
        </label>
      </div>

      {/* Avertissement si des prestations hors domaine sont sélectionnées */}
      {outOfDomainCount > 0 && (
        <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-4 text-sm text-yellow-900">
          <div className="flex items-start gap-3">
            <span className="text-lg">⚠️</span>
            <div>
              <strong className="font-semibold">Attention :</strong> Vous avez
              sélectionné {outOfDomainCount} prestation
              {outOfDomainCount > 1 ? 's' : ''} en dehors de votre domaine
              principal.
              {domaine && (
                <div className="mt-1 text-xs text-yellow-800">
                  Décochez "Filtrer par domaine professionnel" pour voir toutes
                  vos sélections.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Liste des prestations */}
      <div>
        {loading ? (
          <div className="text-center py-8 text-gray-500">
            Chargement des prestations…
          </div>
        ) : prestations === null ? (
          <div className="text-center py-8 text-red-500">
            Impossible de charger les prestations.
          </div>
        ) : displayedWithWarnings.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Aucune prestation disponible.
          </div>
        ) : (
          <div className="grid gap-2">
            {displayedWithWarnings.map((p) => {
              const title =
                getStringField(p, 'name', 'title') ?? `Service #${p.id}`;
              const desc =
                getStringField(p, 'description', 'short_description') ?? '';
              const priceCents = getNumberField(
                p,
                'default_rate_cents',
                'price_cents',
              );
              const checked = selected.includes(p.id);

              return (
                <label
                  key={p.id}
                  className={`grid grid-cols-[auto_1fr_auto] gap-4 items-start p-3 border rounded-lg transition-all cursor-pointer ${
                    p.isOutOfDomain
                      ? 'border-orange-300 bg-orange-50 hover:bg-orange-100'
                      : 'border-gray-200 hover:bg-gray-50 hover:border-gray-300'
                  }`}
                >
                  {/* Checkbox */}
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleSelect(p.id)}
                    className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  />

                  {/* Nom + Description */}
                  <div className="min-w-0">
                    <div className="font-semibold text-gray-900 flex items-center gap-2 flex-wrap">
                      {title}
                      {p.isOutOfDomain && (
                        <span className="text-xs px-2 py-0.5 bg-orange-200 text-orange-800 rounded-full font-normal">
                          Hors domaine
                        </span>
                      )}
                    </div>
                    {desc && (
                      <div className="text-sm text-gray-600 mt-1">{desc}</div>
                    )}
                  </div>

                  {/* Prix */}
                  <div className="text-right text-gray-900 font-medium whitespace-nowrap">
                    {typeof priceCents === 'number'
                      ? `${(priceCents / 100).toFixed(2).replace('.', ',')} €`
                      : '—'}
                  </div>
                </label>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
