import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://8.160.186.192:8000',
        changeOrigin: true
      },
      '/avatars': {
        target: 'http://8.160.186.192:8000',
        changeOrigin: true
      }
    }
  }
})
