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
      // Utilisation du vert de marque (Primary) pour le succès
      variant = 'default';
      label = s === 'ACCEPTED' ? 'Accepté' : 'Payé';
      customClasses =
        'bg-brand text-brand-foreground text-white hover:bg-green-600';
      break;
    case 'SENT':
      // Utilisation de l'orange d'accent
      variant = 'info';
      label = 'Envoyé';
      customClasses =
        'bg-accent-orange text-brand-foreground hover:bg-accent-orange/90';
      break;
    case 'REJECTED':
      // Utilisation du rouge de destruction
      variant = 'destructive';
      label = 'Refusé';
      customClasses =
        'bg-red-500 text-red-foreground text-white hover:bg-red-600';
      break;
    case 'EXPIRED':
      // Gris pour expiré, moins alarmant que 'rejected'
      variant = 'expired';
      label = 'Expiré';
      customClasses =
        'bg-gray-400 text-white hover:bg-gray-500 hover:text-gray-900';
      break;
    case 'DRAFT':
      // Secondaire/Gris clair pour brouillon
      variant = 'secondary';
      label = 'Brouillon';
      customClasses =
        'bg-gray-200 text-secondary-foreground hover:bg-secondary/80 border border-border';
      break;
    default:
      label = s;
      variant = 'secondary';
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
