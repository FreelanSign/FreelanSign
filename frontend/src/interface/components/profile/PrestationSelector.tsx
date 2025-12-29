// src/interface/components/profile/PrestationsSelector.tsx
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
  accountId?: number | null;
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
      {/* Barre de recherche & Filtres */}
      <div className="space-y-3">
        <div className="relative">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher un service..."
            className="pl-3"
            aria-label="Rechercher une prestation"
          />
        </div>

        <div className="flex items-center space-x-2 px-1">
          <input
            id="domain-filter"
            type="checkbox"
            checked={applyDomaineFilter}
            onChange={(e) => setApplyDomaineFilter(e.target.checked)}
            className="h-4 w-4 rounded border-gray-300 text-brand focus:ring-brand"
          />
          <Label
            htmlFor="domain-filter"
            className="text-xs font-medium cursor-pointer"
          >
            Filtrer par domaine professionnel
          </Label>
        </div>
      </div>

      {/* Avertissement si des prestations hors domaine sont sélectionnées */}
      {outOfDomainCount > 0 && (
        <div className="bg-orange-50 border border-orange-100 rounded-lg p-3 text-xs text-orange-800">
          <div className="flex items-start gap-2">
            <span className="shrink-0">⚠️</span>
            <p>
              <span className="font-semibold">Note :</span> {outOfDomainCount}{' '}
              service{outOfDomainCount > 1 ? 's' : ''} hors domaine sélectionné
              {outOfDomainCount > 1 ? 's' : ''}.
              {domaine &&
                !applyDomaineFilter &&
                ' Ils sont affichés en orange.'}
            </p>
          </div>
        </div>
      )}

      {/* Liste des prestations avec hauteur maximale et scroll */}
      <div className="max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
        {loading ? (
          <div className="flex flex-col gap-2">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-16 w-full bg-muted/50 animate-pulse rounded-lg"
              />
            ))}
          </div>
        ) : prestations === null ? (
          <div className="text-center py-8 text-destructive text-sm italic">
            Impossible de charger les prestations.
          </div>
        ) : displayedWithWarnings.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground text-sm italic">
            Aucune prestation disponible.
          </div>
        ) : (
          <div className="flex flex-col gap-2">
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
                  className={`flex items-start gap-3 p-3 border rounded-lg transition-all cursor-pointer group ${
                    checked
                      ? 'border-brand bg-brand/5'
                      : p.isOutOfDomain
                        ? 'border-orange-200 bg-orange-50/30 hover:bg-orange-50'
                        : 'border-border hover:bg-muted/50'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleSelect(p.id)}
                    className="mt-1 h-4 w-4 rounded border-gray-300 text-brand focus:ring-brand"
                  />

                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start gap-2">
                      <span className="text-sm font-semibold truncate group-hover:text-brand transition-colors">
                        {title}
                      </span>
                      <span className="text-xs font-bold whitespace-nowrap">
                        {typeof priceCents === 'number'
                          ? `${(priceCents / 100).toFixed(2).replace('.', ',')}€`
                          : '—'}
                      </span>
                    </div>
                    {desc && (
                      <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5 leading-relaxed">
                        {desc}
                      </p>
                    )}
                    {p.isOutOfDomain && (
                      <span className="inline-block mt-1 text-[10px] uppercase tracking-wider font-bold text-orange-600 bg-orange-100 px-1.5 py-0.5 rounded">
                        Hors domaine
                      </span>
                    )}
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
