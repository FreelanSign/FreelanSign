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

export const authRepository: AuthPort = {
  async login(payload: LoginPayload): Promise<TokenPair> {
    const { data } = await apiClient.post(API_ENDPOINTS.login, payload);
    // Refresh token set as httpOnly cookie by backend — only access token in body
    const tokens: TokenPair = { access: data.access };
    tokenStorage.setAccess(tokens.access);
    return tokens;
  },

  async register(payload: RegisterPayload): Promise<void> {
    await apiClient.post(API_ENDPOINTS.register, {
      email: payload.email,
      password: payload.password,
      full_name: payload.full_name,
      phone: payload.phone,
      profile: payload.profile,
    });
  },

  async refresh(): Promise<TokenPair> {
    // No body — refresh token sent automatically via httpOnly cookie
    const { data } = await apiClient.post(API_ENDPOINTS.refresh, {});
    const tokens: TokenPair = { access: data.access };
    tokenStorage.setAccess(tokens.access);
    return tokens;
  },

  async logout(): Promise<void> {
    // No body — refresh token read from httpOnly cookie by backend
    try {
      await apiClient.post(API_ENDPOINTS.logout, {});
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
