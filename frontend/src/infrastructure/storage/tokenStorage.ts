/**
 * POC de persistance tokens.
 * - accessToken: principalement en mémoire (rapide & non persistant)
 * - refreshToken: localStorage (⚠️ compromis de sécurité pour dev)
 *
 * En prod idéalement: refresh en httpOnly cookie (géré côté back),
 * et access en mémoire uniquement.
 */

const ACCESS_KEY = 'fs_access_token';
const REFRESH_KEY = 'fs_refresh_token';

// Mémoire process
let accessMemory: string | null = null;

export const tokenStorage = {
  getAccess(): string | null {
    return accessMemory ?? window.localStorage.getItem(ACCESS_KEY);
  },
  setAccess(token: string | null) {
    accessMemory = token;
    if (token) {
      // Option dev: on peut éviter de l’écrire en localStorage.
      window.localStorage.setItem(ACCESS_KEY, token);
    } else {
      window.localStorage.removeItem(ACCESS_KEY);
    }
  },
  getRefresh(): string | null {
    return window.localStorage.getItem(REFRESH_KEY);
  },
  setRefresh(token: string | null) {
    if (token) window.localStorage.setItem(REFRESH_KEY, token);
    else window.localStorage.removeItem(REFRESH_KEY);
  },
  clearAll() {
    accessMemory = null;
    window.localStorage.removeItem(ACCESS_KEY);
    window.localStorage.removeItem(REFRESH_KEY);
  },
};
