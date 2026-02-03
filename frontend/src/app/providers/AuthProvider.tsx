/* eslint-disable react-refresh/only-export-components */
import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { makeAuthUseCases } from '../../domain/auth/usecases';
import { authRepository } from '../../infrastructure/auth/authRepository';
import type { AuthUser } from '../../domain/types';
import { tokenStorage } from '../../infrastructure/storage/tokenStorage';

type RegisterPayload = {
  email?: string;
  password?: string;
  profile?: {
    first_name?: string;
    last_name?: string;
    birthday?: string; // YYYY-MM-DD
    phone?: string;
    avatar_url?: string;
    role?: 'freelance' | 'client' | 'admin' | string;
    [k: string]: unknown;
  };
  full_name?: string;
  phone?: string;
  [k: string]: unknown;
};

type AuthContextValue = {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  /**
   * register accepte maintenant :
   * - soit (email: string, password: string)
   * - soit (payload: RegisterPayload) -> payload complet (email, password, profile, professional, ...)
   */
  register: (
    payloadOrEmail: string | RegisterPayload,
    maybePassword?: string,
  ) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const uc = makeAuthUseCases(authRepository);

export const AuthProvider: React.FC<React.PropsWithChildren> = ({
  children,
}) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

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
    return () => {
      active = false;
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      async login(email, password) {
        await uc.login({ email, password });
        try {
          const me = await uc.getMe();
          setUser(me);
        } catch {
          setUser({ id: -1, email } as AuthUser);
        }
      },

      /**
       * register peut recevoir :
       * - (email, password)  => ancien comportement
       * - (payloadObject)     => envoie payload complet au backend
       */
      async register(payloadOrEmail, maybePassword) {
        // Cas ancien : (email: string, password: string)
        if (typeof payloadOrEmail === 'string') {
          const email = payloadOrEmail;
          const password = maybePassword!;
          try {
            await uc.register({ email, password });
          } catch (err: unknown) {
            const axiosErr = err as {
              response?: { data?: { detail?: string; message?: string } };
            };
            const backendMsg =
              axiosErr.response?.data?.detail ||
              axiosErr.response?.data?.message;
            throw new Error(backendMsg || 'Échec inscription');
          }
          await uc.login({ email, password });
          try {
            const me = await uc.getMe();
            setUser(me);
          } catch {
            setUser({ id: -1, email } as AuthUser);
          }
          return;
        }

        // Cas nouveau : payload object (email, password, profile, professional, ...)
        const payload = payloadOrEmail as RegisterPayload;

        // Vérifier que email et password sont présents
        if (!payload.email || !payload.password) {
          throw new Error('Email et mot de passe requis');
        }

        // Appeler le use case register avec le payload complet
        try {
          await uc.register(
            payload as RegisterPayload & { email: string; password: string },
          );
        } catch (err: unknown) {
          const axiosErr = err as {
            response?: { data?: { detail?: string; message?: string } };
          };
          const backendMsg =
            axiosErr.response?.data?.detail || axiosErr.response?.data?.message;
          throw new Error(backendMsg || 'Échec inscription');
        }

        // Si on a email + password, on fait login auto pour récupérer le user
        const email = payload?.email;
        const password = payload?.password;
        if (email && password) {
          try {
            await uc.login({ email, password });
            const me = await uc.getMe();
            setUser(me);
          } catch {
            setUser({ id: -1, email } as AuthUser);
          }
        } else {
          // si pas de mot de passe (par ex. flow OAuth), on peut tenter getMe si token a été fourni par le backend
          try {
            const me = await uc.getMe().catch(() => null);
            if (me) setUser(me);
          } catch {
            // nothing to do
          }
        }
      },

      async logout() {
        await uc.logout();
        setUser(null);
      },
    }),
    [user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
  return ctx;
}
