// src/infrastructure/user/userRepository.ts
import axios from 'axios';
import { apiClient } from '../../infrastructure/http/apiClient';
import { API_ENDPOINTS } from '../../shared/endpoints';
import type { ProfessionalUserDto, UserDto } from '../../domain/user/types';

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

/**
 * Repository pour user/professional.
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
    const { data } = await apiClient.patch(API_ENDPOINTS.me, body);
    return data as UserDto;
  },

  async getProfessionalMe(): Promise<ProfessionalUserDto | null> {
    try {
      const { data } = await apiClient.get(API_ENDPOINTS.professionalMe);
      return data as ProfessionalUserDto;
    } catch (err: unknown) {
      // Narrowing : si c'est une erreur axios on peut consulter response.status
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 404) return null;
      }
      // Sinon, on remonte l'erreur telle quelle
      throw err;
    }
  },

  async updateProfessionalMe(
    payload: Partial<ProfessionalUserDto>,
  ): Promise<ProfessionalUserDto> {
    const { data } = await apiClient.patch(
      API_ENDPOINTS.professionalMe,
      payload,
    );
    return data as ProfessionalUserDto;
  },
};
