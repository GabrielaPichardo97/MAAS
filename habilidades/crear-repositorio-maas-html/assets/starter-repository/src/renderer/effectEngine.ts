import type { EffectInstance } from "../types";

export interface CanonicalEffectFrame {
  scale: number;
  x: number;
  y: number;
  rotation: number;
  alpha: number;
  blur: number;
  noise: number;
  tint: number;
  flash?: { color: number; alpha: number };
  leak?: { color: number; alpha: number; x: number };
  flare?: { alpha: number; x: number; y: number };
  particles?: { count: number; progress: number };
}

const identity = (): CanonicalEffectFrame => ({ scale: 1, x: 0, y: 0, rotation: 0, alpha: 1, blur: 0, noise: 0, tint: 0xffffff });
const clamp = (value: number, min = 0, max = 1) => Math.max(min, Math.min(max, value));
const ease = (value: number) => value * value * (3 - 2 * value);
const numberParam = (effect: EffectInstance, key: string, fallback: number) => typeof effect.params[key] === "number" ? effect.params[key] as number : fallback;
const colorParam = (effect: EffectInstance, key: string, fallback: number) => {
  const value = effect.params[key];
  return typeof value === "string" && /^#[0-9a-f]{6}$/i.test(value) ? Number.parseInt(value.slice(1), 16) : fallback;
};

export function effectProgress(effect: EffectInstance, elapsedMs: number): number | null {
  const local = elapsedMs - effect.startOffsetMs;
  if (local < 0 || local > effect.durationMs) return null;
  return effect.durationMs === 0 ? 1 : clamp(local / effect.durationMs);
}

function pseudo(seed: number): number {
  const x = Math.sin(seed * 12.9898) * 43758.5453;
  return x - Math.floor(x);
}

export function canonicalEffectFrame(effects: EffectInstance[], elapsedMs: number, seed: number, reducedMotion: boolean): CanonicalEffectFrame {
  const frame = identity();
  for (const effect of effects) {
    const progress = effectProgress(effect, elapsedMs);
    if (progress === null) continue;
    const id = effect.id;
    const vestibular = id.includes("camera-shake") || id.includes("speed-ramp") || id.includes("trails") || id.includes("particles") || id.includes("glitch");
    if (reducedMotion && vestibular) continue;
    const intensity = effect.intensity * (reducedMotion ? 0.2 : 1);
    const t = ease(progress);
    if (id.includes("push-in")) frame.scale *= 1 + (numberParam(effect, "scaleEnd", 1.1) - 1) * t * intensity;
    if (id.includes("ken-burns")) {
      frame.scale *= 1 + (numberParam(effect, "scaleEnd", 1.12) - 1) * t * intensity;
      frame.x += numberParam(effect, "endX", 0.1) * t * intensity;
      frame.y += numberParam(effect, "endY", 0) * t * intensity;
    }
    if (id.includes("virtual-dolly") || id.includes("camera-3d")) {
      const travel = numberParam(effect, "travel", 0.25);
      frame.scale *= 1 + travel * t * intensity;
      frame.y -= travel * 0.04 * t * intensity;
      frame.rotation += numberParam(effect, "rollDeg", 0) * Math.PI / 180 * t * intensity;
    }
    if (id.includes("rack-focus")) frame.blur = Math.max(frame.blur, numberParam(effect, "blurPx", 18) * Math.sin(Math.PI * progress) * intensity);
    if (id.includes("camera-shake")) {
      const amplitude = numberParam(effect, "amplitudePx", 8) / 1080 * intensity * (1 - progress);
      const step = Math.floor(elapsedMs / Math.max(1, 1000 / numberParam(effect, "frequencyHz", 8)));
      frame.x += (pseudo(seed + step) * 2 - 1) * amplitude;
      frame.y += (pseudo(seed + step + 91) * 2 - 1) * amplitude;
      frame.rotation += (pseudo(seed + step + 17) * 2 - 1) * amplitude * 0.15;
    }
    if (id.includes("motion-blur") || id.includes("whip-pan")) frame.blur = Math.max(frame.blur, numberParam(effect, "blurPx", 24) * Math.sin(Math.PI * progress) * intensity);
    if (id.includes("whip-pan")) frame.x += Math.sin(Math.PI * (progress - 0.5)) * 0.35 * intensity;
    if (id.includes("jump-cut")) frame.x += Math.floor(progress * 4) * 0.012 * intensity;
    if (id.includes("trails")) frame.alpha = 0.82;
    if (id.includes("flash-frame") && elapsedMs - effect.startOffsetMs <= numberParam(effect, "durationMs", 40)) frame.flash = { color: colorParam(effect, "color", 0xffffff), alpha: numberParam(effect, "opacity", 0.8) * intensity };
    if (id.includes("glitch")) {
      frame.noise = Math.max(frame.noise, numberParam(effect, "noise", numberParam(effect, "corruption", 0.25)) * intensity);
      frame.x += (pseudo(seed + Math.floor(elapsedMs / 40)) * 2 - 1) * 0.012 * intensity;
    }
    if (id.includes("color-grade")) frame.tint = numberParam(effect, "saturation", 1) < 0.9 ? 0xd8e1ea : numberParam(effect, "saturation", 1) > 1.1 ? 0xffe3cf : 0xffffff;
    if (id.includes("light-leak")) frame.leak = { color: colorParam(effect, "color", 0xff8a4c), alpha: numberParam(effect, "intensity", 0.25) * intensity * Math.sin(Math.PI * progress), x: progress };
    if (id.includes("lens-flare")) frame.flare = { alpha: numberParam(effect, "intensity", 0.2) * intensity, x: numberParam(effect, "x", 0.75), y: numberParam(effect, "y", 0.25) };
    if (id.includes("particles")) frame.particles = { count: Math.min(80, Math.round(numberParam(effect, "rate", 40) * intensity)), progress };
    if (id.includes("audio-reactive")) frame.scale *= 1 + Math.sin(elapsedMs / 95) * 0.025 * intensity;
    if (id.includes("punch-edit")) frame.scale *= 1 + Math.sin(Math.PI * progress) * 0.12 * intensity;
  }
  return frame;
}
