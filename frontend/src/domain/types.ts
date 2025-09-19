/** Paire de tokens SimpleJWT. `refresh` peut ne pas être renvoyé
 *  si la rotation est désactivée. On le marque donc optionnel au runtime. */
export type TokenPair = {
  access: string;
  refresh?: string | null;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = {
  email: string;
  password: string;
  // Optionnel : si tu veux transporter plus (profile, phone, ...)
  profile?: {
    first_name?: string;
    last_name?: string;
    phone?: string;
    birthday?: string; // YYYY-MM-DD
    avatar_url?: string;
  };
  full_name?: string;
  phone?: string;
};

export type AuthUser = {
  id: number;
  email: string;
  // Optionnel selon ton serializer
  profile?: {
    first_name?: string | null;
    last_name?: string | null;
    avatar_url?: string | null;
    phone?: string | null;
    role?: string;
  };
};

export interface AuthPort {
  login(payload: LoginPayload): Promise<TokenPair>;
  register(payload: RegisterPayload): Promise<void>;
  refresh(refreshToken: string): Promise<TokenPair>;
  logout(refreshToken: string): Promise<void>;
  getMe(): Promise<AuthUser>;
}
