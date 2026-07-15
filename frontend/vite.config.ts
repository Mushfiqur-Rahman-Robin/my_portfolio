import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

function deferCssPlugin() {
  return {
    name: 'defer-css',
    enforce: 'post' as const,
    transformIndexHtml(html: string) {
      return html.replace(
        /<link rel="stylesheet"\s([^>]*?)href="([^"]+)"([^>]*?)>/g,
        (_match: string, before: string, href: string, after: string) => {
          if (/(?:onload|media\s*=)/.test(before + after)) return _match;
          if (!(before + after).includes('crossorigin')) return _match;
          return `<link rel="preload" as="style" href="${href}" crossorigin />
<link rel="stylesheet" href="${href}" media="print" onload="this.media='all'" crossorigin />
<noscript><link rel="stylesheet" href="${href}" crossorigin /></noscript>`;
        }
      );
    },
  };
}

export default defineConfig({
  plugins: [react(), deferCssPlugin()],
  server: {
    host: true,
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          axios: ['axios'],
        },
      },
    },
  },
})
