/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  // plus de variables d'environnement...
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
