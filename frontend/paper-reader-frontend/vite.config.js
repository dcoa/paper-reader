import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  optimizeDeps: {
    include: ['pdfjs-dist'],
  },
  assetsInclude: ['**/*.worker.js', '**/*.worker.min.js'],
  build: {
    rollupOptions: {
      external: [],
    },
  },
  server: {
    port: 3999,
    host: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5600',
        changeOrigin: true,
        secure: false,
        ws: true,
      }
    }
  },
  define: {
    __VUE_PROD_DEVTOOLS__: false
  }
})
