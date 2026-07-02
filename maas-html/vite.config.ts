import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => ({
  base: mode === "pages" ? "/MAAS/" : "/",
  plugins: [react()],
  build: {
    sourcemap: true,
    assetsDir: "assets",
    outDir: "dist/player",
    rollupOptions: {
      input: {
        player: new URL("./index.html", import.meta.url).pathname,
        episode0: new URL("./episodes/episodio-0-prueba-renderizar/index.html", import.meta.url).pathname,
        effects: new URL("./effects/index.html", import.meta.url).pathname,
      },
    },
  },
}));
