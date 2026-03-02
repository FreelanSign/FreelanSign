import type {
  AuthPort,
  LoginPayload,
  RegisterPayload,
  AuthUser,
  TokenPair,
} from '../types';
import { tokenStorage } from '../../infrastructure/storage/tokenStorage';

export function makeAuthUseCases(port: AuthPort) {
  return {
    async login(data: LoginPayload) {
      return port.login(data);
    },
    async register(data: RegisterPayload) {
      await port.register(data);
    },
    async refresh(): Promise<TokenPair | null> {
      try {
        return await port.refresh();
      } catch {
        return null;
      }
    },
    async logout() {
      try {
        await port.logout();
      } catch {
        // Network error — clear local state anyway
      } finally {
        tokenStorage.clearAll();
      }
    },
    async getMe(): Promise<AuthUser> {
      return port.getMe();
    },
    isAuthenticated(): boolean {
      return !!tokenStorage.getAccess();
    },
  };
}
