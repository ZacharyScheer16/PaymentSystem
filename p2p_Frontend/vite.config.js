import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Mirrors the nginx /api proxy used in the Docker image, so `npm run dev`
  // and the built container both resolve the same relative "/api" base.
  // Without this, the dev server would 404 on API calls.
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
