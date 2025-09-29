// src/interface/components/profile/ProfessionalInfoBox.tsx
import React from 'react';
import type { ProfessionalUserDto } from '../../../domain/user/types';

type Props = {
  professional: ProfessionalUserDto | null | 'loading';
  areaName?: string | null;
  onEdit?: () => void;
};

export default function ProfessionalInfoBox({
  professional,
  areaName,
  onEdit,
}: Props) {
  if (professional === 'loading') {
    return (
      <section className="p-4 border rounded">
        <h2 className="font-medium">Compte professionnel</h2>
        <p className="mt-2">Chargement…</p>
      </section>
    );
  }

  if (!professional) {
    return (
      <section className="p-4 border rounded">
        <h2 className="font-medium">Compte professionnel</h2>
        <p className="mt-2">
          Vous n'avez pas encore de profil professionnel.{' '}
          {onEdit ? (
            <button onClick={onEdit} className="underline text-blue-600">
              Commencer l'onboarding
            </button>
          ) : null}
        </p>
      </section>
    );
  }

  return (
    <section className="p-4 border rounded">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="font-medium">Compte professionnel</h2>

          <p className="mt-2">
            <strong>Nom structure :</strong> {professional.name ?? '—'}
          </p>
          <p>
            <strong>Statut juridique :</strong>{' '}
            {professional.status_juridique ?? '—'}
          </p>
          <p>
            <strong>Domaine :</strong> {areaName ?? '—'}
          </p>
          <p>
            <strong>TJM :</strong>{' '}
            {professional.tjm_cents
              ? (professional.tjm_cents / 100).toFixed(2) + ' €'
              : '—'}
          </p>
          <p>
            <strong>Numéro pro :</strong> {professional.number_pro ?? '—'}
          </p>
          <p>
            <strong>Crée le :</strong> {professional.created_at ?? '—'}
          </p>
        </div>

        {onEdit ? (
          <div>
            <button
              onClick={onEdit}
              className="bg-yellow-500 text-white rounded px-3 py-2"
            >
              Modifier
            </button>
          </div>
        ) : null}
      </div>
    </section>
  );
}
