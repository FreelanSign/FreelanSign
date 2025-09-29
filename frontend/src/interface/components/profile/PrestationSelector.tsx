// src/interface/components/profile/PrestationsSelector.tsx
import React, { useEffect, useMemo, useState } from 'react';
import type { PrestationDto } from '../../../domain/catalog/types';
import { catalogRepository } from '../../../infrastructure/catalog/catalogRepository';

// helper: extraire area id depuis plusieurs shapes possibles d'une prestation
function getPrestationAreaId(p: unknown): number | null {
  if (!p || typeof p !== 'object') return null;
  const obj = p as Record<string, unknown>;

  // cas 1: area est un number
  if (typeof obj['area'] === 'number') return obj['area'] as number;

  // cas 2: area_id est un number
  if (typeof obj['area_id'] === 'number') return obj['area_id'] as number;

  // cas 3: area est un objet { id: number }
  const areaObj = obj['area'];
  if (areaObj && typeof areaObj === 'object') {
    const a = areaObj as Record<string, unknown>;
    if (typeof a['id'] === 'number') return a['id'] as number;
    // parfois id est string -> essayer de parser
    if (typeof a['id'] === 'string') {
      const n = Number(a['id']);
      return Number.isNaN(n) ? null : n;
    }
  }

  // non trouvé
  return null;
}

type Props = {
  // current professional id (used e.g. to persist filters if needed) - kept in the type for future use
  professionalId?: number | null;
  // domaine currently selected in the professional info (used as default filter)
  domaine?: number | null;
  // initial selected prestation ids (from professional.service_types)
  initialSelected?: number[];
  // callback called when selection changes (immediate)
  onChange?: (ids: number[]) => void;
  // callback for save action (optional)
  onSave?: (ids: number[]) => Promise<void> | void;
};

/** safe helpers to read possibly-variant backend shapes without `any` */
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

export default function PrestationsSelector({
  // note: we don't destructure professionalId because it's unused for now (keeps lint clean).
  domaine = null,
  initialSelected = [],
  onChange,
}: Props) {
  const [prestations, setPrestations] = useState<PrestationDto[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [search, setSearch] = useState<string>('');
  const [applyDomaineFilter, setApplyDomaineFilter] = useState<boolean>(true);
  const [onlySelected, setOnlySelected] = useState<boolean>(false);
  const [selected, setSelected] = useState<number[]>(initialSelected ?? []);

  // sync initialSelected if it changes
  useEffect(() => {
    setSelected(initialSelected ?? []);
  }, [initialSelected]);

  // helper to actually load prestations given current filters
  async function loadPrestations() {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {};
      if (applyDomaineFilter && domaine != null) params.area = domaine;
      if (search.trim() !== '') params.search = search.trim();
      // call repository with params (the repo should accept optional params)
      // If your catalogRepository.listPrestations signature doesn't accept params yet,
      // either update it or replace this call by a dedicated API function.
      // We'll call it with params; if it throws, we fallback to the no-param call below.
      try {
        // @ts-expect-error allow optional params call (adjust repo signature if needed)
        const lista = await catalogRepository.listPrestations(params);
        setPrestations(lista);
      } catch {
        // fallback to unfiltered call and do client-side filtering
        const all = await catalogRepository.listPrestations();
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
      console.warn('Prestations load failed', err);
      setPrestations(null);
    } finally {
      setLoading(false);
    }
  }

  // load whenever domaine / applyDomaineFilter / search change
  useEffect(() => {
    loadPrestations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [domaine, applyDomaineFilter, search]);

  // toggles selection
  function toggleSelect(id: number) {
    setSelected((cur) => {
      const next = cur.includes(id)
        ? cur.filter((x) => x !== id)
        : [...cur, id];
      if (onChange) onChange(next);
      return next;
    });
  }

  // compute displayed list based on onlySelected toggle
  const displayed = useMemo(() => {
    if (!prestations) return [];
    if (!onlySelected) return prestations;
    return prestations.filter((p) => selected.includes(p.id));
  }, [prestations, onlySelected, selected]);

  return (
    <section className="p-4 border rounded">
      <div className="flex justify-between items-center">
        <h3 className="font-medium">Prestations</h3>
        {/* bouton Enregistrer géré par le parent (ProfileEditPage) */}
      </div>

      <div className="mt-3 grid gap-2">
        <div className="flex gap-2 items-center">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher un service..."
            className="border p-2 rounded w-full"
            aria-label="Rechercher une prestation"
          />
        </div>

        <div className="flex gap-3 items-center">
          <label className="text-sm flex items-center gap-2">
            <input
              type="checkbox"
              checked={applyDomaineFilter}
              onChange={(e) => setApplyDomaineFilter(e.target.checked)}
            />
            Filtrer par domaine sélectionné
          </label>

          <label className="text-sm flex items-center gap-2">
            <input
              type="checkbox"
              checked={onlySelected}
              onChange={(e) => setOnlySelected(e.target.checked)}
            />
            Montrer uniquement mes sélections
          </label>
        </div>

        <div>
          {loading ? (
            <div>Chargement des prestations…</div>
          ) : prestations === null ? (
            <div>Impossible de charger les prestations.</div>
          ) : displayed.length === 0 ? (
            <div>Aucune prestation.</div>
          ) : (
            <div className="grid gap-2">
              {displayed.map((p) => {
                const title =
                  getStringField(p, 'name', 'title') ?? `Service #${p.id}`;
                const desc =
                  getStringField(p, 'description', 'short_description') ?? '';
                const priceCents = getNumberField(
                  p,
                  'default_rate_cents',
                  'price_cents',
                );
                return (
                  <label
                    key={p.id}
                    className="flex items-center justify-between gap-2 p-2 border rounded"
                  >
                    <div>
                      <div className="font-medium">{title}</div>
                      <div className="text-sm text-gray-600">{desc}</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm">
                        {typeof priceCents === 'number'
                          ? (priceCents / 100).toFixed(2) + ' €'
                          : null}
                      </span>
                      <input
                        type="checkbox"
                        checked={selected.includes(p.id)}
                        onChange={() => toggleSelect(p.id)}
                      />
                    </div>
                  </label>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
