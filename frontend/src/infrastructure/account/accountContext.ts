// src/infrastructure/account/accountContext.ts
// On ne couple pas l'interceptor directement au localStorage
// pour éviter les problèmes de SSR / tests
import { useAccountStore } from "./accountStore";
export const ACTIVE_ACCOUNT_STORAGE_KEY = 'activeAccountId';

export function getActiveAccountId(): string | null {
    // Sécurité SSR / tests
    if (typeof window === "undefined") {
        return null;
    }

    try {
        const raw = useAccountStore.getState().activeAccountId;
        if (!raw) return null;

        const trimmed = raw.trim();
        return trimmed.length > 0 ? trimmed : null;
    } catch {
        // localStorage peut planter si on est dans un contexte non sécurisé
        return null;
    }
}
