export type AccountDto = {
  id: number;
  display_name: string;
  legal_form: string | null;
  legal_id: string | null;
  domain_id: number | null;
  default_rate_cents: number | null;
  service_type_ids: number[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type CreateAccountInput = {
  display_name: string;
  legal_form?: string | null;
  legal_id?: string | null;
  domain_id?: number | null;
  default_rate_cents?: number | null;
  service_type_ids?: number[];
};

export type UpdateAccountInput = Partial<CreateAccountInput>;
