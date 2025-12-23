// @ts-nocheck
import path from "path";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

const env = loadEnv("", process.cwd());

const mergedEnv = {
  ...env,
  ...process.env,
};

const backendHost = mergedEnv.BACKEND_HOST;
const backendPort = mergedEnv.BACKEND_PORT;
const backendUrl = `${backendHost}:${backendPort}`;

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: Number(mergedEnv.FRONTEND_PORT),
    proxy: {
        "/api": {
          target: backendUrl,
          changeOrigin: true,
          secure: false,
        },
      },
  },
  build: {
    sourcemap: false,
    minify: "esbuild",
  },
});

