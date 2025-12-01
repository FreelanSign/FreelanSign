// src/infrastructure/account/accountStore.ts
import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { accountRepository } from './accountRepository';
import type { AccountDto } from '../../domain/account/types';

export type Account = AccountDto;

type AccountState = {
  activeAccountId: number | null;
  accounts: Account[];
  loading: boolean;
  error: string | null;

  fetchAccounts: () => Promise<void>;
  setActiveAccountId: (id: number | null) => void;
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

      fetchAccounts: async () => {
        set({ loading: true, error: null });
        try {
          const accounts = await accountRepository.list();
          set({ accounts, loading: false });
          get().selectFirstAccountIfNeeded();
        } catch (error) {
          set({ error: 'Failed to fetch accounts', loading: false });
        }
      },

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
