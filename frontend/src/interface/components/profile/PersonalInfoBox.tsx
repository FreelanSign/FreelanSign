// src/interface/components/profile/PersonalInfoBox.tsx
import React from 'react';
import type { UserDto } from '../../../domain/user/types';

type Props = {
  user: UserDto | null;
  authEmail?: string | null;
  onEdit?: () => void;
};

export default function PersonalInfoBox({ user, authEmail, onEdit }: Props) {
  const profile = user?.profile ?? null;
  const displayName =
    profile && (profile.first_name || profile.last_name)
      ? `${profile.first_name ?? ''} ${profile.last_name ?? ''}`.trim()
      : '—';

  return (
    <section className="p-4 border rounded max-w-2xl">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="font-medium">Utilisateur</h2>
          <p className="mt-2">
            <strong>Email :</strong> {user?.email ?? authEmail ?? '—'}
          </p>
          <p>
            <strong>Nom :</strong> {displayName}
          </p>
          <p>
            <strong>Téléphone :</strong> {profile?.phone ?? '—'}
          </p>
          {profile?.avatar_url && (
            <img
              src={profile.avatar_url}
              alt="avatar"
              className="w-24 h-24 rounded-full mt-2"
            />
          )}
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
