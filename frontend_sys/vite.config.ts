import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  server: {
    port: 5174, // Use a different port from the old frontend
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Your backend server
        changeOrigin: true,
      },
    },
  },
})
