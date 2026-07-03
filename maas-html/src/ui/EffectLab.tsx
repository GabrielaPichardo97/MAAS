import { useEffect, useMemo, useState } from "react";
import type { CSSProperties } from "react";
import type { EffectCatalog, EffectCatalogEntry, EffectInputReference, EffectInstance, EffectTarget } from "../types";
import { canonicalEffectFrame, type CanonicalEffectFrame, type LayerEffectFrame } from "../renderer/effectEngine";
import { sceneForEffect, type EffectScene } from "./effectScenes";

const supportLabels = {
  native: "Nativo",
  approximation: "Aproximación 2.5D",
  "input-assisted": "Requiere input",
  preprocessed: "Preprocesado",
} as const;

type DemoTarget = EffectTarget | "both";

interface HandmadeDemo {
  mode: Extract<DemoTarget, "background" | "speaker" | "both">;
  label: string;
  description: string;
  intensity: number;
  params: Record<string, number>;
}

const HANDMADE_DEMOS: Record<string, HandmadeDemo> = {
  "stylize.paper-grain.texture.living-fiber.v1.0.0": {
    mode: "background",
    label: "Fondo móvil · personaje quieto",
    description: "La textura del papel respira detrás de un personaje completamente estable.",
    intensity: 0.85,
    params: { amount: 0.1, grainPx: 4, fiber: 0.45, rateFps: 6 },
  },
  "motion.cutout-wobble.presence.puppet-idle.v1.0.0": {
    mode: "speaker",
    label: "Personaje móvil · fondo quieto",
    description: "El recorte se asienta y oscila sobre un escenario inmóvil.",
    intensity: 0.85,
    params: { travelPx: 6, rotationDeg: 0.7, rateFps: 6 },
  },
  "stylize.line-boil.handmade.edge-jitter.v1.0.0": {
    mode: "both",
    label: "Fondo y personaje móviles",
    description: "Los dos planos hierven con semillas independientes sin deformar el texto.",
    intensity: 0.8,
    params: { amplitudePx: 1.8, rateFps: 8, wavelengthPx: 32 },
  },
};

function defaults(effect: EffectCatalogEntry): Record<string, string | number | boolean> {
  return Object.fromEntries(Object.entries(effect.parameters).map(([name, spec]) => [name, spec.default]));
}

function previewDuration(effect: EffectCatalogEntry, params: Record<string, string | number | boolean>): number {
  const candidates = ["durationMs", "holdMs", "lifeMs", "decayMs", "enterMs", "rampMs"]
    .map((name) => params[name])
    .filter((value): value is number => typeof value === "number" && value > 0);
  return Math.max(900, Math.min(4000, (candidates[0] ?? 1800) * (effect.family === "transition" ? 2 : 1.6)));
}

function demoInputs(effect: EffectCatalogEntry): Record<string, EffectInputReference> {
  return Object.fromEntries(effect.requirements.map((name) => [name, {
    kind: ["morphClip", "keyedSource", "objectMatte"].includes(name) ? "media" : "data",
    assetId: `demo-${name}`,
  }]));
}

function signature(frame: CanonicalEffectFrame): string {
  return JSON.stringify({
    x: Number(frame.x.toFixed(4)), y: Number(frame.y.toFixed(4)), scale: Number(frame.scale.toFixed(4)),
    blur: Number(frame.blur.toFixed(3)), noise: Number(frame.noise.toFixed(3)), incoming: Number(frame.incomingAlpha.toFixed(3)),
    outgoing: Number(frame.outgoingAlpha.toFixed(3)), blackout: Number(frame.blackout.toFixed(3)), source: Math.round(frame.sourceTimeMs),
    panes: frame.splitPanes, morph: Number(frame.morph.toFixed(3)), jump: frame.jumpPhase,
    overlay: Boolean(frame.flash || frame.leak || frame.flare || frame.particles || frame.trails || frame.chroma || frame.matte || frame.blend || frame.tracking || frame.kineticType || frame.lowerThird || frame.colorGrade || frame.audioLevel),
    layers: frame.layers,
    diagnostics: frame.diagnostics.map((item) => item.code),
  });
}

function HandmadeFilterDef({ id, state }: { id: string; state: LayerEffectFrame }) {
  const line = state.lineBoil;
  const grain = state.paperGrain;
  if (!line && !grain) return null;
  const lineFrequency = line ? Math.max(0.006, 1 / line.wavelengthPx) : 0.01;
  const grainFrequency = grain ? Math.min(0.8, 1 / grain.grainPx) : 0.2;
  return <svg className="handmade-filter-def" aria-hidden="true">
    <defs>
      <filter id={id} x="-3%" y="-3%" width="106%" height="106%" colorInterpolationFilters="sRGB">
        {line && <><feTurbulence type="fractalNoise" baseFrequency={lineFrequency} numOctaves="2" seed={Math.round(line.seed + line.step)} result="lineNoise" /><feDisplacementMap in="SourceGraphic" in2="lineNoise" scale={line.amplitudePx * 2} xChannelSelector="R" yChannelSelector="G" result="lineResult" /></>}
        {grain && <><feTurbulence type="fractalNoise" baseFrequency={`${grainFrequency} ${grainFrequency * (1 + grain.fiber * 3)}`} numOctaves="1" seed={Math.round(grain.seed + grain.step)} result="grainNoise" /><feColorMatrix in="grainNoise" type="saturate" values="0" result="monoGrain" /><feComponentTransfer in="monoGrain" result="weightedGrain"><feFuncA type="linear" slope={Math.min(0.5, grain.amount * 2)} /></feComponentTransfer><feBlend in={line ? "lineResult" : "SourceGraphic"} in2="weightedGrain" mode="soft-light" /></>}
      </filter>
    </defs>
  </svg>;
}

function layerStyle(state: LayerEffectFrame, filterId: string): CSSProperties {
  return {
    transform: `translate(${state.xPx}px, ${state.yPx}px) rotate(${state.rotation}rad)`,
    filter: state.lineBoil || state.paperGrain ? `url(#${filterId})` : undefined,
    transformOrigin: "50% 100%",
  };
}

function SceneShot({ frame, scene, shot, opacity, className = "" }: { frame: CanonicalEffectFrame; scene: EffectScene; shot: "a" | "b"; opacity: number; className?: string }) {
  const sourcePhase = frame.sourceTimeMs / 260;
  const trackingX = frame.tracking?.x ?? 0;
  const trackingY = frame.tracking?.y ?? 0;
  const baseX = shot === "a" ? frame.secondaryX : frame.x;
  const baseY = shot === "a" ? frame.secondaryY : frame.y;
  const baseScale = shot === "a" ? frame.secondaryScale : frame.scale;
  const movement = Math.sin(sourcePhase) * 2.5;
  const clip = frame.splitPanes > 1
    ? shot === "a" ? `inset(0 ${50 + frame.splitGapPct / 2}% 0 0)` : `inset(0 0 0 ${50 + frame.splitGapPct / 2}%)`
    : undefined;
  const style = {
    opacity,
    clipPath: clip,
    transform: `translate(${(baseX + trackingX) * 100}%, ${(baseY + trackingY) * 100}%) scale(${baseScale}) rotate(${frame.rotation + (frame.tracking?.rotation ?? 0)}rad)`,
    filter: `blur(${Math.min(16, frame.blur / 4)}px) saturate(${frame.colorGrade?.saturation ?? 1}) contrast(${1 + (frame.colorGrade?.contrast ?? 0) * 0.35})`,
    "--frame-tint": `#${frame.tint.toString(16).padStart(6, "0")}`,
    "--prop-motion": `${movement + trackingX * 80}px`,
    "--matte-feather": `${frame.matte?.featherPx ?? 0}px`,
  } as CSSProperties;
  const actorStyle = frame.morph ? { transform: `scale(${1 + frame.morph * 0.12}, ${1 - frame.morph * 0.05}) skewX(${frame.morph * 5}deg)` } : undefined;
  const propStyle = frame.kineticType
    ? { opacity: Math.max(0.15, frame.kineticType.progress), transform: `translateX(calc(-50% + var(--prop-motion))) translateY(${(1 - frame.kineticType.progress) * 28}px) scale(${0.65 + frame.kineticType.progress * 0.35})` }
    : { transform: `translateX(calc(-50% + var(--prop-motion))) rotate(-2deg)` };
  const backgroundFilterId = `handmade-background-${shot}`;
  const speakerFilterId = `handmade-speaker-${shot}`;
  return (
    <div className={`preview-scene preview-shot shot-${shot} mood-${scene.mood} ${className}`} style={style} aria-hidden={shot === "a"}>
      <HandmadeFilterDef id={backgroundFilterId} state={frame.layers.background} />
      <HandmadeFilterDef id={speakerFilterId} state={frame.layers.speaker} />
      <div className="scene-set" data-effect-layer="background" style={layerStyle(frame.layers.background, backgroundFilterId)}><span className="scene-moon" /><span className="scene-window" /><span className="scene-desk" /></div>
      <div className="scene-speaker-layer" data-effect-layer="speaker" style={layerStyle(frame.layers.speaker, speakerFilterId)}>
        <div className="scene-actor actor-left" style={actorStyle}><span>{(shot === "a" ? scene.leftActor : scene.rightActor).slice(0, 1)}</span><small>{shot === "a" ? scene.leftActor : scene.rightActor}</small></div>
        <div className="scene-actor actor-right"><span>{(shot === "a" ? scene.rightActor : scene.leftActor).slice(0, 1)}</span><small>{shot === "a" ? scene.rightActor : scene.leftActor}</small></div>
      </div>
      <div className="scene-prop" style={propStyle}>{shot === "a" ? scene.prop : `${scene.prop} · B`}</div>
      <div className="scene-slate"><small>{scene.location} · PLANO {shot.toUpperCase()}</small><strong>{scene.title}</strong><p>“{scene.dialogue}”</p></div>
      <div className="scene-grade" />
      {frame.chroma && <div className="scene-key-result" style={{ opacity: 0.35 + frame.chroma.tolerance * 0.5 }} />}
      {frame.matte && <div className="scene-matte" />}
    </div>
  );
}

function ParameterControl({ name, spec, value, update }: { name: string; spec: EffectCatalogEntry["parameters"][string]; value: string | number | boolean; update: (value: string | number | boolean) => void }) {
  const description = `${spec.type}${spec.min !== undefined ? ` · ${spec.min}..${spec.max}` : spec.values ? ` · ${spec.values.join(" / ")}` : ""}`;
  return <label><code>{name}</code><span>{description}</span>{
    spec.type === "number" || spec.type === "integer"
      ? <><input type="range" min={spec.min} max={spec.max} step={spec.type === "integer" ? 1 : 0.05} value={Number(value)} onChange={(event) => update(spec.type === "integer" ? Number.parseInt(event.target.value) : Number(event.target.value))} /><output>{String(value)}</output></>
      : spec.type === "enum"
        ? <select value={String(value)} onChange={(event) => update(event.target.value)}>{spec.values?.map((option) => <option key={option} value={option}>{option}</option>)}</select>
        : spec.type === "boolean"
          ? <input type="checkbox" checked={Boolean(value)} onChange={(event) => update(event.target.checked)} />
          : <input type="color" value={String(value)} onChange={(event) => update(event.target.value)} />
  }</label>;
}

export function EffectLab() {
  const [catalog, setCatalog] = useState<EffectCatalog>();
  const [error, setError] = useState<string>();
  const [query, setQuery] = useState("");
  const [family, setFamily] = useState("all");
  const [support, setSupport] = useState("all");
  const [selectedId, setSelectedId] = useState<string>();
  const [intensity, setIntensity] = useState(0.65);
  const [target, setTarget] = useState<DemoTarget>("frame");
  const [params, setParams] = useState<Record<string, string | number | boolean>>({});
  const [elapsed, setElapsed] = useState(0);
  const [playing, setPlaying] = useState(true);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}effects-catalog.json`)
      .then((response) => { if (!response.ok) throw new Error(`Catálogo ${response.status}`); return response.json() as Promise<EffectCatalog>; })
      .then((value) => { setCatalog(value); setSelectedId(value.effects[0]?.id); })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "No se pudo cargar el catálogo"));
  }, []);

  const selected = catalog?.effects.find((item) => item.id === selectedId);
  useEffect(() => {
    if (!selected) return;
    const demo = HANDMADE_DEMOS[selected.id];
    setParams({ ...defaults(selected), ...(demo?.params ?? {}) });
    setTarget(demo?.mode ?? selected.defaultTarget ?? "frame");
    setIntensity(demo?.intensity ?? 0.65);
    setElapsed(0);
    setPlaying(true);
  }, [selected]);
  const duration = selected ? previewDuration(selected, params) : 1800;
  useEffect(() => {
    if (!playing) return;
    let handle = 0;
    let previous = performance.now();
    const tick = (now: number) => {
      setElapsed((value) => (value + now - previous) % duration);
      previous = now;
      handle = requestAnimationFrame(tick);
    };
    handle = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(handle);
  }, [duration, playing, selectedId]);

  const filtered = useMemo(() => catalog?.effects.filter((effect) => {
    const needle = query.trim().toLocaleLowerCase("es");
    const text = `${effect.displayName} ${effect.id} ${effect.description} ${effect.bestMoment}`.toLocaleLowerCase("es");
    return (!needle || text.includes(needle)) && (family === "all" || effect.family === family) && (support === "all" || effect.supportLevel === support);
  }) ?? [], [catalog, family, query, support]);

  if (error) return <main className="lab-state" role="alert"><h1>No se pudo abrir el catálogo</h1><p>{error}</p></main>;
  if (!catalog || !selected) return <main className="lab-state" role="status">Cargando los efectos…</main>;

  const demo = HANDMADE_DEMOS[selected.id];
  const demoTargets: EffectTarget[] = target === "both" ? ["background", "speaker"] : [target];
  const instances: EffectInstance[] = demoTargets.map((effectTarget, index) => ({
    id: selected.id,
    role: index === 0 ? "dominant" : "support",
    intensity,
    startOffsetMs: 0,
    durationMs: duration,
    target: effectTarget,
    params,
    inputs: demoInputs(selected),
  }));
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const frame = canonicalEffectFrame(instances, elapsed, 42, reduce, { simulateInputs: true, audioLevel: 0.5 + Math.sin(elapsed / 110) * 0.5 });
  const scene = sceneForEffect(selected);
  const effectClass = selected.id.split(".")[1];
  const blendMode = frame.blend?.mode === "normal" ? "normal" : frame.blend?.mode;

  return (
    <main className="effect-lab">
      <header className="lab-header"><div><p className="eyebrow">MAAS · CANONICAL-V2.1</p><h1>Biblioteca de efectos</h1><p>{catalog.effects.length} efectos ejecutables, con preview determinista y requisitos explícitos.</p></div><a href={import.meta.env.BASE_URL}>Volver al reproductor</a></header>
      <section className="lab-filters" aria-label="Filtros del catálogo">
        <label>Buscar<input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Nombre, intención o momento…" /></label>
        <label>Familia<select value={family} onChange={(event) => setFamily(event.target.value)}><option value="all">Todas</option>{catalog.families.map((value) => <option key={value}>{value}</option>)}</select></label>
        <label>Soporte<select value={support} onChange={(event) => setSupport(event.target.value)}><option value="all">Todos</option>{catalog.supportLevels.map((value) => <option key={value} value={value}>{supportLabels[value]}</option>)}</select></label>
        <span role="status">{filtered.length} resultados</span>
      </section>
      <div className="lab-layout">
        <nav className="effect-list" aria-label="Efectos disponibles">{filtered.map((effect) => <button key={effect.id} className={effect.id === selected.id ? "selected" : ""} onClick={() => setSelectedId(effect.id)}><strong>{effect.displayName}</strong><span>{effect.family} · {supportLabels[effect.supportLevel]}</span></button>)}</nav>
        <article className="effect-detail">
          <div className="effect-heading"><div><span className={`support-pill ${selected.supportLevel}`}>{supportLabels[selected.supportLevel]}</span><h2>{selected.displayName}</h2><code>{selected.id}</code></div><div className="effect-heading-controls"><label>Intensidad <output>{intensity.toFixed(2)}</output><input type="range" min="0" max="1" step="0.05" value={intensity} onChange={(event) => setIntensity(Number(event.target.value))} /></label>{selected.targets && <label>Capas del ejemplo<select aria-label="Capas del ejemplo" value={target} onChange={(event) => setTarget(event.target.value as DemoTarget)}>{selected.targets.map((value) => <option key={value} value={value}>{value === "speaker" ? "Solo personaje" : "Solo fondo"}</option>)}{selected.targets.length > 1 && <option value="both">Fondo y personaje</option>}</select></label>}</div></div>
          <div className={`effect-preview fx-${effectClass}`} aria-label={`Demostración de ${selected.displayName}`} data-testid="effect-preview" data-effect-id={selected.id} data-example-mode={demo?.mode} data-effect-signature={signature(frame)}>
            {demo && <div className="layer-example" data-testid="layer-example"><strong>{demo.label}</strong><span>{demo.description}</span><div className="layer-example-status" aria-label="Capas animadas"><i className={target === "background" || target === "both" ? "active" : ""}>Fondo</i><i className={target === "speaker" || target === "both" ? "active" : ""}>Personaje</i><i>Texto quieto</i></div></div>}
            <div className="preview-compositor" data-testid="effect-scene" style={{ mixBlendMode: blendMode as CSSProperties["mixBlendMode"] }}>
              <SceneShot frame={frame} scene={scene} shot="a" opacity={frame.outgoingAlpha} className="outgoing-shot" />
              <SceneShot frame={frame} scene={scene} shot="b" opacity={frame.incomingAlpha} className="incoming-shot" />
              {frame.trails && Array.from({ length: Math.min(8, frame.trails.count) }, (_, index) => <div className="scene-trail" key={index} style={{ opacity: Math.pow(frame.trails!.decay, index + 1), transform: `translate(${(index + 1) * -2.5}%, ${(index + 1) * 1.5}%)` }} />)}
              {frame.noise > 0 && <div className="scene-noise" style={{ opacity: Math.min(0.75, frame.noise) }} />}
              {frame.leak && <div className="scene-leak" style={{ opacity: frame.leak.alpha, left: `${frame.leak.x * 100}%`, background: `#${frame.leak.color.toString(16).padStart(6, "0")}` }} />}
              {frame.flare && <div className="scene-flare" style={{ opacity: frame.flare.alpha, left: `${frame.flare.x * 100}%`, top: `${frame.flare.y * 100}%` }} />}
              {frame.particles && <div className="scene-particles">{Array.from({ length: Math.min(30, frame.particles.count) }, (_, index) => <i key={index} style={{ left: `${(index * 37) % 100}%`, top: `${(index * 61 + frame.particles!.progress * 100 * (1 + frame.particles!.gravity)) % 100}%` }} />)}</div>}
              {frame.lowerThird && <div className="demo-lower-third" style={{ left: `${frame.lowerThird.safeMarginPct}%`, transform: `translateX(${(frame.lowerThird.progress - 1) * 120}%)` }}><strong>{scene.leftActor}</strong><span>{scene.location}</span></div>}
              {frame.audioLevel !== undefined && <div className="audio-meter" style={{ transform: `scaleY(${0.15 + frame.audioLevel * 0.85})` }} />}
              {frame.blackout > 0 && <div className="preview-blackout" style={{ opacity: frame.blackout }} />}
              {frame.flash && <div className="preview-flash" style={{ background: `#${frame.flash.color.toString(16).padStart(6, "0")}`, opacity: frame.flash.alpha }} />}
            </div>
            <div className="preview-transport"><button type="button" onClick={() => setPlaying((value) => !value)} aria-label={playing ? "Pausar demostración" : "Reproducir demostración"}>{playing ? "Ⅱ" : "▶"}</button><button type="button" onClick={() => { setElapsed(0); setPlaying(true); }}>Reiniciar</button><input aria-label="Tiempo de la demostración" type="range" min="0" max={duration} step="10" value={Math.min(elapsed, duration)} onChange={(event) => { setPlaying(false); setElapsed(Number(event.target.value)); }} /><output>{Math.round(elapsed)} ms</output></div>
            {selected.requirements.length > 0 && <span className="concept-badge">Demo con input simulado · producción requiere {selected.requirements.join(", ")}</span>}
            {frame.diagnostics.map((item) => <span className="effect-diagnostic" role="status" key={`${item.code}-${item.effectId}`}>{item.message}{item.fallbackId ? ` · fallback ${item.fallbackId}` : ""}</span>)}
          </div>
          <div className="effect-copy"><section><h3>Qué hace</h3><p>{selected.description}</p></section><section><h3>Mejor momento</h3><p>{selected.bestMoment}</p></section><section><h3>Evítalo cuando</h3><ul>{selected.avoidWhen.map((item) => <li key={item}>{item}</li>)}</ul></section></div>
          <section><h3>Parámetros programables</h3><div className="parameter-grid">{Object.entries(selected.parameters).map(([name, spec]) => <ParameterControl key={name} name={name} spec={spec} value={params[name]} update={(value) => setParams((current) => ({ ...current, [name]: value }))} />)}</div></section>
          <dl className="effect-meta"><div><dt>Requisitos</dt><dd>{selected.requirements.join(", ") || "Ninguno"}</dd></div><div><dt>Fallback</dt><dd>{selected.fallbackId ?? "Sin sustitución automática"}</dd></div><div><dt>Riesgo fotosensible</dt><dd>{selected.photosensitivityRisk}</dd></div><div><dt>Movimiento reducido</dt><dd>{selected.reducedMotion}</dd></div><div><dt>Costo</dt><dd>{selected.renderCost}</dd></div><div><dt>Móvil</dt><dd>{selected.mobileSafe ? "Compatible" : "Requiere degradación"}</dd></div></dl>
          <section><h3>{instances.length > 1 ? "Tokens listos para aprobar" : "Token listo para aprobar"}</h3><pre>{instances.map((instance) => `{{fx ${selected.id} role=${instance.role} intensity=${intensity.toFixed(2)} target=${instance.target}${selected.requirements.map((name) => ` ${name}=asset-${name}`).join("")}}}`).join("\n")}</pre></section>
        </article>
      </div>
    </main>
  );
}
