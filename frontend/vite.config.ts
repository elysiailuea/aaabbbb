import { defineConfig } from "vite";
// @ts-ignore
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    port: 5173,
  },
});