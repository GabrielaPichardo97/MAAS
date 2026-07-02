export type EffectCode = "ES" | "ZI" | "ZO" | "PA-I" | "PA-D" | "TI-A" | "TI-B" | "PP";

export interface EffectSpec {
  code: EffectCode;
  intensity: number;
  target?: string | null;
  tremor: boolean;
}

export type EffectRole = "dominant" | "support" | "finish";
export type EffectSupportLevel = "native" | "approximation" | "input-assisted" | "preprocessed";
export type EffectFamily = "transition" | "motion" | "time" | "compositing" | "graphics" | "stylize";

export interface EffectInstance {
  id: string;
  role: EffectRole;
  intensity: number;
  startOffsetMs: number;
  durationMs: number;
  target?: string | null;
  params: Record<string, string | number | boolean>;
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
  schemaVersion: "1.0" | "2.0";
  episodeId: string;
  title: string;
  profile: "legacy-v1" | "canonical-v1" | "canonical-v2";
  durationMs: number;
  timeline: TimelineCue[];
  warnings: Array<Record<string, unknown>>;
  assets: string[];
  assetUrls: Record<string, string>;
}
