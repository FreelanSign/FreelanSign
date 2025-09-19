import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { makeAuthUseCases } from '@/domain/auth/usecases';
import { authRepository } from '@/infrastructure/auth/authRepository';
import type { AuthUser } from '@/domain/auth/types';
import { tokenStorage } from '@/infrastructure/storage/tokenStorage';

/** Contexte d'auth simple.
 *  - expose user (optionnel)
 *  - expose actions login/register/logout
 *  - tente un getMe() si token présent au montage
 */

type AuthContextValue = {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const uc = makeAuthUseCases(authRepository);

export const AuthProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  // Au montage: si access token présent -> tenter de récupérer le profil
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        if (tokenStorage.getAccess()) {
          const me = await uc.getMe().catch(() => null);
          if (active) setUser(me);
        }
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    loading,
    async login(email, password) {
      await uc.login({ email, password });
      // Optionnel : charger user si endpoint /me existe
      try {
        const me = await uc.getMe();
        setUser(me);
      } catch {
        setUser({ id: -1, email }); // fallback minimal si pas d'endpoint /me
      }
    },
    async register(email, password) {
      await uc.register({ email, password });
      // on peut enchainer un login auto si souhaité
      await uc.login({ email, password });
      try {
        const me = await uc.getMe();
        setUser(me);
      } catch {
        setUser({ id: -1, email });
      }
    },
    async logout() {
      await uc.logout();
      setUser(null);
    },
  }), [user, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
  return ctx;
}
