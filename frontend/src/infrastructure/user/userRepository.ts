// src/infrastructure/user/userRepository.ts
import axios from 'axios';
import { apiClient } from '@/infrastructure/http/apiClient';
import { API_ENDPOINTS } from '@/shared/endpoints';
import type { ProfessionalUserDto, UserDto } from '@/domain/user/types';

/**
 * Repository pour user/professional.
 * Attention : on évite l'usage de `any` dans les catches -> on utilise `unknown`
 * et axios.isAxiosError pour faire le narrowing.
 */

export type ProfilePayload = Partial<{
  first_name: string;
  last_name: string;
  phone: string;
  birthday: string;
  avatar_url: string;
}>;

export const userRepository = {
  async getMe(): Promise<UserDto> {
    const { data } = await apiClient.get(API_ENDPOINTS.me);
    return data as UserDto;
  },

  async updateMe(profilePayload: ProfilePayload): Promise<UserDto> {
    const { data } = await apiClient.patch(
      API_ENDPOINTS.meProfile,
      profilePayload,
    );
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
