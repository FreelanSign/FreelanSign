import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Écoute sur toutes les interfaces
    port: 3000,
    watch: {
      usePolling: true, // Nécessaire pour le hot reload dans Docker
    },
    hmr: {
      port: 3000, // Port pour Hot Module Replacement
    },
  },
  preview: {
    host: '0.0.0.0',
    port: 3000,
  },
})
