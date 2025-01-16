import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,  // Change to a different port if necessary
    host: '0.0.0.0',  // Bind to all network interfaces, not just localhost (::1)
  }
});
