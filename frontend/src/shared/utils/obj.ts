// src/shared/utils/obj.ts
/**
 * Helper utilitaire pour tenter de lire plusieurs clés potentielles et
 * retourner une string si trouvée (ou undefined).
 *
 * Usage: getStringField(prestation, 'name', 'title', 'label')
 */
export function getStringField(
  obj: Record<string, unknown>,
  ...keys: string[]
): string | undefined {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === 'string') {
      return v;
    }
    if (typeof v === 'number') {
      return String(v);
    }
  }
  return undefined;
}

export function getNumberField(
  obj: Record<string, unknown>,
  key: string,
): number | undefined {
  const v = obj[key];
  if (typeof v === 'number') return v;
  if (typeof v === 'string' && v.trim() !== '') {
    const n = Number(v);
    return Number.isFinite(n) ? n : undefined;
  }
  return undefined;
}
