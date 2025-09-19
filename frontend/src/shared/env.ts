export const ENV = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL as string,
};

if (!ENV.apiBaseUrl) {
  // Fail fast en dev : évite les "undefined/undefined"
  // ton collègue saura immédiatement quoi faire.
  // eslint-disable-next-line no-console
  console.warn('[ENV] VITE_API_BASE_URL is not set.');
}
