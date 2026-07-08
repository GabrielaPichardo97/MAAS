import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { EpisodeManifest } from "../types";
import type { PlayerOptions } from "../player";
import { MaasStage } from "../renderer/MaasStage";
import { activeInteractions, activeNarrativeCue, activeSubtitle, clampPosition, formatTime } from "../timeline";
import { rebaseManifestAssets } from "../assetUrls";
import type { Interaction } from "../types";

export function App({ manifestUrl, options }: { manifestUrl: string; options: PlayerOptions }) {
  const player = useRef<HTMLElement>(null);
  const host = useRef<HTMLDivElement>(null);
  const stage = useRef<MaasStage | null>(null);
  const positionRef = useRef(0);
  const [manifest, setManifest] = useState<EpisodeManifest>();
  const [loadError, setLoadError] = useState<string>();
  const [renderError, setRenderError] = useState<string>();
  const [started, setStarted] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [captions, setCaptions] = useState(true);
  const [position, setPosition] = useState(0);
  const [fullscreen, setFullscreen] = useState(false);
  const [systemReducedMotion, setSystemReducedMotion] = useState(false);
  const [openPanel, setOpenPanel] = useState<{ id: string; label: string } | null>(null);

  const active = useMemo(
    () => (manifest ? activeNarrativeCue(manifest.timeline, position) : undefined),
    [manifest, position],
  );
  const caption = useMemo(
    () => (manifest ? activeSubtitle(manifest.subtitles, manifest.timeline, position) : undefined),
    [manifest, position],
  );
  const interactions = useMemo(
    () => (manifest ? activeInteractions(manifest.interactions, position) : []),
    [manifest, position],
  );
  const reducedMotion = options.reducedMotion === "on" || (options.reducedMotion === "system" && systemReducedMotion);

  const seek = useCallback((next: number) => {
    if (!manifest) return;
    const clamped = clampPosition(next, manifest.durationMs);
    positionRef.current = clamped;
    setPosition(clamped);
    if (clamped >= manifest.durationMs) setPlaying(false);
  }, [manifest]);

  useEffect(() => {
    const controller = new AbortController();
    fetch(manifestUrl, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error(`No se pudo cargar el manifiesto (${response.status})`);
        return response.json() as Promise<EpisodeManifest>;
      })
      .then((value) => setManifest(rebaseManifestAssets(value, import.meta.env.BASE_URL)))
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") return;
        setLoadError(error instanceof Error ? error.message : "Error desconocido al cargar el episodio");
      });
    return () => controller.abort();
  }, [manifestUrl]);

  useEffect(() => {
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setSystemReducedMotion(query.matches);
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    if (!manifest || !host.current) return;
    const value = new MaasStage(manifest.assetUrls);
    stage.current = value;
    void value.init(host.current).catch((error: unknown) => {
      setRenderError(error instanceof Error ? error.message : "No se pudo iniciar el escenario gráfico");
    });
    const observer = new ResizeObserver(([entry]) => value.resize(entry.contentRect.width, entry.contentRect.height));
    observer.observe(host.current);
    return () => {
      observer.disconnect();
      value.destroy();
      stage.current = null;
    };
  }, [manifest]);

  useEffect(() => {
    void stage.current?.show(active);
    stage.current?.update(active ? position - active.startMs : 0, reducedMotion);
  }, [active, position, reducedMotion]);

  useEffect(() => {
    if (!playing || !manifest) return;
    let frame = 0;
    let last = performance.now();
    const tick = (now: number) => {
      const delta = now - last;
      last = now;
      const next = Math.min(manifest.durationMs, positionRef.current + delta);
      positionRef.current = next;
      setPosition(next);
      if (next >= manifest.durationMs) {
        setPlaying(false);
        return;
      }
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing, manifest]);

  useEffect(() => {
    const update = () => setFullscreen(document.fullscreenElement === player.current);
    document.addEventListener("fullscreenchange", update);
    return () => document.removeEventListener("fullscreenchange", update);
  }, []);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (!started || !manifest) return;
      const target = event.target as HTMLElement | null;
      if (target?.matches("input, button")) return;
      if (event.key === " ") {
        event.preventDefault();
        setPlaying((value) => !value);
      } else if (event.key === "ArrowRight") {
        event.preventDefault();
        seek(positionRef.current + 5000);
      } else if (event.key === "ArrowLeft") {
        event.preventDefault();
        seek(positionRef.current - 5000);
      } else if (event.key.toLowerCase() === "c") {
        setCaptions((value) => !value);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [manifest, seek, started]);

  const toggleFullscreen = async () => {
    if (!player.current) return;
    if (document.fullscreenElement) await document.exitFullscreen();
    else await player.current.requestFullscreen();
  };

  const triggerInteraction = useCallback((interaction: Interaction) => {
    const action = interaction.action;
    if (action.type === "pause") {
      setPlaying(false);
    } else if (action.type === "seek") {
      setStarted(true);
      seek(action.positionMs);
    } else if (action.type === "openPanel") {
      setOpenPanel({ id: action.panelId, label: interaction.label });
      setPlaying(false);
    } else if (action.type === "openUrl") {
      if (action.url.startsWith("/") && !action.url.startsWith("//") && !action.url.includes("..")) {
        window.location.assign(action.url);
      }
    } else if (action.type === "emit") {
      player.current?.dispatchEvent(new CustomEvent("maas-interaction", {
        bubbles: true,
        detail: { id: interaction.id, event: action.event, detail: action.detail ?? {} },
      }));
    }
  }, [seek]);

  if (loadError) return <main className="load-state error" role="alert"><h1>No pudimos abrir el episodio</h1><p>{loadError}</p></main>;
  if (!manifest) return <main className="load-state" role="status"><span className="loader" />Cargando episodio…</main>;

  const speaker = caption?.speakerLabel;
  const captionText = position >= manifest.durationMs ? "Fin del preview" : caption?.text ?? "Preparando escena...";

  return (
    <main className="player" data-orientation="landscape" ref={player}>
      <header className="player-header">
        <div>
          <p className="eyebrow">MAAS · PRIMER HTML</p>
          <h1>{manifest.title}</h1>
        </div>
        <span className="preview-badge">Media real · sin audio</span>
      </header>

      <section className="stage-shell" aria-label="Escenario del episodio">
        <div className="stage" ref={host} aria-hidden="true" />
        {started && interactions.length > 0 && (
          <div className="interaction-layer" aria-label="Interacciones del episodio" data-testid="interaction-layer">
            {interactions.map((interaction) => {
              const style = interaction.target
                ? {
                    left: `${interaction.target.x * 100}%`,
                    top: `${interaction.target.y * 100}%`,
                    width: `${interaction.target.width * 100}%`,
                    height: `${interaction.target.height * 100}%`,
                  }
                : undefined;
              return (
                <button
                  key={interaction.id}
                  type="button"
                  className={`interaction-trigger ${interaction.type}`}
                  style={style}
                  data-testid={`interaction-${interaction.id}`}
                  onClick={() => triggerInteraction(interaction)}
                >
                  {interaction.label}
                </button>
              );
            })}
          </div>
        )}
        {renderError ? (
          <div className="start-card render-error" role="alert">
            <strong>No se pudo iniciar PixiJS</strong>
            <span>{renderError}</span>
          </div>
        ) : !started && (
          <div className="start-card">
            <p>Una prueba visual de {(manifest.durationMs / 1000).toFixed(1)} segundos</p>
            <button className="primary" onClick={() => { seek(0); setStarted(true); setPlaying(true); }}>
              <span aria-hidden="true">▶</span> Iniciar episodio
            </button>
          </div>
        )}
        {openPanel ? (
          <div className="interaction-panel" role="dialog" aria-modal="false" aria-label={openPanel.label}>
            <strong>{openPanel.label}</strong>
            <span>{openPanel.id}</span>
            <button type="button" onClick={() => setOpenPanel(null)}>Cerrar</button>
          </div>
        ) : null}
      </section>

      <div className={`caption ${captions ? "" : "caption-hidden"}`} aria-live="polite" aria-atomic="true">
        {captions ? <><strong>{speaker}</strong>{speaker ? ": " : ""}{captionText}</> : <span>Captions desactivados</span>}
      </div>

      <section className="control-panel" aria-label="Controles de reproducción">
        <div className="transport">
          <button className="icon-button" disabled={!started} onClick={() => setPlaying((value) => !value)} aria-label={playing ? "Pausar" : "Reproducir"}>
            <span aria-hidden="true">{playing ? "Ⅱ" : "▶"}</span>
          </button>
          <button className="icon-button jump-button" disabled={!started} onClick={() => seek(positionRef.current - 5000)} aria-label="Retroceder 5 segundos">−5</button>
          <button className="icon-button jump-button" disabled={!started} onClick={() => seek(positionRef.current + 5000)} aria-label="Adelantar 5 segundos">+5</button>
          <span className="timecode">{formatTime(position)} / {formatTime(manifest.durationMs)}</span>
          <input
            aria-label="Progreso del episodio"
            type="range"
            min={0}
            max={manifest.durationMs}
            step={40}
            value={position}
            onChange={(event) => seek(Number(event.target.value))}
          />
        </div>
        <div className="secondary-controls">
          <button disabled title="Este preview no contiene pistas de audio" aria-label="Audio no disponible">🔇 <span>Sin audio</span></button>
          <button onClick={() => setCaptions((value) => !value)} aria-pressed={captions}>CC <span>{captions ? "Ocultar" : "Mostrar"}</span></button>
          <button onClick={() => void toggleFullscreen()} aria-pressed={fullscreen}><span aria-hidden="true">{fullscreen ? "↙" : "↗"}</span> <span>Pantalla</span></button>
        </div>
      </section>

      <footer>
        <p><strong>Atajos:</strong> espacio reproduce/pausa · ← → saltan 5 s · C alterna captions</p>
        <p className="warning-note">Este episodio usa únicamente los personajes y fondos PNG requeridos, verificados por hash y autorizados para MAAS.</p>
      </footer>
    </main>
  );
}
