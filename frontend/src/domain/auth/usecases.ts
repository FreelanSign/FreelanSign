import type {
  AuthPort,
  LoginPayload,
  RegisterPayload,
  AuthUser,
} from '../types';
import { tokenStorage } from '../../infrastructure/storage/tokenStorage';

/** Les use-cases orchestrent l’implémentation du port et la persistance locale. */

export function makeAuthUseCases(port: AuthPort) {
  return {
    async login(data: LoginPayload) {
      return port.login(data);
    },
    async register(data: RegisterPayload) {
      await port.register(data);
    },
    async logout() {
      const refresh = tokenStorage.getRefresh();
      if (refresh) {
        await port.logout(refresh); // clearAll handled in finally inside repository
      } else {
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
