export type AccountDto = {
  id: number;
  display_name: string;
  legal_form: string | null;
  legal_id: string | null;
  domain_id: number | null;
  default_rate_cents: number | null;
  professional_headline: string | null;
  service_type_ids: number[];
  is_active: boolean;
  logo_url: string | null;
  // Address fields (feat/account-address)
  address_line1: string | null;
  address_line2: string | null;
  city: string | null;
  postal_code: string | null;
  country: string | null;
  // Subscription plan fields
  plan: 'beta' | 'free' | 'pro';
  max_quotes_monthly: number | null;
  max_clients: number | null;
  created_at: string;
  updated_at: string;
};

export type CreateAccountInput = {
  display_name: string;
  legal_form?: string | null;
  legal_id?: string | null;
  domain_id?: number | null;
  default_rate_cents?: number | null;
  professional_headline?: string | null;
  service_type_ids?: number[];
  // Address fields (feat/account-address)
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  postal_code?: string | null;
  country?: string | null;
};

export type UpdateAccountInput = Partial<CreateAccountInput>;
