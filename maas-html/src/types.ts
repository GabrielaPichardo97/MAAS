export type EffectCode = "ES" | "ZI" | "ZO" | "PA-I" | "PA-D" | "TI-A" | "TI-B" | "PP";

export interface EffectSpec {
  code: EffectCode;
  intensity: number;
  target?: string | null;
  tremor: boolean;
}

export type EffectRole = "dominant" | "support" | "finish";
export type EffectTarget = "frame" | "background" | "speaker";
export type EffectSupportLevel = "native" | "approximation" | "input-assisted" | "preprocessed";
export type EffectFamily = "transition" | "motion" | "time" | "compositing" | "graphics" | "stylize";

export const EFFECT_IDS = [
  "transition.cut.continuity.clean.v1.0.0",
  "transition.match-cut.continuity.visual-rhyme.v1.0.0",
  "transition.jump-cut.compression.fragmented.v1.0.0",
  "transition.morph-cut.continuity.interview-clean.v1.0.0",
  "transition.whip-pan.energy.directional.v1.0.0",
  "transition.glitch.disruption.digital.v1.0.0",
  "transition.split-screen.comparison.clean.v1.0.0",
  "motion.push-in.emphasis.subtle.v1.0.0",
  "motion.ken-burns.exposition.documentary.v1.0.0",
  "motion.virtual-dolly.reveal.parallax.v1.0.0",
  "motion.camera-3d.world-building.parallax.v1.0.0",
  "motion.rack-focus.attention.depth-shift.v1.0.0",
  "motion.stabilize.clarity.smooth.v1.0.0",
  "motion.camera-shake.impact.decay.v1.0.0",
  "motion.motion-blur.continuity.directional.v1.0.0",
  "motion.cutout-wobble.presence.puppet-idle.v1.0.0",
  "time.remap.rhythm.variable.v1.0.0",
  "time.speed-ramp.energy.snap.v1.0.0",
  "time.freeze-frame.emphasis.hold.v1.0.0",
  "time.reverse.stylization.circular.v1.0.0",
  "time.trails.energy.decay.v1.0.0",
  "time.flash-frame.impact.single.v1.0.0",
  "time.punch-edit.impact.snap.v1.0.0",
  "compositing.chroma-key.environment.clean.v1.0.0",
  "compositing.rotoscope.isolation.object-matte.v1.0.0",
  "compositing.blend.layering.clean.v1.0.0",
  "compositing.match-move.integration.planar-3d.v1.0.0",
  "graphics.kinetic-type.emphasis.sequenced.v1.0.0",
  "graphics.lower-third.identification.clean.v1.0.0",
  "stylize.color-grade.coherence.clean.v1.0.0",
  "stylize.light-leak.atmosphere.film.v1.0.0",
  "stylize.lens-flare.hero.optical.v1.0.0",
  "stylize.particles.atmosphere.dynamic.v1.0.0",
  "stylize.glitch.disruption.retro-tv.v1.0.0",
  "stylize.audio-reactive.rhythm.pulse.v1.0.0",
  "stylize.line-boil.handmade.edge-jitter.v1.0.0",
  "stylize.paper-grain.texture.living-fiber.v1.0.0",
] as const;

export type CanonicalEffectId = typeof EFFECT_IDS[number];

export interface EffectInputReference {
  kind: "media" | "data";
  assetId: string;
}

export interface EffectInstance {
  id: CanonicalEffectId | string;
  role: EffectRole;
  intensity: number;
  startOffsetMs: number;
  durationMs: number;
  target?: EffectTarget | null;
  params: Record<string, string | number | boolean>;
  inputs?: Record<string, EffectInputReference>;
}

export interface EffectParameterDefinition {
  type: "number" | "integer" | "boolean" | "enum" | "color";
  default: string | number | boolean;
  min?: number;
  max?: number;
  values?: string[];
}

export interface EffectCatalogEntry {
  id: string;
  displayName: string;
  family: EffectFamily;
  intent: string;
  variant: string;
  description: string;
  bestMoment: string;
  avoidWhen: string[];
  parameters: Record<string, EffectParameterDefinition>;
  supportLevel: EffectSupportLevel;
  requirements: string[];
  fallbackId?: string | null;
  renderCost: "low" | "medium" | "high";
  mobileSafe: boolean;
  reducedMotion: "preserve" | "reduce" | "disable" | "fallback";
  photosensitivityRisk: "none" | "low" | "medium" | "high";
  targets?: EffectTarget[];
  defaultTarget?: EffectTarget;
}

export interface EffectCatalog {
  schemaVersion: "1.0";
  catalogVersion: string;
  families: EffectFamily[];
  supportLevels: EffectSupportLevel[];
  effects: EffectCatalogEntry[];
}

export interface CueMedia {
  spriteAssetId: string;
  backgroundAssetId: string;
  mirrorX: boolean;
  layout: "landscape-character-left" | "landscape-character-right";
  fallbackApplied: { requested: string; resolved: string } | null;
}

export interface TimelineCue {
  id: string;
  type: "scene" | "dialogue" | "sfx" | "transition" | "advice" | "ending";
  startMs: number;
  durationMs: number;
  text?: string;
  speaker?: string;
  speakerAlias?: string;
  speakerLabel?: string;
  effect?: EffectSpec;
  effects?: EffectInstance[];
  backgroundUrl?: string;
  spriteUrl?: string;
  speakerPosition?: "izquierda" | "derecha";
  place?: string;
  cueIds?: string[];
  emotion?: string;
  sourceEmotion?: string;
  stageDirection?: string;
  media?: CueMedia;
}

export interface EpisodeManifest {
  schemaVersion: "1.0" | "2.0" | "2.1";
  episodeId: string;
  title: string;
  profile: "legacy-v1" | "canonical-v1" | "canonical-v2";
  durationMs: number;
  timeline: TimelineCue[];
  warnings: Array<Record<string, unknown>>;
  assets: string[];
  assetUrls: Record<string, string>;
}
