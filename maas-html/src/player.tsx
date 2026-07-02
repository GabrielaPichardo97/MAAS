import { createRoot, type Root } from "react-dom/client";
import { App } from "./ui/App";
import "./styles.css";

export interface PlayerOptions {
  orientation?: "landscape" | "portrait" | "auto";
  autoplay?: boolean;
  reducedMotion?: "system" | "on" | "off";
}

export function mountEpisodePlayer(element: HTMLElement, manifestUrl: string, options: PlayerOptions = {}): () => void {
  const root: Root = createRoot(element);
  root.render(<App manifestUrl={manifestUrl} options={options} />);
  return () => root.unmount();
}
