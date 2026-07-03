import { describe, expect, it } from "vitest";
import catalogJson from "../../public/effects-catalog.json";
import { canonicalEffectFrame, REGISTERED_EFFECT_IDS } from "../../src/renderer/effectEngine";
import { EFFECT_IDS, type EffectCatalog, type EffectCatalogEntry, type EffectInstance } from "../../src/types";

const catalog = catalogJson as unknown as EffectCatalog;

function instance(entry: EffectCatalogEntry, overrides: Partial<EffectInstance> = {}): EffectInstance {
  return {
    id: entry.id,
    role: "dominant",
    intensity: 1,
    startOffsetMs: 0,
    durationMs: 1200,
    params: Object.fromEntries(Object.entries(entry.parameters).map(([name, spec]) => [name, spec.default])),
    inputs: Object.fromEntries(entry.requirements.map((name) => [name, { kind: ["morphClip", "keyedSource", "objectMatte"].includes(name) ? "media" : "data", assetId: `fixture-${name}` }])),
    ...overrides,
  };
}

function observable(frame: ReturnType<typeof canonicalEffectFrame>) {
  const { activeEffectIds: _active, diagnostics: _diagnostics, ...state } = frame;
  return state;
}

describe("registro canonical-v2.1", () => {
  it("registra exactamente los 37 efectos del catálogo", () => {
    expect([...REGISTERED_EFFECT_IDS].sort()).toEqual([...EFFECT_IDS].sort());
    expect(catalog.effects.map((effect) => effect.id).sort()).toEqual([...EFFECT_IDS].sort());
  });

  it.each(catalog.effects.map((entry) => [entry.displayName, entry] as const))("%s produce estado observable", (_name, entry) => {
    const effect = instance(entry);
    const samples = [20, 220, 560, 940].map((elapsed) => observable(canonicalEffectFrame([effect], elapsed, 42, false, { simulateInputs: true, audioLevel: 0.72 })));
    const baselines = [20, 220, 560, 940].map((elapsed) => observable(canonicalEffectFrame([], elapsed, 42, false)));
    expect(samples.some((sample, index) => JSON.stringify(sample) !== JSON.stringify(baselines[index]))).toBe(true);
  });

  it("reporta un renderer desconocido en vez de ignorarlo", () => {
    const unknown = { ...instance(catalog.effects[0]), id: "transition.desconocida.test.v1.0.0" };
    expect(canonicalEffectFrame([unknown], 100, 1, false).diagnostics).toMatchObject([{ code: "E_EFFECT_UNSUPPORTED" }]);
  });

  it("aplica fallback y diagnóstico si falta un input real", () => {
    const match = instance(catalog.effects.find((entry) => entry.id.includes("match-cut"))!, { inputs: undefined });
    const frame = canonicalEffectFrame([match], 100, 1, false);
    expect(frame.diagnostics[0]).toMatchObject({ code: "E_EFFECT_INPUT", fallbackId: "transition.cut.continuity.clean.v1.0.0" });
    expect(frame.outgoingAlpha).toBe(1);
  });

  it("respeta disable y fallback bajo movimiento reducido", () => {
    const shake = instance(catalog.effects.find((entry) => entry.id.includes("camera-shake"))!);
    const morph = instance(catalog.effects.find((entry) => entry.id.includes("morph-cut"))!);
    expect(canonicalEffectFrame([shake], 120, 42, true, { simulateInputs: true })).toMatchObject({ x: 0, y: 0, rotation: 0 });
    expect(canonicalEffectFrame([morph], 120, 42, true, { simulateInputs: true })).toMatchObject({ morph: 0, outgoingAlpha: 1, incomingAlpha: 0 });
  });

  it("el shake es determinista", () => {
    const effect = instance(catalog.effects.find((entry) => entry.id.includes("camera-shake"))!);
    expect(canonicalEffectFrame([effect], 250, 42, false)).toEqual(canonicalEffectFrame([effect], 250, 42, false));
  });
});

describe("efectos artesanales por capa", () => {
  const lineBoilEntry = catalog.effects.find((entry) => entry.id.includes("line-boil"))!;
  const wobbleEntry = catalog.effects.find((entry) => entry.id.includes("cutout-wobble"))!;
  const grainEntry = catalog.effects.find((entry) => entry.id.includes("paper-grain"))!;

  it("aísla fondo y personaje sin modificar el frame global", () => {
    const line = instance(lineBoilEntry, { target: "speaker" });
    const grain = instance(grainEntry, { target: "background" });
    const frame = canonicalEffectFrame([line, grain], 260, 42, false);
    expect(frame.layers.speaker.lineBoil).toBeDefined();
    expect(frame.layers.speaker.paperGrain).toBeUndefined();
    expect(frame.layers.background.paperGrain).toBeDefined();
    expect(frame.layers.background.lineBoil).toBeUndefined();
    expect(frame).toMatchObject({ x: 0, y: 0, rotation: 0, scale: 1 });
  });

  it("cuantiza line boil y grano con semilla estable", () => {
    const effects = [instance(lineBoilEntry, { target: "speaker" }), instance(grainEntry, { target: "background" })];
    const early = canonicalEffectFrame(effects, 20, 77, false).layers;
    const held = canonicalEffectFrame(effects, 80, 77, false).layers;
    const advanced = canonicalEffectFrame(effects, 220, 77, false).layers;
    expect(held).toEqual(early);
    expect(advanced.speaker.lineBoil?.step).not.toBe(early.speaker.lineBoil?.step);
    expect(advanced.background.paperGrain?.step).not.toBe(early.background.paperGrain?.step);
  });

  it("usa semillas distintas al animar fondo y personaje a la vez", () => {
    const both = canonicalEffectFrame([
      instance(lineBoilEntry, { role: "dominant", target: "background" }),
      instance(lineBoilEntry, { role: "support", target: "speaker" }),
    ], 220, 77, false);
    expect(both.layers.background.lineBoil?.seed).not.toBe(both.layers.speaker.lineBoil?.seed);
  });

  it("con movimiento reducido congela texturas y desactiva wobble", () => {
    const effects = [instance(lineBoilEntry), instance(wobbleEntry), instance(grainEntry)];
    const reduced = canonicalEffectFrame(effects, 760, 42, true);
    expect(reduced.layers.speaker.lineBoil).toMatchObject({ step: 0, amplitudePx: 0.5 });
    expect(reduced.layers.background.paperGrain).toMatchObject({ step: 0, amount: 0.06 });
    expect(reduced.layers.speaker).toMatchObject({ xPx: 0, yPx: 0, rotation: 0 });
  });
});

describe("contratos de transición", () => {
  const cutEntry = catalog.effects.find((entry) => entry.id.startsWith("transition.cut."))!;

  it("distingue corte, fade y disolución", () => {
    const atQuarter = (mode: string) => canonicalEffectFrame([instance(cutEntry, { params: { mode, durationMs: 1200 } })], 300, 1, false);
    expect(atQuarter("cut")).toMatchObject({ outgoingAlpha: 1, incomingAlpha: 0, blackout: 0 });
    expect(atQuarter("fade")).toMatchObject({ outgoingAlpha: 0.5, incomingAlpha: 0, blackout: 0.5 });
    expect(atQuarter("dissolve").incomingAlpha).toBeGreaterThan(0);
  });

  it("jump cut usa skipMs para saltar el tiempo fuente", () => {
    const entry = catalog.effects.find((effect) => effect.id.includes("jump-cut"))!;
    const frame = canonicalEffectFrame([instance(entry, { params: { skipMs: 800 } })], 700, 1, false);
    expect(frame.jumpPhase).toBe(2);
    expect(frame.sourceTimeMs).toBe(2300);
  });
});

describe("parámetros programables", () => {
  const cases = catalog.effects.flatMap((entry) => Object.entries(entry.parameters).map(([name, spec]) => [entry, name, spec] as const));

  it.each(cases)("%s · %s altera el estado renderizado", (entry, name, spec) => {
    const current = spec.default;
    const alternate = spec.type === "boolean"
      ? !current
      : spec.type === "enum"
        ? spec.values?.find((value) => value !== current) ?? current
        : spec.type === "color"
          ? current === "#ff00ff" ? "#00ffff" : "#ff00ff"
          : current !== spec.min ? spec.min! : spec.max!;
    const baseParams = Object.fromEntries(Object.entries(entry.parameters).map(([key, value]) => [key, value.default]));
    const changedParams = { ...baseParams, [name]: alternate };
    const baseDuration = name === "durationMs" ? Math.max(120, Number(current)) : 1200;
    const changedDuration = name === "durationMs" ? Math.max(120, Number(alternate)) : 1200;
    const base = instance(entry, { params: baseParams, durationMs: baseDuration });
    const changed = instance(entry, { params: changedParams, durationMs: changedDuration });
    const times = [40, 80, 180, 420, 760];
    const differs = times.some((elapsed) => JSON.stringify(observable(canonicalEffectFrame([base], elapsed, 42, false, { simulateInputs: true, audioLevel: 0.72 }))) !== JSON.stringify(observable(canonicalEffectFrame([changed], elapsed, 42, false, { simulateInputs: true, audioLevel: 0.72 }))));
    expect(differs).toBe(true);
  });
});
