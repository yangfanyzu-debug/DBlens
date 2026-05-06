import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/dblens/' : '/',
  plugins: [vue()],
  resolve: {
    alias: { '@': resolve(__dirname, 'src') },
  },
  server: {
    port: 5173,
    proxy: {
      '/dblens-api': {
        target: 'http://localhost:8000',
        rewrite: (path) => path.replace(/^\/dblens-api/, '/api'),
      },
      '/dblens-api/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        rewrite: (path) => path.replace(/^\/dblens-api\/ws/, '/ws'),
      },
    },
  },
}))
