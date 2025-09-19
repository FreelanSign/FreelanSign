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
  status_juridique?: string | null;
  domaine?: number | null; // id of area
  tjm_cents?: number | null;
  number_pro?: string | null;
  service_types?: number[]; // list of prestation ids
  created_at?: string;
  updated_at?: string;
};
