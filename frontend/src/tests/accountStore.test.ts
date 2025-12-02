import { beforeAll, beforeEach, describe, expect, it } from 'vitest';

// src/tests/accountStore.test.ts
let savedState: Record<string, string> = {};
// On déclare la variable, mais on n'importe pas encore le store
let useAccountStore: typeof import('../infrastructure/account/accountStore').useAccountStore;
type Account = import('../domain/account/types').AccountDto;

describe('accountStore', () => {
  beforeAll(async () => {
    savedState = {};

    // Mock globalThis.localStorage AVANT d'importer le store
    globalThis.localStorage = {
      getItem: (key: string) => savedState[key] ?? null,
      setItem: (key: string, value: string) => {
        savedState[key] = value;
      },
      removeItem: (key: string) => {
        delete savedState[key];
      },
      clear: () => {
        savedState = {};
      },
      key: (index: number) => Object.keys(savedState)[index] ?? null,
      get length() {
        return Object.keys(savedState).length;
      },
    } as Storage;

    // ⬅️ Import dynamique APRES avoir installé localStorage
    const mod = await import('../infrastructure/account/accountStore');
    useAccountStore = mod.useAccountStore;
  });

  beforeEach(() => {
    // reset store + storage
    savedState = {};
    const state = useAccountStore.getState();
    useAccountStore.setState({
      activeAccountId: null,
      accounts: [],
      loading: false,
      error: null,
      setActiveAccountId: state.setActiveAccountId,
      setAccounts: state.setAccounts,
      selectFirstAccountIfNeeded: state.selectFirstAccountIfNeeded,
      clear: state.clear,
    });
  });

  it('met à jour activeAccountId quand setActiveAccountId est appelé', () => {
    useAccountStore.getState().setActiveAccountId(123);

    const state = useAccountStore.getState();
    expect(state.activeAccountId).toBe(123);
  });

  it('persiste activeAccountId dans le storage', () => {
    useAccountStore.getState().setActiveAccountId(123);

    // Plus simple : on lit directement dans localStorage mock
    const raw = globalThis.localStorage.getItem('account-store');
    expect(raw).not.toBeNull();

    const parsed = JSON.parse(raw as string) as {
      state?: { activeAccountId?: string };
    };
    expect(parsed.state?.activeAccountId).toBe(123);
  });

  it('selectFirstAccountIfNeeded choisit le premier compte quand aucun actif', () => {
    const accounts: Account[] = [
      {
        id: 1,
        display_name: 'Compte 1',
        legal_form: null,
        legal_id: null,
        domain_id: null,
        default_rate_cents: null,
        service_type_ids: [],
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: 2,
        display_name: 'Compte 2',
        legal_form: null,
        legal_id: null,
        domain_id: null,
        default_rate_cents: null,
        service_type_ids: [],
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    const { setAccounts, selectFirstAccountIfNeeded } =
      useAccountStore.getState();

    setAccounts(accounts);
    selectFirstAccountIfNeeded();

    const state = useAccountStore.getState();
    expect(state.activeAccountId).toBe(1);
  });

  it('selectFirstAccountIfNeeded ne change rien si un compte est déjà actif', () => {
    const accounts: Account[] = [
      {
        id: 1,
        display_name: 'Compte 1',
        legal_form: null,
        legal_id: null,
        domain_id: null,
        default_rate_cents: null,
        service_type_ids: [],
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: 2,
        display_name: 'Compte 2',
        legal_form: null,
        legal_id: null,
        domain_id: null,
        default_rate_cents: null,
        service_type_ids: [],
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    const { setAccounts, setActiveAccountId, selectFirstAccountIfNeeded } =
      useAccountStore.getState();

    setAccounts(accounts);
    setActiveAccountId(2);
    selectFirstAccountIfNeeded();

    const state = useAccountStore.getState();
    expect(state.activeAccountId).toBe(2);
  });
});
