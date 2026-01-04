export type ClientDto = {
  id: string;
  name: string;
  email?: string | null;
  phone?: string | null;
  // Structured address fields
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  postal_code?: string | null;
  country?: string | null;
  company?: string | null;
  vat_number?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type ClientCreateDto = {
  name: string;
  email?: string;
  phone?: string;
  // Structured address fields
  address_line1?: string;
  address_line2?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  company?: string;
};

export type ClientValidationError = {
  name?: string;
  email?: string;
  phone?: string;
};

// Types côté API (ce que renvoie/attend le backend)
export type ApiClient = {
  id?: string;
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  // Structured address fields
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  postal_code?: string | null;
  country?: string | null;
  company?: string | null;
  vat_number?: string | null;
  metadata?: Record<string, unknown> | null;
};

// ViewModel côté UI (si tu veux en partager la forme)
export type UiClient = {
  id?: string;
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  // Structured address fields
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  postal_code?: string | null;
  country?: string | null;
  company?: string | null;
  vat_number?: string | null;
  metadata?: Record<string, unknown> | null;
};
