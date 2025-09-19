// src/domain/catalog/types.ts
/**
 * Types frontend pour le catalogue (Prestation & Area).
 * On reste permissif côté shape car la serialisation backend peut varier.
 *
 * On utilise `unknown` (plutôt que `any`) pour rester safe :
 * - on n'autorise plus l'accès direct sans vérification de type
 * - on force l'utilisation de guards ou helpers quand on veut lire un champ dynamique
 */

export type PrestationDto = {
  id: number;
  name?: string | null;
  title?: string | null;
  label?: string | null;
  description?: string | null;
  short_description?: string | null;
  price_cents?: number | null;
  // other dynamic keys are allowed but typed as unknown
} & Record<string, unknown>;

export type AreaDto = {
  id: number;
  name?: string | null;
  slug?: string | null;
} & Record<string, unknown>;
