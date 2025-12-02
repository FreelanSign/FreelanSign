/**
 * Types légers pour User / Profile.
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
