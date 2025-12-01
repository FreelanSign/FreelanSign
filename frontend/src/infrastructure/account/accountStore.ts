// src/infrastructure/account/accountStore.ts
import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

export type Account = {
  id: string;
  display_name: string;
  legal_form?: string;
  legal_id?: string;
};

type AccountState = {
  activeAccountId: string | null;
  accounts: Account[];
  loading: boolean;
  error: string | null;

  setActiveAccountId: (id: string | null) => void;
  setAccounts: (accounts: Account[]) => void;
  selectFirstAccountIfNeeded: () => void;
  clear: () => void;
};

export const useAccountStore = create<AccountState>()(
  persist(
    (set, get) => ({
      activeAccountId: null,
      accounts: [],
      loading: false,
      error: null,

      setActiveAccountId: (id) => {
        set({ activeAccountId: id });
      },

      setAccounts: (accounts) => {
        set({ accounts });
      },

      selectFirstAccountIfNeeded: () => {
        const state = get();
        if (!state.activeAccountId && state.accounts.length > 0) {
          set({ activeAccountId: state.accounts[0].id });
        }
      },

      clear: () => {
        set({
          activeAccountId: null,
          accounts: [],
          loading: false,
          error: null,
        });
      },
    }),
    {
      name: 'account-store',
      storage: createJSONStorage(() => {
        // ✅ en browser OU en test (globalThis.localStorage mocké)
        if (
          typeof globalThis !== 'undefined' &&
          'localStorage' in globalThis &&
          globalThis.localStorage
        ) {
          return globalThis.localStorage;
        }
        // ✅ en SSR, on tombe ici → noop storage
        return undefined as any;
      }),
      partialize: (state) => ({ activeAccountId: state.activeAccountId }),
    },
  ),
);
