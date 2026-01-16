import type {
  ApiQuoteItem,
  ApiQuoteResponse,
  ApiQuoteUpdatePayload,
  UiQuote,
  UiQuoteDetail,
  UiQuoteLine,
  UiQuoteLineDetail,
} from './types';

const num = (v: unknown, fallback = 0): number =>
  v == null ? fallback : Number(v);

export function apiItemsToUi(items: ApiQuoteItem[] | undefined): UiQuoteLine[] {
  const src = Array.isArray(items) ? items : [];
  return src.map(
    (it, idx): UiQuoteLine => ({
      id: it.id ?? idx,
      designation: it.description ?? '',
      description:
        typeof it.metadata === 'object' &&
        it.metadata &&
        'details' in it.metadata
          ? ((it.metadata as { details?: string | null }).details ?? '')
          : '',
      quantity: Number(it.qty ?? 0),
      unit_price: Number(it.unit_price ?? 0),
      tax_rate: it.tax_rate != null ? Number(it.tax_rate) / 100 : 0,
    }),
  );
}

export function apiToUiQuote(api: Partial<ApiQuoteResponse>): UiQuote {
  const items = Array.isArray(api.items)
    ? api.items
    : Array.isArray(api.line_items)
      ? api.line_items
      : [];

  return {
    id: api.id as string,
    reference: api.reference ?? '',
    title: api.title ?? '',
    status: api.status ?? 'DRAFT',
    issue_date: api.issue_date ?? null,
    due_date: api.valid_until ?? null,
    currency: api.currency ?? 'EUR',
    notes: api.note ?? '',
    terms: api.payment_terms_text ?? '',
    client: api.client
      ? {
          id: api.client.id,
          name: api.client.name ?? '',
          email: api.client.email ?? '',
          phone: api.client.phone ?? '',
          address_line1: api.client.address_line1 ?? '',
          address_line2: api.client.address_line2 ?? '',
          city: api.client.city ?? '',
          postal_code: api.client.postal_code ?? '',
          country: api.client.country ?? '',
          company: api.client.company ?? '',
          vat_number: api.client.vat_number ?? '',
          metadata: api.client.metadata ?? null,
        }
      : {
          id: undefined,
          name: '',
          email: '',
          phone: '',
          address_line1: '',
          address_line2: '',
          city: '',
          postal_code: '',
          country: '',
          company: '',
          vat_number: '',
          metadata: null,
        },
    line_items: apiItemsToUi(items),
  };
}

export function uiToUpdatePayload(q: UiQuote): ApiQuoteUpdatePayload {
  const payload: ApiQuoteUpdatePayload = {
    title: q.title,
    reference: q.reference,
    status: (q.status || '').toUpperCase(),
    issue_date: q.issue_date ?? null,
    valid_until: q.due_date ?? null,
    currency: q.currency ?? 'EUR',
    note: q.notes ?? '',
    payment_terms_text: q.terms ?? '',
    metadata: {},
    client: q.client?.id,
    client_update: {
      name: q.client?.name ?? '',
      email: q.client?.email ?? '',
      phone: q.client?.phone ?? null,
      // Structured address fields
      address_line1: q.client?.address_line1 ?? null,
      address_line2: q.client?.address_line2 ?? null,
      city: q.client?.city ?? null,
      postal_code: q.client?.postal_code ?? null,
      country: q.client?.country ?? null,
      company: q.client?.company ?? null,
      vat_number: q.client?.vat_number ?? null,
    },
  };

  if ((q.line_items?.length ?? 0) > 0) {
    payload.items = q.line_items.map((l, i) => ({
      description: l.designation,
      qty: String(l.quantity),
      unit_price: String(Number(l.unit_price).toFixed(2)),
      tax_rate: String(((l.tax_rate ?? 0) * 100).toFixed(2)),
      discount: '0.00',
      order: i,
      metadata: { details: l.description || null },
    }));
  }

  return payload;
}

export function apiToUiQuoteDetail(
  api: Partial<ApiQuoteResponse>,
): UiQuoteDetail {
  const items: ApiQuoteItem[] = Array.isArray(api.items)
    ? api.items!
    : Array.isArray(api.line_items)
      ? api.line_items!
      : [];

  const line_items: UiQuoteLineDetail[] = items.map((it, idx) => {
    const qty = num(it.qty);
    const up = num(it.unit_price);
    const taxPct = it.tax_rate != null ? num(it.tax_rate) : 0; // 0..100
    const pre = it.pre_tax_total != null ? num(it.pre_tax_total) : qty * up;
    const tax =
      it.tax_amount != null ? num(it.tax_amount) : pre * (taxPct / 100);
    return {
      id: (it.id ?? idx) as string | number,
      designation: it.description ?? '',
      description:
        typeof it.metadata === 'object' &&
        it.metadata &&
        'details' in it.metadata
          ? ((it.metadata as { details?: string | null }).details ?? '')
          : '',
      quantity: qty,
      unit_price: up,
      tax_rate: taxPct / 100,
      pre_tax_total: pre,
      tax_amount: tax,
      total: pre + tax,
    };
  });

  return {
    id: api.id as string,
    reference: api.reference ?? '',
    title: api.title ?? '',
    status: api.status ?? 'DRAFT',
    issue_date: api.issue_date ?? null,
    valid_until: api.valid_until ?? null,
    currency: api.currency ?? 'EUR',
    note: api.note ?? '',
    client: api.client
      ? {
          id: api.client.id,
          name: api.client.name ?? '',
          email: api.client.email ?? null,
          phone: api.client.phone ?? null,
          // Structured address fields
          address_line1: api.client.address_line1 ?? null,
          address_line2: api.client.address_line2 ?? null,
          city: api.client.city ?? null,
          postal_code: api.client.postal_code ?? null,
          country: api.client.country ?? null,
          company: api.client.company ?? null,
          vat_number: api.client.vat_number ?? null,
          metadata: api.client.metadata ?? null,
        }
      : null,
    line_items,
    subtotal: api.subtotal != null ? num(api.subtotal) : undefined,
    tax_total: api.tax_total != null ? num(api.tax_total) : undefined,
    discount_total:
      api.discount_total != null ? num(api.discount_total) : undefined,
    total: api.total != null ? num(api.total) : undefined,
    pdf_url: api.pdf_url ?? '',
  };
}
