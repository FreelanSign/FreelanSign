/**
 * Domain types for legal terms bounded context
 */

export type ClausePreviewDto = {
  identifier: string;
  title: string;
  body: string;
  order: number;
  is_mandatory: boolean;
  was_customized: boolean;
};

export type LegalTermsPreviewDto = {
  clauses: ClausePreviewDto[];
  rendered_html: string;
  rendered_text: string;
  template_version: string;
};

export type ClauseOverrideDto = {
  identifier: string;
  body: string | null;
  is_active: boolean;
};

export type LegalProfileDto = {
  id: string;
  account: string;
  template_version: string;
  clause_overrides: ClauseOverrideDto[];
  created_at: string;
  updated_at: string;
};
