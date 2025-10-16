// src/shared/apiErrors.ts
export type ApiError = { code?: string; detail?: string };
export function parseApiErrorBlob(blob: Blob): Promise<ApiError> {
  return blob.text().then((text) => {
    try {
      const json = JSON.parse(text);
      return json as ApiError;
    } catch {
      return { detail: text.slice(0, 300) || 'Erreur inconnue' };
    }
  });
}

export function humanizePreviewError(e: ApiError, status: number): string {
  const { code, detail } = e;
  if (code === 'QUOTE_PREVIEW_VALIDATION')
    return `Données incomplètes : ${detail ?? ''}`;
  if (code === 'QUOTE_PREVIEW_TEMPLATE')
    return `Template PDF indisponible. ${detail ?? ''}`;
  if (code === 'QUOTE_PREVIEW_ENGINE')
    return `Moteur PDF indisponible. ${detail ?? ''}`;
  if (status === 401) return 'Session expirée (401).';
  if (status === 403) return 'Accès interdit (403).';
  return detail ?? `Erreur serveur (HTTP ${status})`;
}
