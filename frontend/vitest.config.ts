import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['src/tests/**/*.test.ts'],
    environment: 'jsdom',
    globals: true,           // pour pouvoir utiliser `describe`, `it`, `expect` sans import
    coverage: {
      reporter: ['text', 'lcov'],  // affichage console + rapport HTML
      exclude: ['node_modules/', 'src/interface/**'],  // modules et UI si tu veux
    },
  },
});
