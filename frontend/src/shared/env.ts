// env.ts
export const ENV = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL as string,
};

if (!ENV.apiBaseUrl) {
  console.warn('[ENV] VITE_API_BASE_URL is not set.');
  // Option hard: en dev, on lève une erreur pour éviter des 404 silencieux
  if (import.meta.env.DEV) {
    throw new Error(
      'VITE_API_BASE_URL is missing. Create .env.local with VITE_API_BASE_URL=http://localhost:8000',
    );
  }
}
