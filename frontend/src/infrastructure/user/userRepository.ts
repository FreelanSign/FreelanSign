// src/infrastructure/user/userRepository.ts
import type { UserDto } from '../../domain/user/types';
import { apiClient } from '../../infrastructure/http/apiClient';
import { API_ENDPOINTS } from '../../shared/endpoints';

type ProfilePayload = Partial<UserDto['profile']>;
type UpdateMeArg = ProfilePayload | { profile: ProfilePayload };

/**
 * Type guard: determine si payload est du shape { profile: ... }.
 * Evite l'utilisation d'any et permet au compilateur de faire le narrowing proprement.
 */
function isWrappedProfile(v: UpdateMeArg): v is { profile: ProfilePayload } {
  // typeof v === 'object' && v !== null protège l'opérateur 'in'
  return typeof v === 'object' && v !== null && 'profile' in v;
}

function removeNulls<T extends Record<string, unknown>>(obj: T): T {
  const entires = Object.entries(obj).filter(([, v]) => v !== null);
  return Object.fromEntries(entires) as T;
}

/**
 * Repository pour user.
 * Attention : on évite l'usage de `any` dans les catches -> on utilise `unknown`
 * et axios.isAxiosError pour faire le narrowing.
 */
export const userRepository = {
  async getMe(): Promise<UserDto> {
    const { data } = await apiClient.get(API_ENDPOINTS.me);
    return data as UserDto;
  },

  /**
   * updateMe accepte soit:
   *  - un payload direct de profile (ex: { first_name: 'X' })
   *  - soit un wrapper { profile: { ... } }
   *
   * On normalise en { profile: ... } avant d'envoyer au backend.
   */
  async updateMe(payload: UpdateMeArg): Promise<UserDto> {
    const body = isWrappedProfile(payload) ? payload : { profile: payload };
    if ('profile' in body && body.profile) {
      body.profile = removeNulls(body.profile);
    }
    const { data } = await apiClient.patch(API_ENDPOINTS.me, body);
    return data as UserDto;
  },

  /**
   * Export all user data (RGPD Article 20 - Data Portability)
   * Returns JSON data including profile, accounts, clients, and quotes
   */
  async exportData(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(API_ENDPOINTS.exportData);
    return data;
  },

  // TODO: Add routes for reset password here instead of frontend/src/lib/api/auth.ts
};
