import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const devHost = process.env.VITE_DEV_HOST ?? "127.0.0.1";
const devPort = Number(process.env.VITE_DEV_PORT ?? 5173);
const apiProxyTarget = process.env.VITE_API_PROXY_TARGET ?? "http://127.0.0.1:8081";

export default defineConfig({
  plugins: [react()],
  server: {
    host: devHost,
    port: devPort,
    proxy: {
      "/api": {
        target: apiProxyTarget,
        changeOrigin: true
      }
    }
  }
});
