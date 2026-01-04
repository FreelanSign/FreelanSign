// ISO 3166-1 alpha-2 country codes
// Must match backend whitelist in backend/apps/client/domain/policies/client_policies.py

export const COUNTRIES = [
  { code: 'FR', name: 'France' },
  { code: 'BE', name: 'Belgique' },
  { code: 'CH', name: 'Suisse' },
  { code: 'LU', name: 'Luxembourg' },
  { code: 'DE', name: 'Allemagne' },
  { code: 'ES', name: 'Espagne' },
  { code: 'IT', name: 'Italie' },
  { code: 'PT', name: 'Portugal' },
  { code: 'NL', name: 'Pays-Bas' },
  { code: 'GB', name: 'Royaume-Uni' },
  { code: 'US', name: 'États-Unis' },
  { code: 'CA', name: 'Canada' },
  { code: 'AT', name: 'Autriche' },
  { code: 'DK', name: 'Danemark' },
  { code: 'SE', name: 'Suède' },
  { code: 'NO', name: 'Norvège' },
  { code: 'FI', name: 'Finlande' },
  { code: 'IE', name: 'Irlande' },
  { code: 'PL', name: 'Pologne' },
  { code: 'CZ', name: 'République tchèque' },
] as const;

export type CountryCode = (typeof COUNTRIES)[number]['code'];
