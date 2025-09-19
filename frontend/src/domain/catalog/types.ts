// src/domain/catalog/types.ts
/**
 * Types frontend pour le catalogue (Prestation & Area).
 * On reste permissif côté shape car la serialisation backend peut varier.
 */
export type PrestationDto = {
  id: number;
  name?: string | null;
  title?: string | null;
  label?: string | null;
  description?: string | null;
  short_description?: string | null;
  price_cents?: number | null;
  // others: whatever your backend sends
  [key: string]: any;
};

export type AreaDto = {
  id: number;
  name?: string | null;
  slug?: string | null;
  [key: string]: any;
};
