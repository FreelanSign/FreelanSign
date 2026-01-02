// src/infrastructure/branding/themeRepository.ts
import { tokenStorage } from '../storage/tokenStorage';

export type TypographySpec = {
  heading_font: string;
  body_font: string;
  font_sizes: {
    h1: number;
    h2: number;
    h3: number;
    body: number;
    small: number;
  };
  line_heights: { heading: number; body: number };
};

export type SpacingSpec = {
  page_margin: number;
  section_spacing: number;
  element_padding: number;
};

export type ThemeListItem = {
  id: string | number;
  name: string;
  is_active: boolean;
  colors: Record<string, string>;
  logo_url: string | null;
  updated_at: string;
};

export type Theme = {
  id: string | number;
  professional_id: string | number;
  name: string;
  is_active: boolean;
  colors: Record<string, string>;
  typography: TypographySpec;
  spacing: SpacingSpec;
  logo_url: string | null;
  created_at?: string;
  updated_at?: string;
};

// Payloads
export type CreateThemePayload = {
  professional_id?: string | number;
  name: string;
  is_active: boolean;
  colors: Record<string, string>;
  typography: TypographySpec;
  spacing: SpacingSpec;
  logo?: File;
};

// payload d’update typé finement (partiel et imbriqué)
export type UpdateTypographyPayload = {
  heading_font?: string;
  body_font?: string;
  font_sizes?: Partial<TypographySpec['font_sizes']>;
  line_heights?: Partial<TypographySpec['line_heights']>;
};

export type UpdateSpacingPayload = Partial<SpacingSpec>;

export type UpdateThemePayload = {
  name?: string;
  is_active?: boolean;
  colors?: Partial<Record<string, string>>;
  typography?: UpdateTypographyPayload;
  spacing?: UpdateSpacingPayload;
  logo?: File;
};

const API_BASE_URL = import.meta.env.VITE_API_URL;
const BASE_URL = `${API_BASE_URL}/api/branding/themes`;

async function http<T>(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<T> {
  const access = tokenStorage.getAccess();
  const res = await fetch(input, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(access ? { Authorization: `Bearer ${access}` } : {}),
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  const text = await res.text();

  if (!res.ok) {
    console.error('branding api error body: ', text);
    throw new Error(text || res.statusText);
  }

  if (text.trim().startsWith('<!doctype') || text.trim().startsWith('<html')) {
    throw new Error(
      'Serveur a renvoyé du HTML (probablement login ou browsable API)',
    );
  }

  return JSON.parse(text) as T;
}

export const themeRepository = {
  async listMine(): Promise<ThemeListItem[]> {
    return http<ThemeListItem[]>(BASE_URL);
  },

  async create(
    payload: Omit<CreateThemePayload, 'professional_id'>,
  ): Promise<Theme> {
    return http<Theme>(`${BASE_URL}/`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async get(id: string | number): Promise<Theme> {
    return http<Theme>(`${BASE_URL}/${id}/`);
  },

  async update(
    id: string | number,
    payload: UpdateThemePayload,
  ): Promise<Theme> {
    return http<Theme>(`${BASE_URL}/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  },

  async delete(id: string | number): Promise<void> {
    await http<void>(`${BASE_URL}/${id}/`, { method: 'DELETE' });
  },

  async activate(id: string | number): Promise<Theme> {
    return http<Theme>(`${BASE_URL}/${id}/activate/`, {
      method: 'POST',
      body: JSON.stringify({}),
    });
  },

  async deactivate(id: string | number): Promise<Theme> {
    return http<Theme>(`${BASE_URL}/${id}/deactivate/`, {
      method: 'POST',
    });
  },
};
