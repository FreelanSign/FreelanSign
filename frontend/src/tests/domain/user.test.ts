import { describe, it, expect } from 'vitest';
import type { User } from '../../domain/user';

describe('User type', () => {
  it('should have the correct shape', () => {
    const u: User = {
      id: 1,
      full_name: 'Alice',
      email: 'a@example.com',
      phone: null,
    };
    expect(u).toHaveProperty('email', 'a@example.com');
  });
});
