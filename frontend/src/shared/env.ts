export const ENV = {
  apiBaseUrl: import.meta.env.VITE_API_URL,
};

if (!ENV.apiBaseUrl) {
  console.warn('[ENV] VITE_API_URL is not set.');
  if (import.meta.env.DEV) {
    throw new Error('VITE_API_URL is missing. Define it in your .env');
  }
}
