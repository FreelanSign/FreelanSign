// src/interface/pages/ProfileEditPage.tsx
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider';
import { userRepository } from '../../infrastructure/user/userRepository';
import { catalogRepository } from '../../infrastructure/catalog/catalogRepository';
import type { UserDto, ProfessionalUserDto } from '../../domain/user/types';
import type { AreaDto, PrestationDto } from '../../domain/catalog/types';

import PersonalUserDataForm from '../components/profile/PersonalUserDataForm';
import ProfessionalUserDataForm from '../components/profile/ProfessionalUserDataForm';

function Chip({ label, selected, onClick }: { label: string; selected: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-3 py-1 rounded-full text-sm border transition ${
        selected ? 'bg-black text-white border-black' : 'bg-white text-gray-800 border-gray-300'
      }`}
    >
      {label}
    </button>
  );
}

export default function ProfileEditPage() {
  const navigate = useNavigate();
  const { user: authUser } = useAuth();

  const [user, setUser] = useState<UserDto | null>(null);
  const [professional, setProfessional] = useState<ProfessionalUserDto | null | 'loading'>('loading');
  const [areas, setAreas] = useState<AreaDto[] | null>(null);
  const [prestations, setPrestations] = useState<PrestationDto[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        const me = await userRepository.getMe();
        if (!mounted) return;
        setUser(me);

        const prof = await userRepository.getProfessionalMe();
        if (!mounted) return;
        setProfessional(prof ?? null);

        const areasList = await catalogRepository.listAreas();
        if (!mounted) return;
        setAreas(areasList);

        // initial prestations: if pro has domaine -> fetch filtered, else empty array
        if (prof && prof.domaine) {
          try {
            const p = await catalogRepository.listPrestations({ area: prof.domaine });
            if (!mounted) return;
            setPrestations(p);
          } catch {
            // fallback: get all & filter client-side
            const all = await catalogRepository.listPrestations();
            if (!mounted) return;
            setPrestations(all.filter((x) => (x.area ?? x.area_id ?? (x as any).area?.id) === prof.domaine));
          }
        } else {
          setPrestations([]);
        }
      } catch (err) {
        console.error('ProfileEdit load error', err);
        if (mounted) {
          setAreas(null);
          setPrestations(null);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => {
      mounted = false;
    };
  }, []);

  // fetch prestations for a given area id (null => clear)
  async function onDomaineChangeFetch(areaId: number | null) {
    if (areaId == null) {
      setPrestations([]);
      return;
    }
    try {
      const p = await catalogRepository.listPrestations({ area: areaId });
      setPrestations(p);
    } catch (err) {
      // fallback client-side filtering
      try {
        const all = await catalogRepository.listPrestations();
        setPrestations(all.filter((x) => (x.area ?? x.area_id ?? (x as any).area?.id) === areaId));
      } catch (e) {
        console.warn('Impossible de charger prestations pour area', areaId, e);
        setPrestations(null);
      }
    }
  }

  // called when the professional form is saved (submit)
  async function handleProfessionalSaved(payload: {
    name?: string | null;
    status_juridique?: string | null;
    domaine?: number | null;
    tjm_cents?: number | null;
    number_pro?: string | null;
    service_types?: number[] | null;
  }) {
    await userRepository.updateProfessionalMe(payload);
    const prof = await userRepository.getProfessionalMe();
    setProfessional(prof ?? null);

    if (payload.domaine) {
      await onDomaineChangeFetch(payload.domaine);
    } else {
      setPrestations([]);
    }
  }

  // service_types management: toggle selection (local update)
  function toggleServiceTypeLocal(id: number) {
    if (!professional || professional === 'loading') return;
    const current = professional.service_types ?? [];
    const next = current.includes(id) ? current.filter((v) => v !== id) : [...current, id];
    setProfessional({ ...(professional as ProfessionalUserDto), service_types: next });
  }

  async function saveServiceTypesToBackend() {
    if (!professional || professional === 'loading') return;
    await userRepository.updateProfessionalMe({ service_types: professional.service_types ?? [] });
    const prof = await userRepository.getProfessionalMe();
    setProfessional(prof ?? null);
    alert('Services mis à jour');
  }

  if (loading) {
    return <main className="container p-6">Chargement…</main>;
  }

  return (
    <main className="container mx-auto p-6 grid gap-6">
      <header className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Modifier mon profil</h1>
        <div>
          <a href="/profile" className="text-sm text-blue-600">
            Voir mon profil
          </a>
        </div>
      </header>

      <section className="p-4 border rounded max-w-2xl">
        <h2 className="font-medium mb-2">Informations personnelles</h2>
        <PersonalUserDataForm
          initialValues={user?.profile ?? {}}
          onSave={async (vals) => {
            await userRepository.updateMe({ profile: vals });
            const me = await userRepository.getMe();
            setUser(me);
            alert('Informations personnelles mises à jour');
          }}
          onCancel={() => navigate('/profile')}
        />
      </section>

      <section className="p-4 border rounded max-w-3xl">
        <h2 className="font-medium mb-2">Compte professionnel</h2>

        {professional === 'loading' ? (
          <div>Chargement…</div>
        ) : professional ? (
          <>
            <ProfessionalUserDataForm
              initialValues={{
                name: professional.name ?? null,
                status_juridique: professional.status_juridique ?? null,
                domaine: professional.domaine ?? null,
                tjm_cents: professional.tjm_cents ?? undefined,
                number_pro: professional.number_pro ?? null,
                service_types: professional.service_types ?? [],
              } as any}
              areas={areas}
              onSave={async (payload) => {
                await handleProfessionalSaved(payload);
                alert('Compte professionnel mis à jour');
              }}
              onDomaineChange={async (areaId) => {
                // persist domaine immediately (PATCH partial) so DB is in sync
                try {
                  // ensure we send either number or null
                  const domainePayload = { domaine: areaId == null ? null : areaId };
                  await userRepository.updateProfessionalMe(domainePayload);
                  // refresh professional from backend
                  const prof = await userRepository.getProfessionalMe();
                  setProfessional(prof ?? null);
                } catch (err) {
                  console.error('Failed to persist domaine change', err);
                }

                // then refresh prestations for UI
                try {
                  await onDomaineChangeFetch(areaId);
                } catch (err) {
                  console.warn('Fetching prestations after domaine change failed', err);
                }
              }}
              onCancel={() => navigate('/profile')}
            />

            <div className="mt-6">
              <h3 className="font-medium">Prestations pour le domaine sélectionné</h3>
              <p className="text-sm text-gray-500">Sélectionnez les services proposés pour ce domaine.</p>

              <div className="mt-3 grid gap-2" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))' }}>
                {prestations === null ? (
                  <div>Impossible de charger les prestations.</div>
                ) : prestations.length === 0 ? (
                  <div>Aucune prestation pour ce domaine.</div>
                ) : (
                  prestations.map((p) => {
                    const id = p.id;
                    const label = p.name ?? p.title ?? `Service #${id}`;
                    const selected = (professional.service_types ?? []).includes(id);
                    return (
                      <div key={id} className="flex items-center justify-between gap-2">
                        <Chip label={label} selected={selected} onClick={() => toggleServiceTypeLocal(id)} />
                      </div>
                    );
                  })
                )}
              </div>

              <div className="flex gap-3 mt-4">
                <button onClick={() => saveServiceTypesToBackend()} className="bg-blue-600 text-white rounded px-3 py-2">
                  Enregistrer les services
                </button>
              </div>
            </div>
          </>
        ) : (
          <div>
            <p>Vous n'avez pas encore de profil professionnel.</p>
            <button onClick={() => navigate('/onboarding-professional')} className="underline text-blue-600 mt-2">
              Commencer l'onboarding
            </button>
          </div>
        )}
      </section>
    </main>
  );
}
