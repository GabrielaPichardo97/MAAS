import { mountEpisodePlayer } from "./player";

const root = document.getElementById("root");
if (!root) throw new Error("Falta #root");
mountEpisodePlayer(root, "/episodes/episodio-0-prueba-renderizar/episode.manifest.json", {
  orientation: "landscape",
  autoplay: false,
  reducedMotion: "system",
});
