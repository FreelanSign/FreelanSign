/// <reference types="vite/client" />

// Extend Vite's ImportMetaEnv with custom env variables
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
}
