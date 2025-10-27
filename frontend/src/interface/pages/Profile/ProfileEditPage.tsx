// src/interface/pages/ProfileEditPage.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';
import { userRepository } from '../../../infrastructure/user/userRepository';
import { catalogRepository } from '../../../infrastructure/catalog/catalogRepository';
import type { UserDto, ProfessionalUserDto } from '../../../domain/user/types';
import type { AreaDto } from '../../../domain/catalog/types';

import PersonalUserDataForm, {
  type PersonalUserFormValues,
} from '../../components/profile/PersonalUserDataForm';
import ProfessionalInfoForm, {
  type ProfessionalInfoValues,
} from '../../components/profile/ProfessionalInfoForm';
import PrestationsSelector from '../../components/profile/PrestationSelector';

export default function ProfileEditPage() {
  const navigate = useNavigate();
  const { user: authUser } = useAuth();

  const [user, setUser] = useState<UserDto | null>(null);
  const [professional, setProfessional] = useState<
    ProfessionalUserDto | null | 'loading'
  >('loading');
  const [areas, setAreas] = useState<AreaDto[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Draft values kept locally until Save All
  // include both tjm_cents and tjm_eur to avoid any casts later
  type ProDraftType = Partial<
    ProfessionalInfoValues & { tjm_cents?: number; tjm_eur?: number }
  >;
  const [proDraft, setProDraft] = useState<ProDraftType>({});
  const [selectedServiceIds, setSelectedServiceIds] = useState<number[]>([]);

  // NEW: profile draft tracked so Save All can persist profile + pro
  const [profileDraft, setProfileDraft] = useState<
    Partial<PersonalUserFormValues>
  >({});

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        const me = await userRepository.getMe();
        if (!mounted) return;
        setUser(me);

        // initialize profileDraft from backend values
        setProfileDraft(me?.profile ?? {});

        const prof = await userRepository.getProfessionalMe();
        if (!mounted) return;
        setProfessional(prof ?? null);
        setSelectedServiceIds(prof?.service_type_ids ?? []);
        // init draft from backend values
        setProDraft({
          name: prof?.name ?? null,
          status_juridique: prof?.status_juridique ?? null,
          domaine: prof?.domaine ?? null,
          tjm_cents: prof?.tjm_cents ?? undefined,
          number_pro: prof?.number_pro ?? null,
        });

        const areasList = await catalogRepository.listAreas();
        if (!mounted) return;
        setAreas(areasList);
      } catch (err) {
        console.error('ProfileEdit load error', err);
        if (mounted) {
          setAreas(null);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, [navigate]);

  // called by ProfessionalInfoForm watch - update local draft and domaine used to fetch prestations
  function handleProValuesChange(values: ProfessionalInfoValues) {
    setProDraft((prev) => ({
      ...prev,
      name: values.name ?? null,
      status_juridique: values.status_juridique ?? null,
      domaine: values.domaine ?? null,
      // use undefined (not null) to match the state's tjm_eur type
      tjm_eur: values.tjm_eur ?? undefined,
      number_pro: values.number_pro ?? null,
    }));
  }

  // called when domaine changes (immediate) => update local draft and re-fetch prestations in PrestationsSelector (it uses domaine prop)
  function handleDomaineChange(domaine: number | null) {
    setProDraft((d) => ({ ...d, domaine }));
    // NOTE: we DON'T persist to backend here (single save), but PrestationsSelector will get updated domaine prop
  }

  // Save payload type (avoid any)
  type SavePayload = {
    name?: string | null;
    status_juridique?: string | null;
    domaine?: number | null;
    number_pro?: string | null;
    service_type_ids?: number[];
    tjm_cents?: number | null;
  };

  // helper: normalise profile fields (convert '' -> null)
  const normalizeProfile = (p: Partial<PersonalUserFormValues>) => ({
    first_name: p.first_name && p.first_name !== '' ? p.first_name : null,
    last_name: p.last_name && p.last_name !== '' ? p.last_name : null,
    phone: p.phone && p.phone !== '' ? p.phone : null,
    birthday: p.birthday && p.birthday !== '' ? p.birthday : null,
    avatar_url: p.avatar_url && p.avatar_url !== '' ? p.avatar_url : null,
  });

  // central save all
  async function handleSaveAll() {
    try {
      setSaving(true);

      // 0) determine if profile changed vs current backend user
      const currentProfile = user?.profile ?? {};
      const profileChanged =
        JSON.stringify(profileDraft ?? {}) !== JSON.stringify(currentProfile);

      // 1) if profile changed, persist it first
      if (profileChanged) {
        const normalized = normalizeProfile(profileDraft ?? {});
        await userRepository.updateMe({ profile: normalized });

        // re-fetch me to update local user state (and to keep canonical source)
        const me = await userRepository.getMe();
        setUser(me);
        // ensure profileDraft reflect canonical state (avoid drift)
        setProfileDraft(me?.profile ?? {});
      }

      // 2) build payload for professional (existing code)
      const payload: SavePayload = {
        name: proDraft.name ?? null,
        status_juridique: proDraft.status_juridique ?? null,
        domaine: proDraft.domaine ?? null,
        number_pro: proDraft.number_pro ?? null,
        service_type_ids: selectedServiceIds ?? [],
        tjm_cents: null,
      };

      // convert tjm_eur (if provided) to tjm_cents
      if (typeof proDraft.tjm_eur === 'number') {
        payload.tjm_cents = Math.round(proDraft.tjm_eur * 100);
      } else if (typeof proDraft.tjm_cents === 'number') {
        payload.tjm_cents = proDraft.tjm_cents;
      } else {
        payload.tjm_cents = null;
      }

      // single PATCH with everything for professional
      await userRepository.updateProfessionalMe(payload);

      // re-fetch professional
      const prof = await userRepository.getProfessionalMe();
      setProfessional(prof ?? null);
      setSelectedServiceIds(prof?.service_type_ids ?? []);
      // update draft with persisted values
      setProDraft({
        name: prof?.name ?? null,
        status_juridique: prof?.status_juridique ?? null,
        domaine: prof?.domaine ?? null,
        tjm_cents: prof?.tjm_cents ?? undefined,
        number_pro: prof?.number_pro ?? null,
      });

      // navigate to profile page after successful save
      navigate('/profile', { replace: true });
    } catch (err) {
      console.error('Save all failed', err);
      alert(
        'Erreur lors de la sauvegarde: ' +
          (err instanceof Error ? err.message : String(err)),
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <main className="container p-6">Chargement…</main>;

  return (
    <main className="container mx-auto p-6 grid gap-6">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold">Modifier mon profil</h1>
          {/* use authUser here so the variable is used (fixes the lint error) */}
          <p className="text-sm text-gray-600">
            {user?.email ?? authUser?.email ?? '—'}
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => handleSaveAll()}
            className="bg-green-600 text-white rounded px-3 py-2"
            disabled={saving}
          >
            {saving ? 'Enregistrement…' : 'Enregistrer'}
          </button>
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
            // keep individual save available (backwards compatible)
            await userRepository.updateMe({ profile: normalizeProfile(vals) });
            const me = await userRepository.getMe();
            setUser(me);
            setProfileDraft(me?.profile ?? {});
            alert('Informations personnelles mises à jour');
          }}
          onCancel={() => navigate('/profile')}
          onChange={(vals) => setProfileDraft(vals)}
          showButtons={false} // we want a single global Save button
        />
      </section>

      <section className="p-4 border rounded max-w-3xl">
        <h2 className="font-medium mb-2">Compte professionnel</h2>

        {professional === 'loading' ? (
          <div>Chargement…</div>
        ) : professional ? (
          <>
            <ProfessionalInfoForm
              initialValues={{
                name: professional.name ?? null,
                status_juridique: professional.status_juridique ?? null,
                domaine: professional.domaine ?? null,
                tjm_cents: professional.tjm_cents ?? undefined,
                number_pro: professional.number_pro ?? null,
              }}
              areas={areas}
              // onSave kept for backward compatibility (not needed with Save All)
              onSave={async (payload) => {
                // optional immediate save if someone uses the form submit button
                await userRepository.updateProfessionalMe(payload);
                const prof = await userRepository.getProfessionalMe();
                setProfessional(prof ?? null);
                setSelectedServiceIds(prof?.service_type_ids ?? []);
              }}
              onDomaineChange={handleDomaineChange}
              onValuesChange={(vals) => handleProValuesChange(vals)}
              onCancel={() => navigate('/profile')}
            />

            <div className="mt-6">
              <PrestationsSelector
                professionalId={professional.id}
                domaine={proDraft.domaine ?? professional.domaine ?? null}
                selected={selectedServiceIds}
                onChange={setSelectedServiceIds}
                onSave={async (ids) => {
                  await userRepository.updateProfessionalMe({
                    service_type_ids: ids,
                  });
                  const prof = await userRepository.getProfessionalMe();
                  setProfessional(prof ?? null);
                  setSelectedServiceIds(prof?.service_type_ids ?? []);
                  alert('Prestations mises à jour');
                }}
              />
            </div>
          </>
        ) : (
          <div>
            <p>Vous n'avez pas encore de profil professionnel.</p>
            <button
              onClick={() => navigate('/onboarding-professional')}
              className="underline text-blue-600 mt-2"
            >
              Commencer l'onboarding
            </button>
          </div>
        )}
      </section>
    </main>
  );
}
