/**
 * Centralise les endpoints pour pouvoir les ajuster sans toucher au code métier.
 */
export const API_ENDPOINTS = {
  // Auth (DRF SimpleJWT custom views)
  login: '/api/auth/login/', // AuthLoginView (TokenObtainPair)
  refresh: '/api/auth/refresh/', // SecureAuthRefreshView (rotation + blacklist)
  logout: '/api/auth/logout/', // AuthLogoutView (POST { refresh })

  // Registration : 2 variantes possibles -> garde celle qui colle à ton backend
  // Variante A (souvent utilisée) : via UserViewSet.create()
  register: '/api/user/',

  // Variante B (si tu as une route dédiée d’inscription)
  // register: '/api/auth/register/',

  // "Me" : si tu exposes un endpoint pour récupérer l'utilisateur courant
  // Si absent, tu peux l'ignorer et te baser sur le token.
  me: '/api/user/me/',
  meProfile: '/api/user/me/profile/',
  professionalMe: '/api/user/professional/me/',
  catalogPrestation: '/api/catalog/prestations/',
  catalogArea: '/api/catalog/areas/',
  clients: '/api/clients/',
  quotes: '/api/quotes/',
  quotePreview: '/api/quotes/preview-pdf/',
  quotePdf: (id: string | number) => `/api/quotes/${id}/pdf/`,
} as const;
