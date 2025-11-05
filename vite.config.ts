import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// GitHub Pages hosts the site at `/spacetraders-controlcenter/`, so ensure
// production builds resolve assets relative to that base path while keeping
// local development rooted at `/`.
export default defineConfig(({ mode }) => ({
  base: mode === 'production' ? '/spacetraders-controlcenter/' : '/',
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  }
}))
