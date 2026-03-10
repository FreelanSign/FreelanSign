// src/infrastructure/storage/tokenStorage.ts
// Access token: memory only (not persisted — refresh via httpOnly cookie on page reload)
// Refresh token: httpOnly cookie managed by backend (not accessible in JS)

let accessMemory: string | null = null;

export const tokenStorage = {
  getAccess(): string | null {
    return accessMemory;
  },

  setAccess(token: string | null) {
    accessMemory = token;
  },

  clearAll() {
    accessMemory = null;
  },
};
