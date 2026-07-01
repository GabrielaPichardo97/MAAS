import { mountEpisodePlayer } from "./player";

const root = document.getElementById("root");
if (!root) throw new Error("Falta #root");
mountEpisodePlayer(root, "/episodes/demo/episode.manifest.json", { orientation: "auto", autoplay: false, reducedMotion: "system" });
