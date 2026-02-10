// src/interface/pages/Account/AccountOnboardingPage.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast, { Toaster } from 'react-hot-toast';
import type { AreaDto } from '../../../domain/catalog/types';
import { catalogRepository } from '../../../infrastructure/catalog/catalogRepository';
import { accountRepository } from '../../../infrastructure/account/accountRepository';
import { useAccountStore } from '../../../infrastructure/account/accountStore';
import AccountDataForm from '../../components/account/AccountDataForm';

export default function AccountOnboardingPage() {
  const navigate = useNavigate();
  const { setActiveAccountId, fetchAccounts } = useAccountStore();
  const [areas, setAreas] = useState<AreaDto[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const areasList = await catalogRepository.listAreas();
        if (!mounted) return;
        setAreas(areasList);
      } catch (err) {
        console.error('Failed to load areas', err);
        if (mounted) setAreas(null);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  async function handleCreateAccount(payload: {
    display_name?: string | null;
    legal_form?: string | null;
    domain_id?: number | null;
    default_rate_cents?: number | null;
    legal_id?: string | null;
    professional_headline?: string | null;
    service_types?: number[] | null;
    address_line1?: string | null;
    address_line2?: string | null;
    city?: string | null;
    postal_code?: string | null;
    country?: string | null;
  }) {
    try {
      const newAccount = await accountRepository.create({
        display_name: payload.display_name ?? '',
        legal_form: payload.legal_form ?? null,
        domain_id: payload.domain_id ?? null,
        default_rate_cents: payload.default_rate_cents ?? null,
        legal_id: payload.legal_id ?? null,
        professional_headline: payload.professional_headline ?? null,
        service_type_ids: payload.service_types ?? undefined,
        address_line1: payload.address_line1 ?? null,
        address_line2: payload.address_line2 ?? null,
        city: payload.city ?? null,
        postal_code: payload.postal_code ?? null,
        country: payload.country ?? null,
      });

      // Set as active account
      setActiveAccountId(newAccount.id);

      // Refresh accounts list
      await fetchAccounts();

      toast.success('Compte créé avec succès');

      // Redirect to profile
      setTimeout(() => {
        navigate('/profile', { replace: true });
      }, 500);
    } catch (err) {
      console.error('Account creation failed', err);

      // Extract backend error message if available
      let errorMessage = 'Erreur inconnue';
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { error?: string } } };
        errorMessage = axiosErr.response?.data?.error || 'Erreur serveur';
      } else if (err instanceof Error) {
        errorMessage = err.message;
      } else {
        errorMessage = String(err);
      }

      toast.error('Erreur lors de la création du compte: ' + errorMessage);
      throw err;
    }
  }

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="text-gray-500">Chargement…</div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Créer votre compte professionnel
        </h1>
        <p className="text-gray-600">
          Renseignez les informations de votre activité professionnelle pour
          commencer à utiliser FreelanSign.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <AccountDataForm
          initialValues={{}}
          areas={areas}
          onSave={handleCreateAccount}
          onCancel={() => navigate('/dashboard')}
          submitLabel="Créer mon compte"
          showButtons={true}
        />
      </div>

      <Toaster position="top-right" />
    </div>
  );
}
