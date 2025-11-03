// src/interface/utils/branding.ts

/** Types forts pour le thème */
export type Typography = {
  heading_font: string;
  body_font: string;
  font_sizes: {
    h1: number;
    h2: number;
    h3: number;
    body: number;
    small: number;
  };
  line_heights: {
    heading: number;
    body: number;
  };
};

export type Spacing = {
  page_margin: number;
  section_spacing: number;
  element_padding: number;
};

/** Entrées "brutes" permissives (pour venir d'une API, d'un JSON, etc.) */
type TypographyInput =
  | Partial<{
      heading_font: unknown;
      body_font: unknown;
      font_sizes: Partial<
        Record<'h1' | 'h2' | 'h3' | 'body' | 'small', unknown>
      >;
      line_heights: Partial<Record<'heading' | 'body', unknown>>;
    }>
  | null
  | undefined;

type SpacingInput =
  | Partial<
      Record<'page_margin' | 'section_spacing' | 'element_padding', unknown>
    >
  | null
  | undefined;

/** Defaults */
const DEFAULT_TYPO: Readonly<Typography> = {
  heading_font: 'Inter',
  body_font: 'Inter',
  font_sizes: { h1: 20, h2: 16, h3: 13, body: 12, small: 10 },
  line_heights: { heading: 1.2, body: 1.5 },
} as const;

const DEFAULT_SPACING: Readonly<Spacing> = {
  page_margin: 40,
  section_spacing: 12,
  element_padding: 8,
} as const;

/** Helpers de coercition sûrs */
const toString = (v: unknown, fallback: string): string =>
  typeof v === 'string' ? v : fallback;

const toNumber = (v: unknown, fallback: number): number => {
  if (typeof v === 'number') return v;
  if (typeof v === 'string') {
    const n = Number(v);
    return Number.isFinite(n) ? n : fallback;
  }
  return fallback;
};

/** Normalisations (plus de `any`) */
export function normalizeTypography(raw: TypographyInput): Typography {
  return {
    heading_font: toString(raw?.heading_font, DEFAULT_TYPO.heading_font),
    body_font: toString(raw?.body_font, DEFAULT_TYPO.body_font),
    font_sizes: {
      h1: toNumber(raw?.font_sizes?.h1, DEFAULT_TYPO.font_sizes.h1),
      h2: toNumber(raw?.font_sizes?.h2, DEFAULT_TYPO.font_sizes.h2),
      h3: toNumber(raw?.font_sizes?.h3, DEFAULT_TYPO.font_sizes.h3),
      body: toNumber(raw?.font_sizes?.body, DEFAULT_TYPO.font_sizes.body),
      small: toNumber(raw?.font_sizes?.small, DEFAULT_TYPO.font_sizes.small),
    },
    line_heights: {
      heading: toNumber(
        raw?.line_heights?.heading,
        DEFAULT_TYPO.line_heights.heading,
      ),
      body: toNumber(raw?.line_heights?.body, DEFAULT_TYPO.line_heights.body),
    },
  };
}

export function normalizeSpacing(raw: SpacingInput): Spacing {
  return {
    page_margin: toNumber(raw?.page_margin, DEFAULT_SPACING.page_margin),
    section_spacing: toNumber(
      raw?.section_spacing,
      DEFAULT_SPACING.section_spacing,
    ),
    element_padding: toNumber(
      raw?.element_padding,
      DEFAULT_SPACING.element_padding,
    ),
  };
}
