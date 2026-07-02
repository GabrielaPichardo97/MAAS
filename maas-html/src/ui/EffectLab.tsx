import { useEffect, useMemo, useState } from "react";
import type { CSSProperties } from "react";
import type { EffectCatalog, EffectCatalogEntry, EffectInstance } from "../types";
import { canonicalEffectFrame } from "../renderer/effectEngine";
import { sceneForEffect } from "./effectScenes";

const supportLabels = {
  native: "Nativo",
  approximation: "Aproximación 2.5D",
  "input-assisted": "Requiere input",
  preprocessed: "Preprocesado",
} as const;

function defaults(effect: EffectCatalogEntry): Record<string, string | number | boolean> {
  return Object.fromEntries(Object.entries(effect.parameters).map(([name, spec]) => [name, spec.default]));
}

export function EffectLab() {
  const [catalog, setCatalog] = useState<EffectCatalog>();
  const [error, setError] = useState<string>();
  const [query, setQuery] = useState("");
  const [family, setFamily] = useState("all");
  const [support, setSupport] = useState("all");
  const [selectedId, setSelectedId] = useState<string>();
  const [intensity, setIntensity] = useState(0.65);
  const [params, setParams] = useState<Record<string, string | number | boolean>>({});
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}effects-catalog.json`)
      .then((response) => { if (!response.ok) throw new Error(`Catálogo ${response.status}`); return response.json() as Promise<EffectCatalog>; })
      .then((value) => { setCatalog(value); setSelectedId(value.effects[0]?.id); })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "No se pudo cargar el catálogo"));
  }, []);

  const selected = catalog?.effects.find((item) => item.id === selectedId);
  useEffect(() => { if (selected) setParams(defaults(selected)); }, [selected]);
  useEffect(() => {
    let handle = 0;
    const started = performance.now();
    const tick = (now: number) => { setElapsed((now - started) % 3000); handle = requestAnimationFrame(tick); };
    handle = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(handle);
  }, [selectedId]);

  const filtered = useMemo(() => catalog?.effects.filter((effect) => {
    const needle = query.trim().toLocaleLowerCase("es");
    const text = `${effect.displayName} ${effect.id} ${effect.description} ${effect.bestMoment}`.toLocaleLowerCase("es");
    return (!needle || text.includes(needle)) && (family === "all" || effect.family === family) && (support === "all" || effect.supportLevel === support);
  }) ?? [], [catalog, family, query, support]);

  if (error) return <main className="lab-state" role="alert"><h1>No se pudo abrir el catálogo</h1><p>{error}</p></main>;
  if (!catalog || !selected) return <main className="lab-state" role="status">Cargando los efectos…</main>;

  const instance: EffectInstance = { id: selected.id, role: "dominant", intensity, startOffsetMs: 0, durationMs: 3000, params };
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const frame = canonicalEffectFrame([instance], elapsed, 42, reduce);
  const scene = sceneForEffect(selected);
  const effectClass = selected.id.split(".")[1];
  const previewStyle = {
    transform: `translate(${frame.x * 100}%, ${frame.y * 100}%) scale(${frame.scale}) rotate(${frame.rotation}rad)`,
    opacity: frame.alpha,
    filter: `blur(${Math.min(12, frame.blur / 5)}px)`,
    "--frame-tint": `#${frame.tint.toString(16).padStart(6, "0")}`,
  } as CSSProperties;

  return (
    <main className="effect-lab">
      <header className="lab-header">
        <div><p className="eyebrow">MAAS · CANONICAL-V2</p><h1>Biblioteca de efectos</h1><p>{catalog.effects.length} efectos documentados con criterio narrativo, parámetros y soporte verificable.</p></div>
        <a href={import.meta.env.BASE_URL}>Volver al reproductor</a>
      </header>

      <section className="lab-filters" aria-label="Filtros del catálogo">
        <label>Buscar<input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Nombre, intención o momento…" /></label>
        <label>Familia<select value={family} onChange={(event) => setFamily(event.target.value)}><option value="all">Todas</option>{catalog.families.map((value) => <option key={value}>{value}</option>)}</select></label>
        <label>Soporte<select value={support} onChange={(event) => setSupport(event.target.value)}><option value="all">Todos</option>{catalog.supportLevels.map((value) => <option key={value} value={value}>{supportLabels[value]}</option>)}</select></label>
        <span role="status">{filtered.length} resultados</span>
      </section>

      <div className="lab-layout">
        <nav className="effect-list" aria-label="Efectos disponibles">
          {filtered.map((effect) => <button key={effect.id} className={effect.id === selected.id ? "selected" : ""} onClick={() => setSelectedId(effect.id)}><strong>{effect.displayName}</strong><span>{effect.family} · {supportLabels[effect.supportLevel]}</span></button>)}
        </nav>

        <article className="effect-detail">
          <div className="effect-heading"><div><span className={`support-pill ${selected.supportLevel}`}>{supportLabels[selected.supportLevel]}</span><h2>{selected.displayName}</h2><code>{selected.id}</code></div><label>Intensidad <output>{intensity.toFixed(2)}</output><input type="range" min="0" max="1" step="0.05" value={intensity} onChange={(event) => setIntensity(Number(event.target.value))} /></label></div>

          <div className="effect-preview" aria-label={`Demostración conceptual de ${selected.displayName}`}>
            <div className={`preview-scene mood-${scene.mood} fx-${effectClass}`} style={previewStyle} data-testid="effect-scene">
              <div className="scene-set"><span className="scene-moon" /><span className="scene-window" /><span className="scene-desk" /></div>
              <div className="scene-divider" />
              <div className="scene-actor actor-left"><span>{scene.leftActor.slice(0, 1)}</span><small>{scene.leftActor}</small></div>
              <div className="scene-prop">{scene.prop}</div>
              <div className="scene-actor actor-right"><span>{scene.rightActor.slice(0, 1)}</span><small>{scene.rightActor}</small></div>
              <div className="scene-slate"><small>{scene.location}</small><strong>{scene.title}</strong><p>“{scene.dialogue}”</p></div>
              <div className="scene-grade" />
              {frame.noise > 0 && <div className="scene-noise" style={{ opacity: Math.min(0.75, frame.noise) }} />}
              {frame.leak && <div className="scene-leak" style={{ opacity: frame.leak.alpha, left: `${frame.leak.x * 100}%`, background: `#${frame.leak.color.toString(16).padStart(6, "0")}` }} />}
              {frame.flare && <div className="scene-flare" style={{ opacity: frame.flare.alpha, left: `${frame.flare.x * 100}%`, top: `${frame.flare.y * 100}%` }} />}
              {frame.particles && <div className="scene-particles">{Array.from({ length: Math.min(24, frame.particles.count) }, (_, index) => <i key={index} style={{ left: `${(index * 37) % 100}%`, top: `${(index * 61 + frame.particles!.progress * 100) % 100}%` }} />)}</div>}
            </div>
            {frame.flash && <div className="preview-flash" style={{ background: `#${frame.flash.color.toString(16).padStart(6, "0")}`, opacity: frame.flash.alpha }} />}
            {selected.supportLevel !== "native" && <span className="concept-badge">Demostración conceptual; revisa requisitos</span>}
          </div>

          <div className="effect-copy"><section><h3>Qué hace</h3><p>{selected.description}</p></section><section><h3>Mejor momento</h3><p>{selected.bestMoment}</p></section><section><h3>Evítalo cuando</h3><ul>{selected.avoidWhen.map((item) => <li key={item}>{item}</li>)}</ul></section></div>

          <section><h3>Parámetros programables</h3><div className="parameter-grid">{Object.entries(selected.parameters).map(([name, spec]) => <label key={name}><code>{name}</code><span>{spec.type}{spec.min !== undefined ? ` · ${spec.min}..${spec.max}` : spec.values ? ` · ${spec.values.join(" / ")}` : ""}</span>{spec.type === "number" || spec.type === "integer" ? <input type="range" min={spec.min} max={spec.max} step={spec.type === "integer" ? 1 : 0.05} value={Number(params[name])} onChange={(event) => setParams((value) => ({ ...value, [name]: spec.type === "integer" ? Number.parseInt(event.target.value) : Number(event.target.value) }))} /> : <output>{String(params[name])}</output>}</label>)}</div></section>

          <dl className="effect-meta"><div><dt>Requisitos</dt><dd>{selected.requirements.join(", ") || "Ninguno"}</dd></div><div><dt>Fallback</dt><dd>{selected.fallbackId ?? "Sin sustitución automática"}</dd></div><div><dt>Riesgo fotosensible</dt><dd>{selected.photosensitivityRisk}</dd></div><div><dt>Movimiento reducido</dt><dd>{selected.reducedMotion}</dd></div><div><dt>Costo</dt><dd>{selected.renderCost}</dd></div><div><dt>Móvil</dt><dd>{selected.mobileSafe ? "Compatible" : "Requiere degradación"}</dd></div></dl>

          <section><h3>Token listo para aprobar</h3><pre>{`{{fx ${selected.id} role=dominant intensity=${intensity.toFixed(2)} target=frame}}`}</pre></section>
        </article>
      </div>
    </main>
  );
}
