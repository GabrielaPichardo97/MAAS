import { useEffect, useMemo, useRef, useState } from "react";
import type { EpisodeManifest, TimelineCue } from "../types";
import type { PlayerOptions } from "../player";
import { MaasStage } from "../renderer/MaasStage";

export function App({ manifestUrl, options }: { manifestUrl: string; options: PlayerOptions }) {
  const host = useRef<HTMLDivElement>(null);
  const stage = useRef<MaasStage | null>(null);
  const positionRef = useRef(0);
  const [manifest, setManifest] = useState<EpisodeManifest>();
  const [started, setStarted] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [position, setPosition] = useState(0);
  const active = useMemo<TimelineCue | undefined>(() => manifest?.timeline.find((cue) => cue.type !== "scene" && position >= cue.startMs && position < cue.startMs + cue.durationMs), [manifest, position]);

  useEffect(() => { fetch(manifestUrl).then((response) => { if (!response.ok) throw new Error(`Manifest ${response.status}`); return response.json(); }).then(setManifest); }, [manifestUrl]);
  useEffect(() => {
    if (!manifest || !host.current) return;
    const value = new MaasStage(manifest.assetUrls ?? {});
    stage.current = value;
    void value.init(host.current);
    const observer = new ResizeObserver(([entry]) => value.resize(entry.contentRect.width, entry.contentRect.height));
    observer.observe(host.current);
    return () => { observer.disconnect(); value.destroy(); };
  }, [manifest]);
  useEffect(() => { if (active) void stage.current?.show(active); }, [active?.id]);
  useEffect(() => {
    if (!playing || !manifest) return;
    let frame = 0;
    let last = performance.now();
    const tick = (now: number) => {
      const delta = now - last;
      last = now;
      setPosition((old) => {
        const next = Math.min(manifest.durationMs, old + delta);
        positionRef.current = next;
        return next;
      });
      stage.current?.update(active ? positionRef.current - active.startMs : 0);
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing, manifest, active?.id]);

  if (!manifest) return <p role="status">Cargando episodio…</p>;
  return <main className="player" data-orientation={options.orientation ?? "auto"}>
    <h1>{manifest.title}</h1>
    <div className="stage" ref={host} aria-hidden="true" />
    <p className="caption" aria-live="polite"><strong>{active?.speakerLabel ?? active?.speaker}</strong>{active?.speaker ? ": " : ""}{active?.text}</p>
    {!started ? <button onClick={() => { setStarted(true); setPlaying(options.autoplay ?? false); }}>Iniciar episodio</button> : <div className="controls">
      <button onClick={() => setPlaying((value) => !value)}>{playing ? "Pausar" : "Reproducir"}</button>
      <input aria-label="Progreso" type="range" min={0} max={manifest.durationMs} value={position} onChange={(event) => { const next = Number(event.target.value); positionRef.current = next; setPosition(next); }} />
    </div>}
  </main>;
}
