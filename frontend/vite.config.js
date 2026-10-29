import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Dev proxy: forwards /api/* to Flask backend — no CORS issues in development.
    // The frontend api.js uses the direct URL 'http://127.0.0.1:5000/api' which
    // works fine both in dev (same machine) and in production builds.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
