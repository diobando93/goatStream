import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "GoatStream",
        short_name: "GoatStream",
        description: "Live sports streaming aggregator",
        theme_color: "#0a0a0a",
        background_color: "#0a0a0a",
        display: "standalone",
        orientation: "landscape",
        icons: [
          {
            src: "icon.svg",
            sizes: "any",
            type: "image/svg+xml",
            purpose: "any maskable",
          },
        ],
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,svg}"],
      },
    }),
  ],
});
