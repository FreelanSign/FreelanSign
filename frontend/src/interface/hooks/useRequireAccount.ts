// src/interface/hooks/useRequireAccount.ts
import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAccountStore } from '../../infrastructure/account/accountStore';

type UseRequireAccountOptions = {
  redirectTo?: string;
  loading?: boolean; // loading local de la page
  enabled?: boolean; // si false, le hook ne fait rien
};

export function useRequireAccount(options: UseRequireAccountOptions = {}) {
  const {
    redirectTo = '/onboarding-account',
    loading = false,
    enabled = true,
  } = options;

  const navigate = useNavigate();
  const location = useLocation();

  const accounts = useAccountStore((state) => state.accounts);
  const activeAccountId = useAccountStore((state) => state.activeAccountId);

  const hasAccount = accounts.length > 0 || activeAccountId !== null;

  useEffect(() => {
    if (!enabled) return;
    if (loading) return;

    if (!hasAccount && location.pathname !== redirectTo) {
      navigate(redirectTo, { replace: true });
    }
  }, [enabled, loading, hasAccount, redirectTo, navigate, location.pathname]);
}
