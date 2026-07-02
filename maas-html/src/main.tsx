import { mountEpisodePlayer } from "./player";
import { lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const EffectLab = lazy(() => import("./ui/EffectLab").then((module) => ({ default: module.EffectLab })));

const root = document.getElementById("root");
if (!root) throw new Error("Falta #root");
const routePath = window.location.pathname.startsWith(import.meta.env.BASE_URL)
  ? `/${window.location.pathname.slice(import.meta.env.BASE_URL.length)}`
  : window.location.pathname;
if (routePath.startsWith("/effects") || new URLSearchParams(window.location.search).get("view") === "effects") {
  createRoot(root).render(<Suspense fallback={<main className="lab-state" role="status">Cargando laboratorio…</main>}><EffectLab /></Suspense>);
} else {
  const episodeMatch = routePath.match(/^\/episodes\/([a-z0-9-]+)\/?$/);
  const episodeId = episodeMatch?.[1] ?? "episodio-0-prueba-renderizar";
  mountEpisodePlayer(root, `${import.meta.env.BASE_URL}episodes/${episodeId}/episode.manifest.json`, {
    orientation: "landscape",
    autoplay: false,
    reducedMotion: "system",
  });
}
