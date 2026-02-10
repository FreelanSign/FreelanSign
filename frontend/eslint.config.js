import js from '@eslint/js';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import { globalIgnores } from 'eslint/config';
import globals from 'globals';
import tseslint from 'typescript-eslint';

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended, // ok de garder celui-là
      reactHooks.configs['recommended-latest'],
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        // 👇 IMPORTANT : demande à TS-ESLint d'utiliser ton tsconfig
        projectService: true,
        // racine où se trouve ton tsconfig.json (ici frontend/)
        tsconfigRootDir: new URL('.', import.meta.url).pathname,
      },
    },
  },
]);
