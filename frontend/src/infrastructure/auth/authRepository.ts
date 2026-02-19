import type {
  AuthPort,
  AuthUser,
  LoginPayload,
  RegisterPayload,
  TokenPair,
} from '../../domain/types';
import { apiClient } from '../../infrastructure/http/apiClient';
import { tokenStorage } from '../../infrastructure/storage/tokenStorage';
import { API_ENDPOINTS } from '../../shared/endpoints';

/**
 * Implémentation concrète des appels Auth contre DRF.
 * On documente explicitement les payloads pour coller aux serializers fournis.
 */
export const authRepository: AuthPort = {
  async login(payload: LoginPayload): Promise<TokenPair> {
    // TokenObtainPairSerializer attend { email, password }
    const { data } = await apiClient.post(API_ENDPOINTS.login, payload);
    const tokens: TokenPair = { access: data.access, refresh: data.refresh };
    // on enregistre immédiatement
    tokenStorage.setAccess(tokens.access);
    if (tokens.refresh) tokenStorage.setRefresh(tokens.refresh);
    return tokens;
  },

  async register(payload: RegisterPayload): Promise<void> {
    // Tu exposes un serializer UserRegistrationSerializer côté back.
    // Version minimale : { email, password }
    await apiClient.post(API_ENDPOINTS.register, {
      email: payload.email,
      password: payload.password,
      // Optionnels pour compat:
      full_name: payload.full_name,
      phone: payload.phone,
      profile: payload.profile,
    });
  },

  async refresh(refreshToken: string): Promise<TokenPair> {
    const { data } = await apiClient.post(API_ENDPOINTS.refresh, {
      refresh: refreshToken,
    });
    const tokens: TokenPair = { access: data.access, refresh: data.refresh };
    tokenStorage.setAccess(tokens.access);
    if (tokens.refresh) tokenStorage.setRefresh(tokens.refresh);
    return tokens;
  },

  async logout(refreshToken: string): Promise<void> {
    // AuthLogoutView attend { refresh } et renvoie 204
    try {
      await apiClient.post(API_ENDPOINTS.logout, { refresh: refreshToken });
    } finally {
      tokenStorage.clearAll();
    }
  },

  async getMe(): Promise<AuthUser> {
    const { data } = await apiClient.get(API_ENDPOINTS.me);
    return data as AuthUser;
  },

  async requestPasswordReset(email: string): Promise<void> {
    await apiClient.post(API_ENDPOINTS.requestPasswordReset, { email });
  },
};
