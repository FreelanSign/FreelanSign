import type { ApiClient, UiClient } from '../client/types';

/**
 * Payload minimal pour créer un devis “vide” côté back.
 * On met les totaux à 0.00 pour respecter la contrainte ck_quote_totals_match.
 * Les lignes (QuoteLineItem) seront ajoutées plus tard sur une autre page.
 */
export type QuoteCreatePayload = {
  client: string; // Client UUID (FK)
  title: string;
  currency?: string; // 'EUR' par défaut
  language?: string; // 'fr' par défaut
  issue_date: string; // 'YYYY-MM-DD'
  valid_until?: string | null; // 'YYYY-MM-DD' optionnel
  payment_terms?: string | null; // UUID d’un PaymentTerms si tu l’utilises (optionnel)
  payment_terms_text?: string | null; // libre si pas de template

  // Totaux requis par la contrainte (commencent à 0 pour un devis vide)
  subtotal?: string; // "0.00"
  tax_total?: string; // "0.00"
  discount_total?: string; // "0.00"
  total?: string; // "0.00"
};

// === API ===
export type ApiQuoteItem = {
  id?: string | number;
  description?: string | null;
  qty?: string | number | null;
  unit_price?: string | number | null;
  tax_rate?: string | number | null; // 0–100 (%)
  discount?: string | number | null;
  order?: number;
  metadata?: { details?: string | null } | Record<string, unknown> | null;
  pre_tax_total?: string | number | null;
  tax_amount?: string | number | null;
};

export type ApiQuoteResponse = {
  id: string;
  reference?: string | null;
  title?: string | null;
  status?: string | null;
  issue_date?: string | null;
  valid_until?: string | null;
  currency?: string | null;
  note?: string | null;
  payment_terms_text?: string | null;
  client?: ApiClient | null;
  items?: ApiQuoteItem[]; // détail renvoie "items"
  line_items?: ApiQuoteItem[]; // (certains endpoints)
  // totaux + url pdf (présents sur le read serializer)
  subtotal?: string | number | null;
  tax_total?: string | number | null;
  discount_total?: string | number | null;
  total?: string | number | null;
  pdf_url?: string | null;
};

export type ApiQuoteUpdatePayload = {
  title: string;
  reference: string;
  status: string; // DRAFT/SENT/...
  issue_date: string | null;
  valid_until: string | null;
  currency: string | null;
  note: string | null;
  metadata: Record<string, unknown>;
  client: string | undefined; // UUID
  client_update: {
    name: string;
    email: string | null;
    // ajoute: phone/address/vat_number/metadata si supportés
  };
  items?: Array<{
    description: string;
    qty: string;
    unit_price: string;
    tax_rate: string; // "20.00"
    discount: string; // "0.00"
    order: number;
    metadata: Record<string, unknown>;
  }>;
};

// === UI ===
export type UiQuoteLine = {
  id?: string | number;
  designation: string;
  description?: string | null;
  quantity: number;
  unit_price: number;
  tax_rate?: number | null; // 0.2 => 20%
};

export type UiQuote = {
  id: string;
  reference: string;
  title: string;
  status: string;
  issue_date?: string | null;
  due_date?: string | null; // UI; mappé vers valid_until (API)
  currency?: string | null;
  notes?: string | null; // UI; mappé vers note (API)
  terms?: string | null; // UI only (payment_terms_text coté API)
  client?: UiClient | null;
  line_items: UiQuoteLine[];
};

// --- UI (détail) ---
export type UiQuoteLineDetail = {
  id: string | number;
  designation: string;
  description?: string | null;
  quantity: number;
  unit_price: number;
  tax_rate?: number | null; // fraction 0..1
  pre_tax_total?: number | null;
  tax_amount?: number | null;
  total?: number | null;
};

export type UiQuoteDetail = {
  id: string;
  reference: string;
  title: string;
  status: string;
  issue_date?: string | null;
  valid_until?: string | null;
  currency?: string | null;
  note?: string | null;
  client?: UiClient | null;
  line_items: UiQuoteLineDetail[];
  subtotal?: number | null;
  tax_total?: number | null;
  discount_total?: number | null;
  total?: number | null;
  pdf_url?: string | null;
};
