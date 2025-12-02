// src/infrastructure/http/__tests__/apiClient.account-header.test.ts
import MockAdapter from 'axios-mock-adapter';
import { afterEach, beforeAll, beforeEach, describe, expect, it } from 'vitest';
import { useAccountStore } from '../infrastructure/account/accountStore';
import { apiClient } from '../infrastructure/http/apiClient';

describe('apiClient – X-Account-Id header', () => {
  let mock: MockAdapter;

  beforeAll(() => {
    // Faux localStorage pour le runtime de test (Node)
    let store: Record<string, string> = {};

    globalThis.localStorage = {
      getItem: (key: string) => store[key] ?? null,
      setItem: (key: string, value: string) => {
        store[key] = value;
      },
      removeItem: (key: string) => {
        delete store[key];
      },
      clear: () => {
        store = {};
      },
      key: (index: number) => Object.keys(store)[index] ?? null,
      get length() {
        return Object.keys(store).length;
      },
    } as Storage;
  });

  beforeEach(() => {
    mock = new MockAdapter(apiClient);

    // reset Zustand store
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

  afterEach(() => {
    mock.reset();
  });

  it('n’ajoute PAS X-Account-Id quand aucun account actif', async () => {
    // on s’assure qu’il n’y a pas d’account actif
    useAccountStore.getState().setActiveAccountId(null);

    mock.onGet('/test').reply((config) => {
      const headers = config.headers ?? {};
      expect(headers['X-Account-Id']).toBeUndefined();
      return [200, {}];
    });

    await apiClient.get('/test');
  });

  it('ajoute X-Account-Id quand un account actif est présent dans le store', async () => {
    useAccountStore.getState().setActiveAccountId(123);

    mock.onGet('/test').reply((config) => {
      const headers = config.headers ?? {};
      expect(headers['X-Account-Id']).toBe('123');
      return [200, {}];
    });

    await apiClient.get('/test');
  });

  it("n'écrase pas un header X-Account-Id déjà fourni", async () => {
    useAccountStore.getState().setActiveAccountId(123);

    mock.onGet('/test').reply((config) => {
      const headers = config.headers ?? {};
      expect(headers['X-Account-Id']).toBe('123');
      return [200, {}];
    });

    await apiClient.get('/test', {
      headers: {
        'X-Account-Id': 123,
      },
    });
  });
});
