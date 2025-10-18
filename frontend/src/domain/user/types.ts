/**
 * Types légers pour User / Profile / ProfessionalUser.
 * Ajuste selon ton serializer backend.
 */

export type ProfileDto = {
  first_name?: string | null;
  last_name?: string | null;
  birthday?: string | null;
  phone?: string | null;
  avatar_url?: string | null;
  role?: string | null;
};

export type UserDto = {
  id: number;
  email: string;
  profile?: ProfileDto | null;
};

export type ProfessionalUserDto = {
  id: number;
  user: number; // user id
  name?: string | null;
  email?: string | null;
  siret?: string | null;
  status_juridique?: string | null;
  domaine?: number | null; // id of area
  tjm_cents?: number | null;
  number_pro?: string | null;
  service_types?: number[]; // list of prestation ids
  // optional meta information to help the frontend render warnings (read-only)
  service_types_meta?: Array<{
    id: number;
    name?: string | null;
    area_id?: number | null;
    area_name?: string | null;
    off_domain?: boolean;
  }>;
  created_at?: string;
  updated_at?: string;
};
