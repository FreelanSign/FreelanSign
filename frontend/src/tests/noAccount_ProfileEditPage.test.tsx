import { render, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

// 1) Mock router
const mockNavigate = vi.fn();
let mockLocation = { pathname: '/profile' };

vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>(
      'react-router-dom',
    );
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => mockLocation,
  };
});

// 2) Mock account store
let mockAccountState = {
  accounts: [] as { id: number }[],
  activeAccountId: null as number | null,
};

vi.mock('../infrastructure/account/accountStore', () => ({
  useAccountStore: (selector: (s: typeof mockAccountState) => any) =>
    selector(mockAccountState),
}));

// ⬇️ 3) Mock useAuth avec LE BON CHEMIN depuis /src/tests
vi.mock('../app/providers/AuthProvider', () => ({
  useAuth: () => ({
    user: { email: 'test@example.com' },
  }),
}));

// 4) Ensuite seulement on importe ProfilePage
import ProfileEditPage from '../interface/pages/Profile/ProfileEditPage';

describe('ProfileEditPage – no-account handling', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
    mockAccountState = { accounts: [], activeAccountId: null };
    mockLocation = { pathname: '/profile' };
  });

  it('redirige vers onboarding quand aucun compte', async () => {
    mockAccountState = { accounts: [], activeAccountId: null };

    render(<ProfileEditPage />);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/onboarding-account', {
        replace: true,
      });
    });
  });

  it('ne redirige pas quand un compte existe', async () => {
    mockAccountState = {
      accounts: [{ id: 1 } as any],
      activeAccountId: 1,
    };

    render(<ProfileEditPage />);

    await waitFor(() => {
      const calls = mockNavigate.mock.calls.map(([path]) => path);
      expect(calls).not.toContain('/onboarding-account');
    });
  });
});
