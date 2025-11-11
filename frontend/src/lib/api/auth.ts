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

  if (!res.ok) {
    const body = await res.json();
    throw new Error(body?.message || 'Erreur lors de la réinitialisation.');
  }
}
