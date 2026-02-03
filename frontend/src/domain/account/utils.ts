/**
 * Détecte si une erreur indique que l'utilisateur n'a pas de compte professionnel actif.
 * Utilisé pour afficher un CTA d'onboarding au lieu d'un message d'erreur générique.
 */
export function isAccountMissingError(err: unknown): boolean {
  if (!err) return false;

  // Cas 1: String contenant le message d'erreur 403
  if (typeof err === 'string') {
    return (
      err.includes('"detail":"You do not have permission') ||
      err.includes('You do not have permission to perform this action')
    );
  }

  if (typeof err !== 'object') return false;

  // Cas 2: Erreur Axios avec response.status
  if ('response' in err) {
    const axiosErr = err as { response?: { status?: number; data?: unknown } };
    if (axiosErr.response?.status === 403) {
      return true;
    }
  }

  // Cas 3: Error object avec message contenant le JSON de la 403
  if (err instanceof Error) {
    const msg = err.message;
    if (
      msg.includes('"detail":"You do not have permission') ||
      msg.includes('You do not have permission to perform this action')
    ) {
      return true;
    }
  }

  return false;
}
