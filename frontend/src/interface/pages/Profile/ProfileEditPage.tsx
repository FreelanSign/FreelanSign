// src/interface/pages/ProfileEditPage.tsx
import { useEffect, useMemo, useState } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import type { AreaDto } from '../../../domain/catalog/types';
import type { AccountDto } from '../../../domain/account/types';
import type { UserDto } from '../../../domain/user/types';
import { catalogRepository } from '../../../infrastructure/catalog/catalogRepository';
import { userRepository } from '../../../infrastructure/user/userRepository';
import { accountRepository } from '../../../infrastructure/account/accountRepository';
import { useAccountStore } from '../../../infrastructure/account/accountStore';

import { Card } from '../../components/common/Card';
import { ConfirmModal } from '../../components/common/ConfirmModal';
import PersonalUserDataForm, {
  type PersonalUserFormValues,
} from '../../components/profile/PersonalUserDataForm';
import PrestationsSelector from '../../components/profile/PrestationSelector';
import AccountDataForm, {
  type AccountFormValues,
} from '../../components/account/AccountDataForm';

import styles from './profile-edit-page.module.css';

export default function ProfileEditPage() {
  const navigate = useNavigate();
  const activeAccountId = useAccountStore((state) => state.activeAccountId);
  const accounts = useAccountStore((state) => state.accounts);

  const [user, setUser] = useState<UserDto | null>(null);
  const [account, setAccount] = useState<AccountDto | null | 'loading'>(
    'loading',
  );
  const [areas, setAreas] = useState<AreaDto[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);

  // Draft values kept locally until Save All
  // include both default_rate_cents and tjm_eur to avoid any casts later
  type AccountDraftType = Partial<
    AccountFormValues & { default_rate_cents?: number; tjm_eur?: number }
  >;
  const [accountDraft, setAccountDraft] = useState<AccountDraftType>({});
  const [selectedServiceIds, setSelectedServiceIds] = useState<number[]>([]);

  // NEW: profile draft tracked so Save All can persist profile + pro
  const [profileDraft, setProfileDraft] = useState<
    Partial<PersonalUserFormValues>
  >({});

  // Redirect to onboarding if no active account
  useEffect(() => {
    if (!loading && accounts.length === 0) {
      navigate('/onboarding-account');
    }
  }, [accounts, loading, navigate]);

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

        if (activeAccountId) {
          const acc = await accountRepository.retrieve(activeAccountId);
          if (!mounted) return;
          setAccount(acc ?? null);
          setSelectedServiceIds(acc?.service_type_ids ?? []);
          // init draft from backend values
          setAccountDraft({
            display_name: acc?.display_name ?? null,
            legal_form: acc?.legal_form ?? null,
            domain_id: acc?.domain_id ?? null,
            default_rate_cents: acc?.default_rate_cents ?? undefined,
            legal_id: acc?.legal_id ?? null,
          });
        } else {
          setAccount(null);
        }

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
  }, [navigate, activeAccountId]);

  // called by AccountDataForm watch - update local draft and domain_id used to fetch prestations
  function handleAccountValuesChange(values: AccountFormValues) {
    setAccountDraft((prev) => ({
      ...prev,
      display_name: values.display_name ?? null,
      legal_form: values.legal_form ?? null,
      domain_id: values.domain_id ?? null,
      // use undefined (not null) to match the state's tjm_eur type
      tjm_eur: values.tjm_eur ?? undefined,
      legal_id: values.legal_id ?? null,
    }));
  }

  // called when domain_id changes (immediate) => update local draft and re-fetch prestations in PrestationsSelector (it uses domaine prop)
  function handleDomainChange(domain_id: number | null) {
    setAccountDraft((d) => ({ ...d, domain_id }));
    // NOTE: we DON'T persist to backend here (single save), but PrestationsSelector will get updated domaine prop
  }

  // Save payload type (avoid any)
  type SavePayload = {
    display_name?: string;
    legal_form?: string | null;
    domain_id?: number | null;
    legal_id?: string | null;
    service_type_ids?: number[];
    default_rate_cents?: number | null;
  };

  // helper: normalise profile fields (convert '' -> null)
  const normalizeProfile = (p: Partial<PersonalUserFormValues>) => ({
    first_name: p.first_name && p.first_name !== '' ? p.first_name : null,
    last_name: p.last_name && p.last_name !== '' ? p.last_name : null,
    phone: p.phone && p.phone !== '' ? p.phone : null,
    birthday: p.birthday && p.birthday !== '' ? p.birthday : null,
    avatar_url: p.avatar_url && p.avatar_url !== '' ? p.avatar_url : null,
  });

  // Check if there are unsaved changes
  const isDirty = useMemo(() => {
    const currentProfile = user?.profile ?? {};
    const profileChanged =
      JSON.stringify(profileDraft ?? {}) !== JSON.stringify(currentProfile);

    const currentAcc = account && account !== 'loading' ? account : null;
    const accountDraftChanged =
      JSON.stringify({
        display_name: accountDraft.display_name ?? null,
        legal_form: accountDraft.legal_form ?? null,
        domain_id: accountDraft.domain_id ?? null,
        default_rate_cents: accountDraft.default_rate_cents ?? null,
        legal_id: accountDraft.legal_id ?? null,
      }) !==
      JSON.stringify({
        display_name: currentAcc?.display_name ?? null,
        legal_form: currentAcc?.legal_form ?? null,
        domain_id: currentAcc?.domain_id ?? null,
        default_rate_cents: currentAcc?.default_rate_cents ?? null,
        legal_id: currentAcc?.legal_id ?? null,
      });

    const servicesChanged =
      JSON.stringify(selectedServiceIds) !==
      JSON.stringify(currentAcc?.service_type_ids ?? []);

    return profileChanged || accountDraftChanged || servicesChanged;
  }, [user, account, profileDraft, accountDraft, selectedServiceIds]);

  // Handle cancel with confirmation if dirty
  function handleCancel() {
    if (isDirty) {
      setShowCancelModal(true);
    } else {
      navigate('/profile');
    }
  }

  function handleConfirmCancel() {
    setShowCancelModal(false);
    navigate('/profile');
  }

  // central save all
  async function handleSaveAll() {
    try {
      setSaving(true);

      if (!activeAccountId) {
        toast.error('Aucun compte actif sélectionné');
        return;
      }

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

      // 2) build payload for account
      const payload: SavePayload = {
        display_name: accountDraft.display_name ?? '',
        legal_form: accountDraft.legal_form ?? null,
        domain_id: accountDraft.domain_id ?? null,
        legal_id: accountDraft.legal_id ?? null,
        service_type_ids: selectedServiceIds ?? [],
        default_rate_cents: null,
      };

      // convert tjm_eur (if provided) to default_rate_cents
      if (typeof accountDraft.tjm_eur === 'number') {
        payload.default_rate_cents = Math.round(accountDraft.tjm_eur * 100);
      } else if (typeof accountDraft.default_rate_cents === 'number') {
        payload.default_rate_cents = accountDraft.default_rate_cents;
      } else {
        payload.default_rate_cents = null;
      }

      // single PATCH with everything for account
      await accountRepository.update(activeAccountId, payload);

      // re-fetch account
      const acc = await accountRepository.retrieve(activeAccountId);
      setAccount(acc ?? null);
      setSelectedServiceIds(acc?.service_type_ids ?? []);
      // update draft with persisted values
      setAccountDraft({
        display_name: acc?.display_name ?? null,
        legal_form: acc?.legal_form ?? null,
        domain_id: acc?.domain_id ?? null,
        default_rate_cents: acc?.default_rate_cents ?? undefined,
        legal_id: acc?.legal_id ?? null,
      });

      // show success toast
      toast.success('Profil mis à jour avec succès');

      // navigate to profile page after successful save
      setTimeout(() => {
        navigate('/profile', { replace: true });
      }, 500);
    } catch (err) {
      console.error('Save all failed', err);
      toast.error(
        'Erreur lors de la sauvegarde: ' +
          (err instanceof Error ? err.message : String(err)),
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <div className={styles.loading}>Chargement…</div>;
  }

  return (
    <div className="grid gap-6">
      {/* Informations personnelles */}
      <Card title="Informations personnelles">
        <PersonalUserDataForm
          initialValues={user?.profile ?? {}}
          onSave={async (vals) => {
            // keep individual save available (backwards compatible)
            await userRepository.updateMe({
              profile: normalizeProfile(vals),
            });
            const me = await userRepository.getMe();
            setUser(me);
            setProfileDraft(me?.profile ?? {});
            toast.success('Informations personnelles mises à jour');
          }}
          onCancel={() => navigate('/profile')}
          onChange={(vals) => setProfileDraft(vals)}
          showButtons={false}
        />
      </Card>

      {/* Compte professionnel */}
      <Card title="Compte professionnel">
        {account === 'loading' ? (
          <div className="text-gray-500">Chargement…</div>
        ) : account ? (
          <AccountDataForm
            initialValues={{
              display_name: account.display_name ?? null,
              legal_form: account.legal_form ?? null,
              domain_id: account.domain_id ?? null,
              default_rate_cents: account.default_rate_cents ?? undefined,
              legal_id: account.legal_id ?? null,
            }}
            areas={areas}
            onSave={async (payload) => {
              if (!activeAccountId) return;
              await accountRepository.update(activeAccountId, {
                display_name: payload.display_name ?? '',
                legal_form: payload.legal_form ?? null,
                domain_id: payload.domain_id ?? null,
                legal_id: payload.legal_id ?? null,
                default_rate_cents: payload.default_rate_cents ?? null,
              });
              const acc = await accountRepository.retrieve(activeAccountId);
              setAccount(acc ?? null);
              setSelectedServiceIds(acc?.service_type_ids ?? []);
            }}
            onDomainChange={handleDomainChange}
            onChange={(vals) => handleAccountValuesChange(vals)}
            onCancel={() => navigate('/profile')}
            showButtons={false}
          />
        ) : (
          <div>
            <p className="text-gray-600">
              Vous n'avez pas encore de compte professionnel.
            </p>
            <button
              onClick={() => navigate('/onboarding-account')}
              className="underline text-blue-600 mt-2 hover:text-blue-800"
            >
              Commencer l'onboarding
            </button>
          </div>
        )}
      </Card>

      {/* Services proposés */}
      {account && account !== 'loading' && (
        <Card title="Services proposés">
          <PrestationsSelector
            accountId={account.id}
            domaine={accountDraft.domain_id ?? account.domain_id ?? null}
            selected={selectedServiceIds}
            onChange={setSelectedServiceIds}
          />
        </Card>
      )}

      {/* Buttons sticky at bottom */}
      <div className={styles.buttonContainer}>
        <button
          onClick={handleCancel}
          className={styles.buttonGhost}
          disabled={saving}
        >
          Annuler
        </button>
        <button
          onClick={handleSaveAll}
          className={styles.buttonPrimary}
          disabled={saving}
        >
          {saving ? 'Enregistrement…' : 'Enregistrer'}
        </button>
      </div>

      {/* Toast notifications */}
      <Toaster position="top-right" />

      {/* Cancel confirmation modal */}
      <ConfirmModal
        open={showCancelModal}
        title="Annuler les modifications ?"
        message="Les modifications non enregistrées seront perdues."
        confirmText="Abandonner les modifications"
        cancelText="Continuer l'édition"
        onConfirm={handleConfirmCancel}
        onCancel={() => setShowCancelModal(false)}
      />
    </div>
  );
}
