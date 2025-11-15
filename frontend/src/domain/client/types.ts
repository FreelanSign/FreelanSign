export type ClientDto = {
  id: string;
  name: string;
  email?: string | null;
  phone?: string | null;
};

export type ClientCreateDto = {
  name: string;
  email?: string;
  phone?: string;
  address?: string;
};

export type ClientValidationError = {
  name?: string;
  email?: string;
  phone?: string;
  address?: string;
};

// Types côté API (ce que renvoie/attend le backend)
export type ApiClient = {
  id?: string;
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  vat_number?: string | null;
  metadata?: Record<string, unknown> | null;
};

// ViewModel côté UI (si tu veux en partager la forme)
export type UiClient = {
  id?: string;
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  vat_number?: string | null;
  metadata?: Record<string, unknown> | null;
};
