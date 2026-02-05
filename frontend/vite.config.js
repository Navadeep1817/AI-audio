import { defineConfig } from "vite";
import react            from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  server: {
    port: 5173,

    // Proxy API requests to the FastAPI backend during development.
    // In production the reverse-proxy (nginx / ALB) handles this.
    proxy: {
      "/api": {
        target:     "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },

  // Build output goes to /dist — serve with `vite preview` or a static host
  build: {
    outDir: "dist",
  },
});