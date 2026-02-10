import { apiClient } from '../http/apiClient';
import { API_ENDPOINTS } from '../../shared/endpoints';
import type {
  AccountDto,
  CreateAccountInput,
  UpdateAccountInput,
} from '../../domain/account/types';

export const accountRepository = {
  async list(): Promise<AccountDto[]> {
    const { data } = await apiClient.get(API_ENDPOINTS.accounts);
    return data;
  },

  async retrieve(id: string | number): Promise<AccountDto> {
    const { data } = await apiClient.get(API_ENDPOINTS.account(String(id)));
    return data;
  },

  async create(payload: CreateAccountInput): Promise<AccountDto> {
    const { data } = await apiClient.post(API_ENDPOINTS.accounts, payload);
    return data;
  },

  async update(
    id: string | number,
    payload: UpdateAccountInput,
  ): Promise<AccountDto> {
    const { data } = await apiClient.patch(
      API_ENDPOINTS.account(String(id)),
      payload,
    );
    return data;
  },

  async delete(id: string | number): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.account(String(id)));
  },
};
