// src/interface/pages/Profile/ProfileEditPage.tsx
import { useEffect, useMemo, useState } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

import type { AccountDto } from '../../../domain/account/types';
import type { AreaDto } from '../../../domain/catalog/types';
import type { UserDto } from '../../../domain/user/types';
import { accountRepository } from '../../../infrastructure/account/accountRepository';
import { useAccountStore } from '../../../infrastructure/account/accountStore';
import { catalogRepository } from '../../../infrastructure/catalog/catalogRepository';
import { userRepository } from '../../../infrastructure/user/userRepository';

import AccountDataForm, {
  type AccountFormValues,
} from '../../components/account/AccountDataForm';
import PersonalUserDataForm, {
  type PersonalUserFormValues,
} from '../../components/profile/PersonalUserDataForm';
import PrestationsSelector from '../../components/profile/PrestationSelector';

import { Briefcase, PencilLine, ShieldCheck } from 'lucide-react';
import { useRequireAccount } from '../../hooks/useRequireAccount';

/**
 * Component for RGPD data export (Article 20 - Data Portability)
 */
function DataExportSection() {
  const [isExporting, setIsExporting] = useState(false);

  const handleExportData = async () => {
    try {
      setIsExporting(true);
      const data = await userRepository.exportData();

      // Create JSON file and trigger download
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const timestamp = new Date().toISOString().split('T')[0];
      link.download = `freelansign-data-export-${timestamp}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast.success('Vos données ont été téléchargées avec succès');
    } catch (err) {
      console.error('Export data failed', err);
      toast.error(
        "Erreur lors de l'export des données: " +
          (err instanceof Error ? err.message : String(err)),
      );
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        Conformément au RGPD (Article 20), vous pouvez télécharger toutes vos
        données personnelles au format JSON.
      </p>
      <Button
        onClick={handleExportData}
        disabled={isExporting}
        variant="outline"
        className="w-full sm:w-auto"
      >
        {isExporting ? 'Téléchargement...' : 'Télécharger mes données'}
      </Button>
    </div>
  );
}

export default function ProfileEditPage() {
  const navigate = useNavigate();
  const activeAccountId = useAccountStore((state) => state.activeAccountId);
  const [user, setUser] = useState<UserDto | null>(null);
  const [account, setAccount] = useState<AccountDto | null | 'loading'>(
    'loading',
  );
  const [areas, setAreas] = useState<AreaDto[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);

  // Draft values kept locally until Save All
  type AccountDraftType = Partial<
    AccountFormValues & { default_rate_cents?: number; tjm_eur?: number }
  >;
  const [accountDraft, setAccountDraft] = useState<AccountDraftType>({});
  const [selectedServiceIds, setSelectedServiceIds] = useState<number[]>([]);

  // Profile draft tracked so Save All can persist profile + pro
  const [profileDraft, setProfileDraft] = useState<
    Partial<PersonalUserFormValues>
  >({});

  useRequireAccount({ loading });

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
            professional_headline: acc?.professional_headline ?? null,
            // Address fields
            address_line1: acc?.address_line1 ?? null,
            address_line2: acc?.address_line2 ?? null,
            city: acc?.city ?? null,
            postal_code: acc?.postal_code ?? null,
            country: acc?.country ?? null,
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
  const handleAccountValuesChange = useMemo(
    () => (values: AccountFormValues) => {
      setAccountDraft((prev) => ({
        ...prev,
        display_name: values.display_name ?? null,
        legal_form: values.legal_form ?? null,
        domain_id: values.domain_id ?? null,
        tjm_eur: values.tjm_eur ?? undefined,
        legal_id: values.legal_id ?? null,
        professional_headline: values.professional_headline ?? null,
        // Address fields
        address_line1: values.address_line1 ?? null,
        address_line2: values.address_line2 ?? null,
        city: values.city ?? null,
        postal_code: values.postal_code ?? null,
        country: values.country ?? null,
      }));
    },
    [],
  );

  const handleProfileDraftChange = useMemo(
    () => (vals: PersonalUserFormValues) => {
      setProfileDraft(vals);
    },
    [],
  );

  // called when domain_id changes (immediate) => update local draft and re-fetch prestations
  const handleDomainChange = useMemo(
    () => (domain_id: number | null) => {
      setAccountDraft((d) => ({ ...d, domain_id }));
    },
    [],
  );

  // Save payload type
  type SavePayload = {
    display_name?: string;
    legal_form?: string | null;
    domain_id?: number | null;
    legal_id?: string | null;
    professional_headline?: string | null;
    service_type_ids?: number[];
    default_rate_cents?: number | null;
    // Address fields
    address_line1?: string | null;
    address_line2?: string | null;
    city?: string | null;
    postal_code?: string | null;
    country?: string | null;
  };

  // helper: normalise profile fields (convert '' -> null)
  const normalizeProfile = (p: Partial<PersonalUserFormValues>) => ({
    first_name: p.first_name && p.first_name !== '' ? p.first_name : null,
    last_name: p.last_name && p.last_name !== '' ? p.last_name : null,
    phone: p.phone && p.phone !== '' ? p.phone : null,
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
        professional_headline: accountDraft.professional_headline ?? null,
        // Address fields
        address_line1: accountDraft.address_line1 ?? null,
        address_line2: accountDraft.address_line2 ?? null,
        city: accountDraft.city ?? null,
        postal_code: accountDraft.postal_code ?? null,
        country: accountDraft.country ?? null,
      }) !==
      JSON.stringify({
        display_name: currentAcc?.display_name ?? null,
        legal_form: currentAcc?.legal_form ?? null,
        domain_id: currentAcc?.domain_id ?? null,
        default_rate_cents: currentAcc?.default_rate_cents ?? null,
        legal_id: currentAcc?.legal_id ?? null,
        professional_headline: currentAcc?.professional_headline ?? null,
        // Address fields
        address_line1: currentAcc?.address_line1 ?? null,
        address_line2: currentAcc?.address_line2 ?? null,
        city: currentAcc?.city ?? null,
        postal_code: currentAcc?.postal_code ?? null,
        country: currentAcc?.country ?? null,
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

        // re-fetch me to update local user state
        const me = await userRepository.getMe();
        setUser(me);
        setProfileDraft(me?.profile ?? {});
      }

      // 2) build payload for account
      const payload: SavePayload = {
        display_name: accountDraft.display_name ?? '',
        legal_form: accountDraft.legal_form ?? null,
        domain_id: accountDraft.domain_id ?? null,
        legal_id: accountDraft.legal_id ?? null,
        professional_headline: accountDraft.professional_headline ?? null,
        service_type_ids: selectedServiceIds ?? [],
        default_rate_cents: null,
        // Address fields
        address_line1: accountDraft.address_line1 ?? null,
        address_line2: accountDraft.address_line2 ?? null,
        city: accountDraft.city ?? null,
        postal_code: accountDraft.postal_code ?? null,
        country: accountDraft.country ?? null,
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
        professional_headline: acc?.professional_headline ?? null,
        // Address fields
        address_line1: acc?.address_line1 ?? null,
        address_line2: acc?.address_line2 ?? null,
        city: acc?.city ?? null,
        postal_code: acc?.postal_code ?? null,
        country: acc?.country ?? null,
      });

      // show success toast
      toast.success('Profil mis à jour avec succès');

      // navigate to profile page after successful save
      setTimeout(() => {
        navigate('/profile', { replace: true });
      }, 500);
    } catch (err: unknown) {
      console.error('Save all failed', err);
      let errorMessage = 'Erreur lors de la sauvegarde';

      const errorObj = err as {
        response?: { data?: unknown };
        message?: string;
      };

      // AIDEV-NOTE: Parsing backend specific validation errors (e.g. "Identifiant légal invalide")
      // Currently backend returns simple string arrays or objects with field keys
      if (errorObj.response?.data) {
        const data = errorObj.response.data;
        if (Array.isArray(data)) {
          errorMessage = data.join(', ');
        } else if (typeof data === 'object') {
          // Handle cases like {"legal_id": ["Invalid..."]} or {"detail": "..."}
          const parts: string[] = [];
          Object.entries(data).forEach(([key, val]) => {
            if (key === 'detail' && typeof val === 'string') {
              parts.push(val);
            } else if (Array.isArray(val)) {
              parts.push(`${val.join(', ')}`);
            } else {
              parts.push(String(val));
            }
          });
          if (parts.length > 0) errorMessage = parts.join('\n');
        }
      } else if (errorObj.message) {
        errorMessage = errorObj.message;
      }

      toast.error(errorMessage);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="h-96 bg-muted/50 rounded-lg animate-pulse" />
      </div>
    );
  }

  const fullName = user
    ? `${user.profile?.first_name || ''} ${user.profile?.last_name || ''}`.trim() ||
      'Votre Profil'
    : 'Votre Profil';

  return (
    <div className="container mx-auto py-6 px-4 sm:px-6 lg:px-8 space-y-8 pb-32">
      {/* Breadcrumb / Title */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span
            className="cursor-pointer hover:text-brand transition-colors"
            onClick={() => navigate('/profile')}
          >
            Profil
          </span>
          <span>/</span>
          <span className="text-foreground font-medium">Édition</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight font-playfair">
          Paramètres du profil
        </h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Profile Summary / Header Card */}
        <div className="lg:col-span-12">
          <header className="flex flex-col sm:flex-row items-center gap-6 p-6 bg-white rounded-xl border border-border shadow-sm">
            <div className="relative">
              <div className="w-20 h-20 rounded-full overflow-hidden border-4 border-muted shadow-inner bg-muted/20">
                <img
                  src={
                    profileDraft.avatar_url ||
                    user?.profile?.avatar_url ||
                    '/img/default-avatar.jpeg'
                  }
                  alt="Avatar"
                  className="object-cover w-full h-full"
                />
              </div>
            </div>

            <div className="flex-1 text-center sm:text-left space-y-1">
              <h2 className="text-2xl font-bold font-playfair">{fullName}</h2>
              <p className="text-sm text-muted-foreground">
                {user?.email || '—'}
              </p>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={handleCancel}
                disabled={saving}
              >
                Annuler
              </Button>
              <Button
                onClick={handleSaveAll}
                className="bg-brand text-white hover:bg-brand-dark shadow-sm"
                disabled={saving || !isDirty}
              >
                {saving ? 'Enregistrement…' : 'Enregistrer'}
              </Button>
            </div>
          </header>
        </div>

        {/* Main Content Areas */}
        <div className="lg:col-span-8 space-y-8">
          {/* Informations personnelles */}
          <Card className="shadow-none border border-border overflow-hidden">
            <CardHeader className="bg-muted/30 border-b border-border/50 py-4">
              <CardTitle className="text-base flex items-center gap-2">
                <PencilLine className="h-4 w-4 text-brand" />
                Informations personnelles
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <PersonalUserDataForm
                initialValues={user?.profile ?? {}}
                onCancel={() => navigate('/profile')}
                onChange={handleProfileDraftChange}
                showButtons={false}
              />
            </CardContent>
          </Card>

          {/* Compte professionnel */}
          <Card className="shadow-none border border-border overflow-hidden">
            <CardHeader className="bg-muted/30 border-b border-border/50 py-4">
              <CardTitle className="text-base flex items-center gap-2">
                <Briefcase className="h-4 w-4 text-brand" />
                Structure professionnelle
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              {account === 'loading' ? (
                <div className="flex items-center justify-center py-8 animate-pulse text-muted-foreground italic">
                  Chargement des données professionnelles...
                </div>
              ) : account ? (
                <AccountDataForm
                  initialValues={{
                    display_name: account.display_name ?? null,
                    legal_form: account.legal_form ?? null,
                    domain_id: account.domain_id ?? null,
                    default_rate_cents: account.default_rate_cents ?? undefined,
                    legal_id: account.legal_id ?? null,
                    professional_headline:
                      account.professional_headline ?? null,
                    // Address fields
                    address_line1: account.address_line1 ?? null,
                    address_line2: account.address_line2 ?? null,
                    city: account.city ?? null,
                    postal_code: account.postal_code ?? null,
                    country: account.country ?? null,
                  }}
                  areas={areas}
                  accountId={account.id}
                  currentLogoUrl={account.logo_url}
                  onLogoChange={(url) => {
                    setAccount({ ...account, logo_url: url });
                  }}
                  onDomainChange={handleDomainChange}
                  onChange={(vals) => handleAccountValuesChange(vals)}
                  showButtons={false}
                />
              ) : (
                <div className="text-center py-6">
                  <p className="text-muted-foreground mb-4">
                    Vous n'avez pas encore de compte professionnel.
                  </p>
                  <Button
                    onClick={() => navigate('/onboarding-account')}
                    variant="outline"
                  >
                    Commencer l'onboarding
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar content */}
        <div className="lg:col-span-4 space-y-8">
          {/* Services proposés */}
          {account && account !== 'loading' && (
            <Card className="shadow-none border border-border overflow-hidden">
              <CardHeader className="bg-muted/30 border-b border-border/50 py-4">
                <CardTitle className="text-base">
                  Prestations proposées
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <PrestationsSelector
                  accountId={account.id}
                  domaine={accountDraft.domain_id ?? account.domain_id ?? null}
                  selected={selectedServiceIds}
                  onChange={setSelectedServiceIds}
                />
              </CardContent>
            </Card>
          )}

          {/* Données & Confidentialité */}
          <Card className="shadow-none border border-border">
            <CardHeader className="bg-muted/30 border-b border-border/50 py-4">
              <CardTitle className="text-base flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-orange-600" />
                Sécurité & Données
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <DataExportSection />
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Floating Action Bar */}
      {isDirty && (
        <footer className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 w-[min(calc(100%-2rem),40rem)] bg-white/95 backdrop-blur-md border border-border p-3 rounded-2xl shadow-2xl flex items-center justify-between gap-4 animate-in slide-in-from-bottom-4 duration-300">
          <div className="flex items-center gap-3 pl-2">
            <div className="w-2 h-2 rounded-full bg-brand animate-pulse" />
            <span
              className="text-sm font-medium
            "
            >
              Modifications non enregistrées
            </span>
          </div>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCancel}
              disabled={saving}
            >
              Annuler
            </Button>
            <Button
              size="sm"
              onClick={handleSaveAll}
              className="bg-brand text-white hover:bg-brand-dark px-6"
              disabled={saving}
            >
              {saving ? 'Enregistrement…' : 'Tout enregistrer'}
            </Button>
          </div>
        </footer>
      )}

      <Toaster position="top-right" />

      {/* Cancel Confirmation Modal */}
      <Dialog open={showCancelModal} onOpenChange={setShowCancelModal}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Abandonner les modifications ?</DialogTitle>
            <DialogDescription className="pt-2">
              Attention, vous avez des modifications en cours. Si vous quittez
              cette page maintenant, vos changements seront définitivement
              perdus.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-6 flex flex-col sm:flex-row gap-2">
            <Button
              variant="outline"
              onClick={() => setShowCancelModal(false)}
              className="flex-1"
            >
              Continuer l'édition
            </Button>
            <Button
              variant="destructive"
              className="flex-1"
              onClick={handleConfirmCancel}
            >
              Abandonner
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
