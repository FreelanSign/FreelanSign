// src/interface/pages/ProfilePage.tsx
import { useEffect, useState } from 'react';
import { userRepository } from '../../../infrastructure/user/userRepository';
import { catalogRepository } from '../../../infrastructure/catalog/catalogRepository';
import type { UserDto, ProfessionalUserDto } from '../../../domain/user/types';
import type { PrestationDto } from '../../../domain/catalog/types';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';

import PersonalInfoBox from '../../components/profile/PersonalInfoBox';
import ProfessionalInfoBox from '../../components/profile/ProfessionalInfoBox';
import PrestationsList from '../../components/profile/PrestationList';
import Navbar from '../../components/navbar/Navbar';

/**
 * Page profil: affiche user.profile + professional (si présent)
 * et liste détaillée des prestations liées au professional.
 */

export default function ProfilePage() {
  const { user: authUser } = useAuth();
  const [user, setUser] = useState<UserDto | null>(null);
  const [professional, setProfessional] = useState<
    ProfessionalUserDto | null | 'loading'
  >('loading');
  const [prestations, setPrestations] = useState<
    PrestationDto[] | 'loading' | null
  >(null);
  const [areaName, setAreaName] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // helper type-guard
  function isApiError(e: unknown): e is { response?: { status?: number } } {
    return (
      typeof e === 'object' &&
      e !== null &&
      'response' in e &&
      typeof (e as Record<string, unknown>).response === 'object'
    );
  }

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        const me = await userRepository.getMe();
        if (!mounted) return;
        setUser(me);

        const prof = await userRepository.getProfessionalMe();
        if (!mounted) return;
        setProfessional(prof ?? null);

        if (prof) {
          setPrestations('loading');

          const ids = prof.service_types ?? [];
          try {
            const prestationsResult =
              await catalogRepository.getPrestationsByIds(ids);
            if (!mounted) return;
            setPrestations(prestationsResult);
          } catch (err) {
            console.error('Erreur récupération prestations', err);
            if (!mounted) return;
            setPrestations(null);
          }

          try {
            const domaineId = prof.domaine as unknown as number | null;
            const area = await catalogRepository.getAreaById(domaineId);
            if (!mounted) return;
            setAreaName(area?.name ?? null);
          } catch (err) {
            console.warn('Erreur récupération domaine', err);
            if (!mounted) return;
            setAreaName(null);
          }
        }
      } catch (e: unknown) {
        if (isApiError(e) && e.response?.status === 401) {
          navigate('/login', { replace: true });
        } else {
          console.error('ProfilePage load error', e);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => {
      mounted = false;
    };
  }, [navigate]);

  if (loading)
    return <main className="container p-6">Chargement du profil…</main>;

  return (
    <>
      <Navbar />
      <main className="container mx-auto p-6 grid gap-6">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Mon profil</h1>
            <p className="text-sm text-gray-600">
              {user?.email ?? authUser?.email ?? '—'}
            </p>
          </div>

          <div className="flex gap-2">
            {/* Unique bouton Modifier centralisé */}
            <button
              onClick={() => navigate('/profile/edit')}
              className="bg-yellow-500 text-white rounded px-3 py-2"
            >
              Modifier
            </button>

            {/* lien secondaire 'Voir mon profil' si tu veux le garder */}
            <a href="/profile" className="text-sm text-blue-600 self-center">
              Voir mon profil
            </a>
          </div>
        </header>

        <PersonalInfoBox
          user={user}
          authEmail={authUser?.email ?? null}
          /* plus d'onEdit passé ici */
        />

        <div className="grid gap-6">
          <ProfessionalInfoBox
            professional={professional}
            areaName={areaName}
            /* plus d'onEdit passé ici */
          />

          {/* Prestations list is shown only when professional exists (we still accept 'loading' state) */}
          {professional === 'loading' ? null : professional ? (
            <PrestationsList prestations={prestations} />
          ) : null}
        </div>
      </main>
    </>
  );
}
