// src/tests/useRequireAccount.test.tsx
import { render } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useRequireAccount } from '../interface/hooks/useRequireAccount';

// mock navigate
const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>(
      'react-router-dom',
    );
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ pathname: '/test' }), // n'importe quel path
  };
});

// state mockable pour le store
let mockAccountState: {
  accounts: { id: number }[];
  activeAccountId: number | null;
};

// mock useAccountStore
vi.mock('../infrastructure/account/accountStore', () => ({
  useAccountStore: (selector: (s: typeof mockAccountState) => any) =>
    selector(mockAccountState),
}));

function TestComponent(props: {
  loading?: boolean;
  enabled?: boolean;
  redirectTo?: string;
}) {
  useRequireAccount(props);
  return null;
}

describe('useRequireAccount', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
    mockAccountState = {
      accounts: [],
      activeAccountId: null,
    };
  });

  it('redirige quand aucun compte et loading = false', () => {
    mockAccountState.accounts = [];
    mockAccountState.activeAccountId = null;

    render(<TestComponent loading={false} />);

    expect(mockNavigate).toHaveBeenCalledWith('/onboarding-account', {
      replace: true,
    });
  });

  it('ne redirige pas pendant le chargement', () => {
    mockAccountState.accounts = [];
    mockAccountState.activeAccountId = null;

    render(<TestComponent loading={true} />);

    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('ne redirige pas quand un compte existe dans la liste', () => {
    mockAccountState.accounts = [{ id: 1 }];
    mockAccountState.activeAccountId = null;

    render(<TestComponent loading={false} />);

    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('ne redirige pas quand activeAccountId est défini', () => {
    mockAccountState.accounts = [];
    mockAccountState.activeAccountId = 123;

    render(<TestComponent loading={false} />);

    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('ne fait rien quand enabled = false', () => {
    mockAccountState.accounts = [];
    mockAccountState.activeAccountId = null;

    render(<TestComponent loading={false} enabled={false} />);

    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('utilise redirectTo personnalisé', () => {
    mockAccountState.accounts = [];
    mockAccountState.activeAccountId = null;

    render(<TestComponent loading={false} redirectTo="/custom-onboarding" />);

    expect(mockNavigate).toHaveBeenCalledWith('/custom-onboarding', {
      replace: true,
    });
  });
});
