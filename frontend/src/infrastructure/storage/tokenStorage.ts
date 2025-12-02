// src/infrastructure/storage/tokenStorage.ts

const ACCESS_KEY = 'fs_access_token';
const REFRESH_KEY = 'fs_refresh_token';

// Mémoire process
let accessMemory: string | null = null;

const getLocalStorage = (): Storage | null => {
  if (typeof globalThis === 'undefined') return null;

  const ls = (globalThis as any).localStorage as Storage | undefined | null;
  return ls ?? null;
};

export const tokenStorage = {
  getAccess(): string | null {
    const storage = getLocalStorage();
    return accessMemory ?? storage?.getItem(ACCESS_KEY) ?? null;
  },

  setAccess(token: string | null) {
    accessMemory = token;

    const storage = getLocalStorage();
    if (!storage) return; // SSR / tests sans localStorage

    // Option dev: on pourrait choisir de ne pas persister l'accessToken
    if (token) {
      storage.setItem(ACCESS_KEY, token);
    } else {
      storage.removeItem(ACCESS_KEY);
    }
  },

  getRefresh(): string | null {
    const storage = getLocalStorage();
    return storage?.getItem(REFRESH_KEY) ?? null;
  },

  setRefresh(token: string | null) {
    const storage = getLocalStorage();
    if (!storage) return;

    if (token) storage.setItem(REFRESH_KEY, token);
    else storage.removeItem(REFRESH_KEY);
  },

  clearAll() {
    accessMemory = null;
    const storage = getLocalStorage();
    if (!storage) return;

    storage.removeItem(ACCESS_KEY);
    storage.removeItem(REFRESH_KEY);
  },
};
