import type { User } from '../domain/user';
import { api } from '../infrastructure/api';

export async function fetchUsers(): Promise<User[]> {
  const response = await api.get('/');
  return response.data;
}

export async function createUser(payload: {
  full_name: string;
  email: string;
  phone?: string;
  password: string;
}): Promise<User> {
  const response = await api.post('/', payload);
  return response.data;
}
