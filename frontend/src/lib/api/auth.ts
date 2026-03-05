// frontend/lib/api/auth.ts

export async function resetPassword(
  token: string,
  new_password: string,
): Promise<void> {
  const res = await fetch('/api/auth/reset-password/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, new_password }),
  });

  if (res.ok) return;

  let message = 'Erreur lors de la réinitialisation.';
  try {
    const body = await res.json();
    if (res.status === 404) {
      message = 'Lien invalide ou expiré. Demandez un nouveau lien.';
    } else {
      message = body?.detail || body?.message || message;
    }
  } catch {
    // body vide (ex: 405)
  }
  throw new Error(message);
}
