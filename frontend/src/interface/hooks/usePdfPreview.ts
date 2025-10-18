// src/interface/hooks/usePdfPreview.ts
import { useCallback, useEffect, useRef, useState } from 'react';
import { apiClient } from '../../infrastructure/http/apiClient';
import { API_ENDPOINTS } from '../../shared/endpoints';
import {
  parseApiErrorBlob,
  humanizePreviewError,
} from '../../shared/apiErrors';

export type PreviewPayload = {
  seller: Record<string, unknown>;
  client: Record<string, unknown>;
  meta: Record<string, unknown>;
  lines: Array<{
    designation: string;
    description: string | null;
    quantity: number;
    unit_price: number;
    tax_rate: number | null;
    discount?: number;
  }>;
  branding: Record<string, unknown> | null;
};

export function usePdfPreview(payload: PreviewPayload | null, enabled = true) {
  const [url, setUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const lastUrl = useRef<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Ref qui garde la dernière valeur de payload
  const payloadRef = useRef<PreviewPayload | null>(null);
  useEffect(() => {
    payloadRef.current = payload;
  }, [payload]); // maj quand le contenu change

  // callback ne référence plus "payload" directement
  const doFetch = useCallback(async () => {
    if (!enabled) return;
    const current = payloadRef.current;
    if (!current) return;

    setLoading(true);
    setError(null);
    try {
      console.debug('[PDF Preview] POST', API_ENDPOINTS.quotePreview, current);
      const res = await apiClient.post(API_ENDPOINTS.quotePreview, current, {
        responseType: 'blob',
        headers: {
          Accept: 'application/pdf, application/json;q=0.9, */*;q=0.8',
        },
        validateStatus: () => true,
      });

      if (res.status >= 400) {
        const apiError = await parseApiErrorBlob(res.data as Blob);
        throw new Error(humanizePreviewError(apiError, res.status));
      }

      const blob = new Blob([res.data], { type: 'application/pdf' });
      const objectUrl = URL.createObjectURL(blob);
      if (lastUrl.current) URL.revokeObjectURL(lastUrl.current);
      lastUrl.current = objectUrl;
      setUrl(objectUrl);
    } catch (e: unknown) {
      setUrl(null);
      setError(e instanceof Error ? e.message : 'Erreur prévisualisation PDF');
    } finally {
      setLoading(false);
    }
  }, [enabled]); // OK: dépend de l'activation (payload via ref)

  useEffect(() => {
    return () => {
      if (lastUrl.current) URL.revokeObjectURL(lastUrl.current);
    };
  }, []);

  return { url, loading, error, refresh: doFetch };
}
