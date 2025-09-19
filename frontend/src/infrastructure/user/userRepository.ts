import { apiClient } from '../../infrastructure/http/apiClient';
import { API_ENDPOINTS } from '../../shared/endpoints';
import type { ProfessionalUserDto, UserDto } from '../../domain/user/types'
/**
 * Repository dédié à la récupération du profil et du professional user.
 * Sépare la logique HTTP du composant (testable, remplaçable).
 */

export const userRepository = {
  async getMe(): Promise<UserDto> {
    const { data } = await apiClient.get(API_ENDPOINTS.me);
    return data as UserDto;
  },

  async getProfessionalMe(): Promise<ProfessionalUserDto | null> {
    try {
      const { data } = await apiClient.get(API_ENDPOINTS.professionalMe);
      return data as ProfessionalUserDto;
    } catch (err: any) {
      // Si 404 -> pas de professional attached
      if (err?.response?.status === 404) return null;
      throw err;
    }
  },
};
