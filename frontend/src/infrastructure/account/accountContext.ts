// src/infrastructure/account/accountContext.ts
// On ne couple pas l'interceptor directement au localStorage
// pour éviter les problèmes de SSR / tests
import { useAccountStore } from './accountStore';

export const ACTIVE_ACCOUNT_STORAGE_KEY = 'activeAccountId';

export function getActiveAccountId(): string | null {
  try {
    const raw = useAccountStore.getState().activeAccountId;
    if (raw == null) return null;

    const trimmed = raw.toString().trim();
    return trimmed.length > 0 ? trimmed : null;
  } catch {
    return null;
  }
}
