/**
 * Payload minimal pour créer un devis “vide” côté back.
 * On met les totaux à 0.00 pour respecter la contrainte ck_quote_totals_match.
 * Les lignes (QuoteLineItem) seront ajoutées plus tard sur une autre page.
 */
export type QuoteCreatePayload = {
  client: string;               // Client UUID (FK)
  title: string;
  reference: string;            // unique par owner
  currency?: string;            // 'EUR' par défaut
  language?: string;            // 'fr' par défaut
  issue_date: string;           // 'YYYY-MM-DD'
  valid_until?: string | null;  // 'YYYY-MM-DD' optionnel
  payment_terms?: string | null;      // UUID d’un PaymentTerms si tu l’utilises (optionnel)
  payment_terms_text?: string | null; // libre si pas de template

  // Totaux requis par la contrainte (commencent à 0 pour un devis vide)
  subtotal?: string;        // "0.00"
  tax_total?: string;       // "0.00"
  discount_total?: string;  // "0.00"
  total?: string;           // "0.00"
};
