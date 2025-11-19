// src/infrastructure/user/userRepository.ts
import axios from 'axios';
import type { ProfessionalUserDto, UserDto } from '../../domain/user/types';
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

function isNumberArray(arr: unknown): arr is number[] {
  return Array.isArray(arr) && arr.every((v) => typeof v === 'number');
}

function toNullableNumber(x: unknown): number | null {
  if (typeof x === 'number') return x;
  if (typeof x === 'string') {
    const n = Number(x);
    return Number.isNaN(n) ? null : n;
  }
  return null;
}

/** Normalise un objet backend hétérogène en `ProfessionalUserDto` */
function normalizeProfessionalDto(data: unknown): ProfessionalUserDto {
  const raw = (
    typeof data === 'object' && data !== null
      ? (data as Record<string, unknown>)
      : {}
  ) as Record<string, unknown>;
  const domaine =
    toNullableNumber(raw.domaine) ?? toNullableNumber(raw.domaine_id);
  const serviceTypeIds = isNumberArray(raw.service_type_ids)
    ? raw.service_type_ids
    : isNumberArray(raw.service_types)
      ? raw.service_types
      : [];
  // on reconstruit l'objet en conservant les autres propriétés connues
  return {
    ...(raw as unknown as Omit<
      ProfessionalUserDto,
      'domaine' | 'service_type_ids'
    >),
    domaine,
    service_type_ids: serviceTypeIds,
  };
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
    if ('profile' in body && body.profile) {
      body.profile = removeNulls(body.profile);
    }
    const { data } = await apiClient.patch(API_ENDPOINTS.me, body);
    return data as UserDto;
  },

  async getProfessionalMe(): Promise<ProfessionalUserDto | null> {
    try {
      const { data } = await apiClient.get(API_ENDPOINTS.professionalMe);
      return normalizeProfessionalDto(data);
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 404) return null;
      throw err;
    }
  },

  async updateProfessionalMe(
    payload: Partial<ProfessionalUserDto>,
  ): Promise<ProfessionalUserDto> {
    console.log('[userRepository] updateProfessionalMe payload:', payload);

    const body: Record<string, unknown> = {};

    // Copier tous les champs SAUF ceux qui nécessitent une transformation
    for (const [key, value] of Object.entries(payload)) {
      if (key !== 'domaine' && key !== 'service_type_ids') {
        body[key] = value;
      }
    }

    // Transformation domaine -> domaine_id
    if ('domaine' in payload) {
      body.domaine_id = payload.domaine ?? null;
    }

    // Transformation service_type_ids (GARDER le champ, ne pas le supprimer)
    if ('service_type_ids' in payload) {
      body.service_type_ids = payload.service_type_ids ?? [];
    }

    console.log('[userRepository] updateProfessionalMe body to send:', body);
    const { data } = await apiClient.patch(API_ENDPOINTS.professionalMe, body);
    console.log('[userRepository] updateProfessionalMe response:', data);
    return normalizeProfessionalDto(data);
  },

  // TODO: Add routes for reset password here instead of frontend/src/lib/api/auth.ts
};
