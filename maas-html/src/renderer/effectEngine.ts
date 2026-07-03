import { EFFECT_IDS, type CanonicalEffectId, type EffectInstance } from "../types";

export type LayerEffectTarget = "background" | "speaker";

export interface LayerEffectFrame {
  xPx: number;
  yPx: number;
  rotation: number;
  lineBoil?: { amplitudePx: number; wavelengthPx: number; step: number; seed: number };
  paperGrain?: { amount: number; grainPx: number; fiber: number; step: number; seed: number };
}

export interface EffectDiagnostic {
  code: "E_EFFECT_INPUT" | "E_EFFECT_UNSUPPORTED";
  effectId: string;
  message: string;
  fallbackId?: CanonicalEffectId;
}

export interface CanonicalEffectFrame {
  scale: number;
  x: number;
  y: number;
  rotation: number;
  alpha: number;
  blur: number;
  noise: number;
  tint: number;
  incomingAlpha: number;
  outgoingAlpha: number;
  blackout: number;
  sourceTimeMs: number;
  secondaryX: number;
  secondaryY: number;
  secondaryScale: number;
  parallaxDepth: number;
  splitPanes: number;
  splitGapPct: number;
  morph: number;
  jumpPhase: number;
  freeze: boolean;
  flash?: { color: number; alpha: number };
  leak?: { color: number; alpha: number; x: number };
  flare?: { alpha: number; x: number; y: number };
  particles?: { count: number; progress: number; gravity: number; lifeMs: number };
  trails?: { count: number; decay: number };
  directionalBlur?: { strength: number; angleDeg: number };
  chroma?: { keyColor: number; tolerance: number; spill: number };
  matte?: { featherPx: number; expansionPx: number };
  blend?: { mode: string; opacity: number };
  tracking?: { x: number; y: number; rotation: number };
  kineticType?: { progress: number; staggerMs: number; unit: string };
  lowerThird?: { progress: number; safeMarginPct: number };
  colorGrade?: { contrast: number; saturation: number; tint: number };
  audioLevel?: number;
  layers: Record<LayerEffectTarget, LayerEffectFrame>;
  diagnostics: EffectDiagnostic[];
  activeEffectIds: string[];
}

export interface EffectRuntimeContext {
  simulateInputs?: boolean;
  audioLevel?: number;
}

interface HandlerContext {
  effect: EffectInstance;
  frame: CanonicalEffectFrame;
  progress: number;
  eased: number;
  intensity: number;
  elapsedMs: number;
  runtime: EffectRuntimeContext;
  seed: number;
  reducedMotion: boolean;
}

type EffectHandler = (context: HandlerContext) => void;

const identity = (elapsedMs: number): CanonicalEffectFrame => ({
  scale: 1,
  x: 0,
  y: 0,
  rotation: 0,
  alpha: 1,
  blur: 0,
  noise: 0,
  tint: 0xffffff,
  incomingAlpha: 1,
  outgoingAlpha: 0,
  blackout: 0,
  sourceTimeMs: elapsedMs,
  secondaryX: 0,
  secondaryY: 0,
  secondaryScale: 1,
  parallaxDepth: 0,
  splitPanes: 1,
  splitGapPct: 0,
  morph: 0,
  jumpPhase: 0,
  freeze: false,
  layers: {
    background: { xPx: 0, yPx: 0, rotation: 0 },
    speaker: { xPx: 0, yPx: 0, rotation: 0 },
  },
  diagnostics: [],
  activeEffectIds: [],
});

const clamp = (value: number, min = 0, max = 1) => Math.max(min, Math.min(max, value));
const ease = (value: number) => value * value * (3 - 2 * value);
const numberParam = (effect: EffectInstance, key: string, fallback: number) => typeof effect.params[key] === "number" ? effect.params[key] as number : fallback;
const stringParam = (effect: EffectInstance, key: string, fallback: string) => typeof effect.params[key] === "string" ? effect.params[key] as string : fallback;
const boolParam = (effect: EffectInstance, key: string, fallback: boolean) => typeof effect.params[key] === "boolean" ? effect.params[key] as boolean : fallback;
const colorParam = (effect: EffectInstance, key: string, fallback: number) => {
  const value = effect.params[key];
  return typeof value === "string" && /^#[0-9a-f]{6}$/i.test(value) ? Number.parseInt(value.slice(1), 16) : fallback;
};

function pseudo(seed: number): number {
  const value = Math.sin(seed * 12.9898) * 43758.5453;
  return value - Math.floor(value);
}

function targetFor(context: HandlerContext, defaultTarget: LayerEffectTarget): LayerEffectTarget {
  return context.effect.target === "background" || context.effect.target === "speaker" ? context.effect.target : defaultTarget;
}

function layerFor(context: HandlerContext, defaultTarget: LayerEffectTarget): LayerEffectFrame {
  return context.frame.layers[targetFor(context, defaultTarget)];
}

function quantizedStep(elapsedMs: number, rateFps: number, reducedMotion: boolean): number {
  return reducedMotion ? 0 : Math.floor(elapsedMs / Math.max(1, 1000 / rateFps));
}

function hasInput(context: HandlerContext, name: string): boolean {
  return context.runtime.simulateInputs === true || Boolean(context.effect.inputs?.[name]?.assetId);
}

function missingInput(context: HandlerContext, name: string, fallbackId?: CanonicalEffectId): boolean {
  if (hasInput(context, name)) return false;
  context.frame.diagnostics.push({
    code: "E_EFFECT_INPUT",
    effectId: context.effect.id,
    message: `Falta el input ${name}`,
    fallbackId,
  });
  return true;
}

function cleanCut({ frame, progress }: HandlerContext): void {
  frame.outgoingAlpha = progress < 0.5 ? 1 : 0;
  frame.incomingAlpha = progress < 0.5 ? 0 : 1;
}

const handlers: Record<CanonicalEffectId, EffectHandler> = {
  "transition.cut.continuity.clean.v1.0.0": (context) => {
    const mode = stringParam(context.effect, "mode", "cut");
    if (mode === "dissolve") {
      context.frame.outgoingAlpha = 1 - context.eased;
      context.frame.incomingAlpha = context.eased;
      return;
    }
    if (mode === "fade") {
      context.frame.outgoingAlpha = 1 - clamp(context.progress * 2);
      context.frame.incomingAlpha = clamp((context.progress - 0.5) * 2);
      context.frame.blackout = 1 - Math.max(context.frame.outgoingAlpha, context.frame.incomingAlpha);
      return;
    }
    cleanCut(context);
  },
  "transition.match-cut.continuity.visual-rhyme.v1.0.0": (context) => {
    if (missingInput(context, "matchAnchors", "transition.cut.continuity.clean.v1.0.0")) return cleanCut(context);
    const tolerance = numberParam(context.effect, "tolerance", 0.8);
    const matchType = stringParam(context.effect, "matchType", "shape");
    context.frame.outgoingAlpha = context.progress < 0.5 ? 1 : 0;
    context.frame.incomingAlpha = context.progress < 0.5 ? 0 : 1;
    context.frame.secondaryX = (1 - context.eased) * (1 - tolerance) * 0.35;
    context.frame.secondaryY = matchType === "motion" ? (1 - context.eased) * 0.12 : 0;
    context.frame.rotation += matchType === "graphic" ? (1 - context.eased) * 0.08 : 0;
    context.frame.secondaryScale = 1 + (1 - context.eased) * (1 - tolerance) * 0.18;
    context.frame.morph = context.eased;
  },
  "transition.jump-cut.compression.fragmented.v1.0.0": (context) => {
    const skipMs = numberParam(context.effect, "skipMs", 400);
    const phase = Math.min(3, Math.floor(context.progress * 4));
    context.frame.jumpPhase = phase;
    context.frame.sourceTimeMs = context.elapsedMs + phase * skipMs;
    context.frame.x += phase * 0.035 * context.intensity;
    context.frame.scale *= 1 + phase * 0.025 * context.intensity;
    context.frame.rotation += (phase % 2 === 0 ? -1 : 1) * 0.008 * context.intensity;
  },
  "transition.morph-cut.continuity.interview-clean.v1.0.0": (context) => {
    if (missingInput(context, "morphClip", "transition.cut.continuity.clean.v1.0.0")) return cleanCut(context);
    context.frame.outgoingAlpha = 1 - context.eased;
    context.frame.incomingAlpha = context.eased;
    context.frame.morph = Math.sin(Math.PI * context.progress) * context.intensity;
    context.frame.blur = Math.max(context.frame.blur, context.frame.morph * 6);
    context.frame.secondaryScale = 0.96 + context.eased * 0.04;
  },
  "transition.whip-pan.energy.directional.v1.0.0": (context) => {
    const direction = stringParam(context.effect, "direction", "right");
    const horizontal = direction === "left" || direction === "right";
    const sign = direction === "left" || direction === "up" ? -1 : 1;
    const travel = Math.sin(Math.PI * context.progress) * sign * 0.8 * context.intensity;
    if (horizontal) context.frame.x += travel;
    else context.frame.y += travel;
    context.frame.outgoingAlpha = 1 - context.eased;
    context.frame.incomingAlpha = context.eased;
    context.frame.directionalBlur = { strength: numberParam(context.effect, "blurPx", 80) * Math.sin(Math.PI * context.progress) * context.intensity, angleDeg: horizontal ? 0 : 90 };
    context.frame.blur = Math.max(context.frame.blur, context.frame.directionalBlur.strength * 0.35);
  },
  "transition.glitch.disruption.digital.v1.0.0": (context) => {
    const peak = Math.sin(Math.PI * context.progress);
    context.frame.outgoingAlpha = context.progress < 0.5 ? 1 : 0;
    context.frame.incomingAlpha = context.progress < 0.5 ? 0 : 1;
    context.frame.noise = Math.max(context.frame.noise, numberParam(context.effect, "noise", 0.25) * peak * context.intensity);
    context.frame.secondaryX = numberParam(context.effect, "rgbOffsetPx", 6) / 500 * peak * context.intensity;
    context.frame.x += (pseudo(Math.floor(context.elapsedMs / 40)) * 2 - 1) * 0.035 * peak * context.intensity;
  },
  "transition.split-screen.comparison.clean.v1.0.0": ({ effect, frame, eased }) => {
    frame.splitPanes = Math.round(numberParam(effect, "panes", 2));
    frame.splitGapPct = numberParam(effect, "gapPct", 2);
    frame.outgoingAlpha = 1;
    frame.incomingAlpha = eased;
  },
  "motion.push-in.emphasis.subtle.v1.0.0": ({ effect, frame, eased, intensity }) => {
    const easing = stringParam(effect, "easing", "ease-in-out");
    const progress = easing === "linear" ? Math.sqrt(eased) : easing === "ease-in" ? eased * eased : easing === "ease-out" ? 1 - (1 - eased) ** 2 : eased;
    frame.scale *= 1 + (numberParam(effect, "scaleEnd", 1.1) - 1) * progress * intensity;
  },
  "motion.ken-burns.exposition.documentary.v1.0.0": ({ effect, frame, eased, intensity }) => {
    frame.scale *= 1 + (numberParam(effect, "scaleEnd", 1.12) - 1) * eased * intensity;
    frame.x += numberParam(effect, "endX", 0.1) * eased * intensity;
    frame.y += numberParam(effect, "endY", 0) * eased * intensity;
  },
  "motion.virtual-dolly.reveal.parallax.v1.0.0": ({ effect, frame, eased, intensity }) => {
    const travel = numberParam(effect, "travel", 0.25);
    frame.scale *= 1 + travel * eased * intensity;
    frame.y -= travel * 0.08 * eased * intensity;
    frame.parallaxDepth = numberParam(effect, "depth", 0.35) * eased * intensity;
    frame.secondaryX = -frame.parallaxDepth * 0.12;
  },
  "motion.camera-3d.world-building.parallax.v1.0.0": ({ effect, frame, eased, intensity }) => {
    frame.parallaxDepth = numberParam(effect, "depth", 0.5) * Math.sin(Math.PI * eased) * intensity;
    frame.secondaryX = frame.parallaxDepth * 0.18;
    frame.secondaryY = -frame.parallaxDepth * 0.08;
    frame.rotation += numberParam(effect, "rollDeg", 0) * Math.PI / 180 * eased * intensity;
    frame.scale *= 1 + frame.parallaxDepth * 0.08;
  },
  "motion.rack-focus.attention.depth-shift.v1.0.0": ({ effect, frame, progress, intensity }) => {
    frame.blur = Math.max(frame.blur, numberParam(effect, "blurPx", 18) * Math.sin(Math.PI * progress) * intensity);
    const target = stringParam(effect, "focusTo", "subject");
    const depthShift = target === "background" ? -0.04 : target === "foreground" ? 0.02 : 0.04;
    frame.secondaryScale = 1 + Math.sin(Math.PI * progress) * depthShift * intensity;
  },
  "motion.stabilize.clarity.smooth.v1.0.0": (context) => {
    if (missingInput(context, "stabilizationTrack")) return;
    const strength = numberParam(context.effect, "strength", 0.5) * context.intensity;
    const step = Math.floor(context.elapsedMs / 70);
    context.frame.x -= (pseudo(step + 19) * 2 - 1) * 0.035 * strength;
    context.frame.y -= (pseudo(step + 71) * 2 - 1) * 0.025 * strength;
    context.frame.rotation -= (pseudo(step + 9) * 2 - 1) * 0.012 * strength;
  },
  "motion.camera-shake.impact.decay.v1.0.0": ({ effect, frame, elapsedMs, intensity }) => {
    const decay = 1 - clamp(elapsedMs / numberParam(effect, "decayMs", 500));
    const amplitude = numberParam(effect, "amplitudePx", 8) / 1080 * intensity * decay;
    const step = Math.floor(elapsedMs / Math.max(1, 1000 / numberParam(effect, "frequencyHz", 8)));
    frame.x += (pseudo(step + 11) * 2 - 1) * amplitude;
    frame.y += (pseudo(step + 91) * 2 - 1) * amplitude;
    frame.rotation += (pseudo(step + 17) * 2 - 1) * amplitude * 0.3;
  },
  "motion.motion-blur.continuity.directional.v1.0.0": ({ effect, frame, progress, intensity }) => {
    const strength = numberParam(effect, "blurPx", 24) * Math.sin(Math.PI * progress) * intensity;
    frame.directionalBlur = { strength, angleDeg: numberParam(effect, "angleDeg", 0) };
    frame.blur = Math.max(frame.blur, strength * 0.45);
    frame.x += Math.cos(frame.directionalBlur.angleDeg * Math.PI / 180) * Math.sin(Math.PI * progress) * 0.04 * intensity;
    frame.y += Math.sin(frame.directionalBlur.angleDeg * Math.PI / 180) * Math.sin(Math.PI * progress) * 0.04 * intensity;
  },
  "motion.cutout-wobble.presence.puppet-idle.v1.0.0": (context) => {
    const layer = layerFor(context, "speaker");
    const rateFps = numberParam(context.effect, "rateFps", 6);
    const frameMs = 1000 / rateFps;
    const step = Math.floor(context.elapsedMs / frameMs);
    const settle = ease(clamp((context.elapsedMs % frameMs) / (frameMs * 0.22)));
    const travel = numberParam(context.effect, "travelPx", 4) * context.intensity;
    const rotation = numberParam(context.effect, "rotationDeg", 0.45) * Math.PI / 180 * context.intensity;
    const pose = (index: number, offset: number) => pseudo(context.seed * 0.071 + index * 13.17 + offset) * 2 - 1;
    layer.xPx += (pose(step - 1, 11) * (1 - settle) + pose(step, 11) * settle) * travel;
    layer.yPx += (pose(step - 1, 29) * (1 - settle) + pose(step, 29) * settle) * travel * 0.55;
    layer.rotation += (pose(step - 1, 47) * (1 - settle) + pose(step, 47) * settle) * rotation;
  },
  "time.remap.rhythm.variable.v1.0.0": ({ effect, frame, elapsedMs, intensity }) => {
    const speed = numberParam(effect, "speed", 1);
    frame.sourceTimeMs = elapsedMs * speed;
    frame.x += Math.sin(frame.sourceTimeMs / 180) * 0.025 * intensity;
    if (!boolParam(effect, "preservePitch", true)) frame.secondaryScale = 0.96;
  },
  "time.speed-ramp.energy.snap.v1.0.0": ({ effect, frame, elapsedMs, progress, intensity }) => {
    const ramp = clamp(numberParam(effect, "rampMs", 320) / Math.max(1, effect.durationMs));
    const envelope = ramp === 0 ? 1 : clamp(Math.sin(Math.PI * progress) / ramp);
    const speed = 1 + (numberParam(effect, "peakSpeed", 4) - 1) * envelope;
    frame.sourceTimeMs = elapsedMs * speed;
    frame.x += Math.sin(frame.sourceTimeMs / 110) * 0.035 * intensity;
    frame.blur = Math.max(frame.blur, envelope * 8 * intensity);
  },
  "time.freeze-frame.emphasis.hold.v1.0.0": ({ effect, frame, elapsedMs }) => {
    const holdMs = numberParam(effect, "holdMs", 800);
    const holdStart = Math.max(0, (effect.durationMs - holdMs) / 2);
    frame.sourceTimeMs = elapsedMs < holdStart ? elapsedMs : elapsedMs < holdStart + holdMs ? holdStart : elapsedMs - holdMs;
    frame.freeze = elapsedMs >= holdStart && elapsedMs < holdStart + holdMs;
    frame.x += Math.sin(frame.sourceTimeMs / 180) * 0.022;
    frame.y += Math.cos(frame.sourceTimeMs / 240) * 0.009;
  },
  "time.reverse.stylization.circular.v1.0.0": ({ effect, frame, elapsedMs, intensity }) => {
    frame.sourceTimeMs = Math.max(0, effect.durationMs - elapsedMs * numberParam(effect, "speed", 1));
    frame.x += Math.sin(frame.sourceTimeMs / 170) * 0.025 * intensity;
    frame.rotation -= Math.sin(frame.sourceTimeMs / 300) * 0.012 * intensity;
  },
  "time.trails.energy.decay.v1.0.0": ({ effect, frame }) => {
    frame.trails = { count: Math.round(numberParam(effect, "frames", 4)), decay: numberParam(effect, "decay", 0.65) };
    frame.alpha = 0.9;
    frame.x += Math.sin(frame.sourceTimeMs / 130) * 0.035;
  },
  "time.flash-frame.impact.single.v1.0.0": ({ effect, frame, elapsedMs, intensity }) => {
    if (elapsedMs <= numberParam(effect, "durationMs", 40)) frame.flash = { color: colorParam(effect, "color", 0xffffff), alpha: numberParam(effect, "opacity", 0.8) * intensity };
  },
  "time.punch-edit.impact.snap.v1.0.0": ({ effect, frame, progress, intensity }) => {
    const peak = Math.sin(Math.PI * progress);
    frame.scale *= 1 + peak * 0.14 * intensity;
    frame.blur = Math.max(frame.blur, numberParam(effect, "blurBoost", 0.35) * 30 * peak * intensity);
    frame.sourceTimeMs *= 1 + (numberParam(effect, "peakSpeed", 4) - 1) * peak;
  },
  "compositing.chroma-key.environment.clean.v1.0.0": (context) => {
    if (missingInput(context, "keyedSource")) return;
    context.frame.chroma = { keyColor: colorParam(context.effect, "keyColor", 0x00ff00), tolerance: numberParam(context.effect, "tolerance", 0.25), spill: numberParam(context.effect, "spill", 0.5) };
  },
  "compositing.rotoscope.isolation.object-matte.v1.0.0": (context) => {
    if (missingInput(context, "objectMatte")) return;
    context.frame.matte = { featherPx: numberParam(context.effect, "featherPx", 3), expansionPx: numberParam(context.effect, "expansionPx", 0) };
  },
  "compositing.blend.layering.clean.v1.0.0": ({ effect, frame }) => {
    frame.blend = { mode: stringParam(effect, "blendMode", "normal"), opacity: numberParam(effect, "opacity", 1) };
    frame.outgoingAlpha = frame.blend.opacity;
  },
  "compositing.match-move.integration.planar-3d.v1.0.0": (context) => {
    if (missingInput(context, "trackingData", "graphics.lower-third.identification.clean.v1.0.0")) {
      context.frame.lowerThird = { progress: context.eased, safeMarginPct: 8 };
      return;
    }
    const trackType = stringParam(context.effect, "trackType", "planar");
    const factor = trackType === "camera" ? 1.45 : trackType === "object" ? 0.75 : 1;
    context.frame.tracking = { x: 0.12 * factor * Math.sin(context.progress * Math.PI * 2), y: -0.08 * factor * Math.cos(context.progress * Math.PI * 2), rotation: Math.sin(context.progress * Math.PI) * 0.08 * factor };
  },
  "graphics.kinetic-type.emphasis.sequenced.v1.0.0": ({ effect, frame, eased }) => {
    frame.kineticType = { progress: eased, staggerMs: numberParam(effect, "staggerMs", 80), unit: stringParam(effect, "unit", "word") };
  },
  "graphics.lower-third.identification.clean.v1.0.0": ({ effect, frame, elapsedMs }) => {
    frame.lowerThird = { progress: ease(clamp(elapsedMs / numberParam(effect, "enterMs", 320))), safeMarginPct: numberParam(effect, "safeMarginPct", 8) };
  },
  "stylize.color-grade.coherence.clean.v1.0.0": ({ effect, frame }) => {
    const saturation = numberParam(effect, "saturation", 1);
    const tint = numberParam(effect, "tint", 0);
    frame.colorGrade = { contrast: numberParam(effect, "contrast", 0), saturation, tint };
    frame.tint = tint < -0.05 ? 0xbcd7ff : tint > 0.05 ? 0xffc9bb : saturation < 0.9 ? 0xd8e1ea : saturation > 1.1 ? 0xffe3cf : 0xffffff;
  },
  "stylize.light-leak.atmosphere.film.v1.0.0": ({ effect, frame, progress, intensity }) => {
    frame.leak = { color: colorParam(effect, "color", 0xff8a4c), alpha: numberParam(effect, "intensity", 0.25) * intensity * Math.sin(Math.PI * progress), x: progress };
  },
  "stylize.lens-flare.hero.optical.v1.0.0": ({ effect, frame, progress, intensity }) => {
    frame.flare = { alpha: numberParam(effect, "intensity", 0.2) * intensity * (0.55 + Math.sin(Math.PI * progress) * 0.45), x: numberParam(effect, "x", 0.75), y: numberParam(effect, "y", 0.25) };
  },
  "stylize.particles.atmosphere.dynamic.v1.0.0": ({ effect, frame, progress, intensity }) => {
    frame.particles = { count: Math.min(80, Math.round(numberParam(effect, "rate", 40) * intensity)), progress, gravity: numberParam(effect, "gravity", 0.2), lifeMs: numberParam(effect, "lifeMs", 1800) };
  },
  "stylize.glitch.disruption.retro-tv.v1.0.0": ({ effect, frame, elapsedMs, progress, intensity }) => {
    const peak = 0.45 + Math.sin(progress * Math.PI * 4) * 0.45;
    frame.noise = Math.max(frame.noise, (numberParam(effect, "corruption", 0.25) * peak + numberParam(effect, "scanlines", 0.35) * 0.12) * intensity);
    frame.secondaryX = numberParam(effect, "rgbOffsetPx", 4) / 500 * intensity;
    frame.x += (pseudo(Math.floor(elapsedMs / 40)) * 2 - 1) * 0.018 * intensity;
  },
  "stylize.audio-reactive.rhythm.pulse.v1.0.0": (context) => {
    if (missingInput(context, "audioEnvelope")) return;
    const band = stringParam(context.effect, "band", "full");
    const bandRate = band === "bass" ? 150 : band === "mid" ? 95 : band === "treble" ? 52 : 110;
    const bandFactor = band === "bass" ? 1 : band === "mid" ? 0.82 : band === "treble" ? 0.66 : 0.92;
    const raw = (context.runtime.audioLevel ?? (0.5 + Math.sin(context.elapsedMs / bandRate) * 0.5)) * bandFactor;
    const smoothing = numberParam(context.effect, "smoothing", 0.75);
    const level = clamp(raw * numberParam(context.effect, "sensitivity", 0.8) * (1 - smoothing * 0.35));
    context.frame.audioLevel = level;
    context.frame.scale *= 1 + level * 0.09 * context.intensity;
    context.frame.alpha = 0.82 + level * 0.18;
  },
  "stylize.line-boil.handmade.edge-jitter.v1.0.0": (context) => {
    const target = targetFor(context, "speaker");
    const layer = context.frame.layers[target];
    const amplitude = numberParam(context.effect, "amplitudePx", 1.25) * context.intensity * (context.reducedMotion ? 0.4 : 1);
    const next = {
      amplitudePx: amplitude,
      wavelengthPx: numberParam(context.effect, "wavelengthPx", 36),
      step: quantizedStep(context.elapsedMs, numberParam(context.effect, "rateFps", 8), context.reducedMotion),
      seed: context.seed + (target === "background" ? 17 : 43),
    };
    if (layer.lineBoil) next.amplitudePx = Math.min(4, layer.lineBoil.amplitudePx + next.amplitudePx);
    layer.lineBoil = next;
  },
  "stylize.paper-grain.texture.living-fiber.v1.0.0": (context) => {
    const target = targetFor(context, "background");
    const layer = context.frame.layers[target];
    const next = {
      amount: numberParam(context.effect, "amount", 0.06) * context.intensity,
      grainPx: numberParam(context.effect, "grainPx", 3),
      fiber: numberParam(context.effect, "fiber", 0.35),
      step: quantizedStep(context.elapsedMs, numberParam(context.effect, "rateFps", 6), context.reducedMotion),
      seed: context.seed + (target === "background" ? 101 : 151),
    };
    if (layer.paperGrain) next.amount = Math.min(0.25, layer.paperGrain.amount + next.amount);
    layer.paperGrain = next;
  },
};

const disabledForReducedMotion = new Set<CanonicalEffectId>([
  "motion.camera-shake.impact.decay.v1.0.0",
  "motion.motion-blur.continuity.directional.v1.0.0",
  "time.trails.energy.decay.v1.0.0",
  "time.flash-frame.impact.single.v1.0.0",
  "stylize.particles.atmosphere.dynamic.v1.0.0",
  "stylize.glitch.disruption.retro-tv.v1.0.0",
  "stylize.audio-reactive.rhythm.pulse.v1.0.0",
  "motion.cutout-wobble.presence.puppet-idle.v1.0.0",
]);

const fallbackForReducedMotion: Partial<Record<CanonicalEffectId, CanonicalEffectId>> = {
  "transition.match-cut.continuity.visual-rhyme.v1.0.0": "transition.cut.continuity.clean.v1.0.0",
  "transition.morph-cut.continuity.interview-clean.v1.0.0": "transition.cut.continuity.clean.v1.0.0",
  "transition.whip-pan.energy.directional.v1.0.0": "transition.cut.continuity.clean.v1.0.0",
  "transition.glitch.disruption.digital.v1.0.0": "transition.cut.continuity.clean.v1.0.0",
  "motion.virtual-dolly.reveal.parallax.v1.0.0": "motion.push-in.emphasis.subtle.v1.0.0",
  "motion.camera-3d.world-building.parallax.v1.0.0": "motion.virtual-dolly.reveal.parallax.v1.0.0",
  "motion.rack-focus.attention.depth-shift.v1.0.0": "motion.push-in.emphasis.subtle.v1.0.0",
  "time.speed-ramp.energy.snap.v1.0.0": "time.remap.rhythm.variable.v1.0.0",
  "time.punch-edit.impact.snap.v1.0.0": "time.speed-ramp.energy.snap.v1.0.0",
  "compositing.match-move.integration.planar-3d.v1.0.0": "graphics.lower-third.identification.clean.v1.0.0",
  "graphics.kinetic-type.emphasis.sequenced.v1.0.0": "graphics.lower-third.identification.clean.v1.0.0",
};

const effectIdSet = new Set<string>(EFFECT_IDS);
export const REGISTERED_EFFECT_IDS = Object.freeze(Object.keys(handlers) as CanonicalEffectId[]);

export function isCanonicalEffectId(value: string): value is CanonicalEffectId {
  return effectIdSet.has(value);
}

export function effectProgress(effect: EffectInstance, elapsedMs: number): number | null {
  const local = elapsedMs - effect.startOffsetMs;
  if (local < 0 || local > effect.durationMs) return null;
  return effect.durationMs === 0 ? 1 : clamp(local / effect.durationMs);
}

export function canonicalEffectFrame(effects: EffectInstance[], elapsedMs: number, seed: number, reducedMotion: boolean, runtime: EffectRuntimeContext = {}): CanonicalEffectFrame {
  const frame = identity(elapsedMs);
  for (const effect of effects) {
    const progress = effectProgress(effect, elapsedMs);
    if (progress === null) continue;
    if (!isCanonicalEffectId(effect.id)) {
      frame.diagnostics.push({ code: "E_EFFECT_UNSUPPORTED", effectId: effect.id, message: "El efecto no tiene renderer registrado" });
      continue;
    }
    frame.activeEffectIds.push(effect.id);
    if (reducedMotion && disabledForReducedMotion.has(effect.id)) continue;
    const preservesReducedIntensity = effect.id === "stylize.line-boil.handmade.edge-jitter.v1.0.0" || effect.id === "stylize.paper-grain.texture.living-fiber.v1.0.0";
    const intensity = effect.intensity * (reducedMotion && !preservesReducedIntensity ? 0.2 : 1);
    const context = { effect, frame, progress, eased: ease(progress), intensity, elapsedMs: elapsedMs - effect.startOffsetMs, runtime, seed, reducedMotion };
    const fallbackId = reducedMotion ? fallbackForReducedMotion[effect.id] : undefined;
    if (fallbackId) handlers[fallbackId](context);
    else handlers[effect.id](context);
  }
  return frame;
}
