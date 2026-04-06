import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
  root: ".",
  base: "/static/",
  build: {
    manifest: "manifest.json",
    outDir: "staticfiles",
    rollupOptions: {
      input: "static/src/main.js",
    },
  },
});
