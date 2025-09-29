// src/interface/components/profile/PrestationsList.tsx
import React from 'react';
import type { PrestationDto } from '../../../domain/catalog/types';
import { getStringField, getNumberField } from '../../../shared/utils/obj';

type Props = {
  prestations: PrestationDto[] | 'loading' | null;
};

export default function PrestationsList({ prestations }: Props) {
  return (
    <section className="p-4 border rounded">
      <h3 className="font-medium">Services proposés</h3>

      <div className="mt-4">
        {prestations === 'loading' ? (
          <p>Chargement des services…</p>
        ) : prestations === null ? (
          <p>Impossible de charger les services pour le moment.</p>
        ) : prestations.length === 0 ? (
          <p>Aucun service renseigné.</p>
        ) : (
          <ul className="grid gap-3">
            {prestations.map((p) => {
              const title =
                getStringField(p, 'name', 'title', 'label') ??
                `Service #${p.id}`;
              const desc = getStringField(
                p,
                'short_description',
                'description',
              );
              const priceCents = getNumberField(p, 'price_cents');

              return (
                <li key={p.id} className="p-3 border rounded">
                  <div className="flex justify-between items-start">
                    <div>
                      <strong className="block text-lg">{title}</strong>
                      {desc && <p className="text-sm mt-1">{desc}</p>}
                    </div>
                    <div className="text-right">
                      {priceCents != null ? (
                        <div className="text-sm font-medium">
                          {(priceCents / 100).toFixed(2)} €
                        </div>
                      ) : null}
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </section>
  );
}
