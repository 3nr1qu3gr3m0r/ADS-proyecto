// ============ PROMPT ============
// Configura Vite como bundler del frontend React con el plugin oficial
// @vitejs/plugin-react, usando la configuración por defecto para
// desarrollo con HMR y builds de producción optimizados.
// ======== FIN DEL PROMPT ========

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
