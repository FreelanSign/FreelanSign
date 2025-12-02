export const ENV = {
  apiBaseUrl: (import.meta as any).env.VITE_API_URL,
};

if (!ENV.apiBaseUrl) {
  console.warn('[ENV] VITE_API_URL is not set.');
  if ((import.meta as any).env.DEV) {
    throw new Error('VITE_API_URL is missing. Define it in your .env');
  }
}
