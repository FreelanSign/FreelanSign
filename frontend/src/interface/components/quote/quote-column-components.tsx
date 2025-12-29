import { Badge } from '@/components/ui/badge';

// AIDEV-NOTE: Définition des classes personnalisées pour les badges de statut
export type QuoteStatusVariant =
  | 'default'
  | 'secondary'
  | 'outline'
  | 'success' // Vert / Primaire (Accepté, Payé)
  | 'info' // Orange / Accent (Envoyé)
  | 'expired' // Gris foncé (Expiré)
  | 'destructive'; // Rouge (Refusé)

/** AIDEV-NOTE: Mapping statut -> variant FreelanSign. */
export function StatusPill({ status }: { status: string }) {
  const s = (status ?? '').toUpperCase();

  let variant: QuoteStatusVariant = 'secondary';
  let label = s;
  let customClasses = '';

  switch (s) {
    case 'ACCEPTED':
    case 'PAID':
      variant = 'default';
      label = s === 'ACCEPTED' ? 'Accepté' : 'Payé';
      customClasses =
        'bg-emerald-50 text-emerald-700 border-emerald-100 hover:bg-emerald-100 shadow-none';
      break;
    case 'SENT':
      variant = 'info';
      label = 'Envoyé';
      customClasses =
        'bg-orange-50 text-orange-700 border-orange-100 hover:bg-orange-100 shadow-none';
      break;
    case 'REJECTED':
      variant = 'destructive';
      label = 'Refusé';
      customClasses =
        'bg-red-50 text-red-700 border-red-100 hover:bg-red-100 shadow-none';
      break;
    case 'EXPIRED':
      variant = 'expired';
      label = 'Expiré';
      customClasses =
        'bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200 shadow-none';
      break;
    case 'DRAFT':
      variant = 'secondary';
      label = 'Brouillon';
      customClasses =
        'bg-gray-50 text-gray-500 border-gray-200 hover:bg-gray-100 shadow-none';
      break;
    default:
      label = s;
      variant = 'secondary';
      customClasses = 'shadow-none';
  }

  return (
    <Badge
      variant={variant}
      className={`font-medium min-w-[70px] justify-center ${customClasses}`}
    >
      {label}
    </Badge>
  );
}
