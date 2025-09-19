// src/interface/pages/ProfileEditPage.tsx
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '../../app/providers/AuthProvider';
import { userRepository } from '../../infrastructure/user/userRepository';
import { catalogRepository } from '../../infrastructure/catalog/catalogRepository';
import type { ProfessionalUserDto, UserDto } from '../../domain/user/types';
import type { PrestationDto, AreaDto } from '../../domain/catalog/types';

/**
 * Page d'édition du profil utilisateur & professionnel.
 * - Récupère les données (prefill)
 * - Permet patcher user.profile et professional
 * - Feedback minimal (success / error)
 */

// ------- schemas Zod pour validation -------
const ProfileSchema = z.object({
  first_name: z.string().optional().nullable(),
  last_name: z.string().optional().nullable(),
  phone: z.string().optional().nullable(),
  birthday: z.string().optional().nullable(), // YYYY-MM-DD
  avatar_url: z.string().url().optional().nullable(),
});

const ProfessionalSchema = z.object({
  name: z.string().optional().nullable(),
  status_juridique: z.string().optional().nullable(),
  domaine: z.number().nullable().optional(),
  // tjm en euros côté formulaire (number) -> convert to cents at submit
  tjm_eur: z.number().nonnegative().nullable().optional(),
  number_pro: z.string().optional().nullable(),
  service_types: z.array(z.number()).optional().nullable(),
});

type ProfileForm = z.infer<typeof ProfileSchema>;
type ProfessionalForm = z.infer<typeof ProfessionalSchema>;

function getErrorMessage(err: unknown): string {
  if (err instanceof Error) return err.message;
  // try to stringify common response shapes
  try {
    return JSON.stringify(err);
  } catch {
    return String(err);
  }
}

export default function ProfileEditPage() {
  const navigate = useNavigate();
  const { user: authUser } = useAuth();

  // keep the user state (we now use it in the UI below)
  const [user, setUser] = useState<UserDto | null>(null);
  const [professional, setProfessional] = useState<
    ProfessionalUserDto | null | 'loading'
  >('loading');
  const [prestationsList, setPrestationsList] = useState<
    PrestationDto[] | null
  >(null);
  const [areasList, setAreasList] = useState<AreaDto[] | null>(null);

  // react-hook-form instances
  const profileForm = useForm<ProfileForm>({
    resolver: zodResolver(ProfileSchema),
  });
  const profForm = useForm<ProfessionalForm>({
    resolver: zodResolver(ProfessionalSchema),
  });

  // destructure the stable methods we'll call in the effect to avoid unnecessary reruns
  const { reset: resetProfile } = profileForm;
  const { reset: resetProf } = profForm;

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const me = await userRepository.getMe();
        if (!mounted) return;
        setUser(me);
        // Pré-remplissage du form profile (use reset from hook)
        resetProfile(me.profile ?? {});

        // Récup professional
        const prof = await userRepository.getProfessionalMe();
        if (!mounted) return;
        setProfessional(prof ?? null);

        if (prof) {
          // Pré-remplir professional form
          resetProf({
            name: prof.name ?? null,
            status_juridique: prof.status_juridique ?? null,
            domaine: prof.domaine ?? null,
            tjm_eur: prof.tjm_cents != null ? prof.tjm_cents / 100 : null,
            number_pro: prof.number_pro ?? null,
            service_types: prof.service_types ?? [],
          });

          // Récupérer listes pour selects (areas & prestations)
          try {
            const [prestations, areas] = await Promise.all([
              catalogRepository.listPrestations(),
              catalogRepository.listAreas(),
            ]);
            if (!mounted) return;
            setPrestationsList(prestations);
            setAreasList(areas);
          } catch (err: unknown) {
            console.warn('Impossible de charger catalogues', err);
            setPrestationsList(null);
            setAreasList(null);
          }
        }
      } catch (err: unknown) {
        console.error('ProfileEdit load error', getErrorMessage(err));
      }
    })();
    return () => {
      mounted = false;
    };
    // resetProfile & resetProf are stable references provided by react-hook-form,
    // include them to satisfy exhaustive-deps and avoid lint warning.
  }, [navigate, resetProfile, resetProf]);

  // Soumission du formulaire
  async function onSubmitAll() {
    // On récupère les valeurs validées des deux forms
    const profileValues = profileForm.getValues();
    const profValues = profForm.getValues();

    try {
      // Update profile (on envoie { profile: {...} })
      await userRepository.updateMe({ profile: profileValues });

      // Update professional si présent
      if (professional && professional !== 'loading') {
        // Convert tjm_eur -> tjm_cents
        const payload: Partial<ProfessionalUserDto> = {
          name: profValues.name ?? null,
          status_juridique: profValues.status_juridique ?? null,
          domaine: profValues.domaine ?? null,
          number_pro: profValues.number_pro ?? null,
        };
        if (typeof profValues.tjm_eur === 'number') {
          payload.tjm_cents = Math.round(profValues.tjm_eur * 100);
        }
        if (Array.isArray(profValues.service_types)) {
          payload.service_types = profValues.service_types;
        }
        await userRepository.updateProfessionalMe(payload);
      }

      // Après succès : redirige vers /profile
      navigate('/profile', { replace: true });
    } catch (err: unknown) {
      console.error('Update error', getErrorMessage(err));
      // TODO: remplacer alert par un toast/inline errors
      alert('Erreur lors de la mise à jour : ' + getErrorMessage(err));
    }
  }

  return (
    <main className="container mx-auto p-6 grid gap-6">
      <h1 className="text-2xl font-semibold">Modifier mon profil</h1>

      {/* UTILISATION DE user / authUser pour éviter l'erreur "assigned but never used" */}
      <p className="text-sm text-gray-600">
        Compte : {user?.email ?? authUser?.email ?? '—'}
      </p>

      {/* FORM PROFILE */}
      <section className="p-4 border rounded max-w-lg">
        <h2 className="font-medium">Informations personnelles</h2>

        <form
          onSubmit={profileForm.handleSubmit(() => {})}
          className="grid gap-3 mt-3"
        >
          <label>
            <div className="text-sm">Prénom</div>
            <input
              {...profileForm.register('first_name')}
              className="border p-2 rounded w-full"
            />
          </label>

          <label>
            <div className="text-sm">Nom</div>
            <input
              {...profileForm.register('last_name')}
              className="border p-2 rounded w-full"
            />
          </label>

          <label>
            <div className="text-sm">Téléphone</div>
            <input
              {...profileForm.register('phone')}
              className="border p-2 rounded w-full"
            />
          </label>

          <label>
            <div className="text-sm">Date de naissance</div>
            <input
              {...profileForm.register('birthday')}
              type="date"
              className="border p-2 rounded w-full"
            />
          </label>

          <label>
            <div className="text-sm">Avatar (URL)</div>
            <input
              {...profileForm.register('avatar_url')}
              className="border p-2 rounded w-full"
            />
          </label>
        </form>
      </section>

      {/* FORM PROFESSIONAL */}
      {professional === 'loading' ? (
        <div>Chargement professionnel…</div>
      ) : professional ? (
        <section className="p-4 border rounded max-w-2xl">
          <h2 className="font-medium">Compte professionnel</h2>

          <form
            onSubmit={profForm.handleSubmit(() => {})}
            className="grid gap-3 mt-3"
          >
            <label>
              <div className="text-sm">Nom structure</div>
              <input
                {...profForm.register('name')}
                className="border p-2 rounded w-full"
              />
            </label>

            <label>
              <div className="text-sm">Statut juridique</div>
              <input
                {...profForm.register('status_juridique')}
                className="border p-2 rounded w-full"
              />
            </label>

            <label>
              <div className="text-sm">Domaine</div>
              <select
                {...profForm.register('domaine')}
                className="border p-2 rounded w-full"
              >
                <option value="">-- Aucune --</option>
                {Array.isArray(areasList) && areasList.length > 0 ? (
                  areasList.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name ?? a.slug ?? `Area ${a.id}`}
                    </option>
                  ))
                ) : (
                  <option value="">
                    {areasList == null
                      ? 'Chargement impossible'
                      : 'Aucune area disponible'}
                  </option>
                )}
              </select>
            </label>

            <label>
              <div className="text-sm">TJM (EUR)</div>
              <input
                type="number"
                step="0.01"
                {...profForm.register('tjm_eur', { valueAsNumber: true })}
                className="border p-2 rounded w-full"
              />
            </label>

            <label>
              <div className="text-sm">Numéro pro (SIRET / TVA)</div>
              <input
                {...profForm.register('number_pro')}
                className="border p-2 rounded w-full"
              />
            </label>

            <label>
              <div className="text-sm">Services proposés</div>
              <div className="grid gap-1">
                {prestationsList === null ? (
                  <div>Impossible de charger la liste des services.</div>
                ) : !Array.isArray(prestationsList) ||
                  prestationsList.length === 0 ? (
                  <div>Aucune prestation disponible.</div>
                ) : (
                  prestationsList.map((p) => (
                    <label key={p.id} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        value={String(p.id)}
                        onChange={(e) => {
                          const val = Number(e.target.value);
                          const current =
                            profForm.getValues('service_types') ?? [];
                          if (e.target.checked) {
                            profForm.setValue('service_types', [
                              ...current,
                              val,
                            ]);
                          } else {
                            profForm.setValue(
                              'service_types',
                              current.filter((id) => id !== val),
                            );
                          }
                        }}
                        checked={(
                          profForm.getValues('service_types') ?? []
                        ).includes(p.id)}
                      />
                      <span>{p.name ?? p.title ?? `Service #${p.id}`}</span>
                    </label>
                  ))
                )}
              </div>
            </label>

            <div className="flex gap-3 mt-4">
              <button
                type="button"
                onClick={() => onSubmitAll()}
                className="bg-blue-600 text-white rounded px-3 py-2"
              >
                Enregistrer
              </button>

              <button
                type="button"
                onClick={() => navigate('/profile')}
                className="bg-gray-200 rounded px-3 py-2"
              >
                Annuler
              </button>
            </div>
          </form>
        </section>
      ) : (
        <section className="p-4 border rounded">
          <p>
            Vous n'avez pas encore de profil professionnel.{' '}
            <button
              onClick={() => navigate('/onboarding-professional')}
              className="underline"
            >
              Commencer l'onboarding
            </button>
          </p>
        </section>
      )}
    </main>
  );
}
