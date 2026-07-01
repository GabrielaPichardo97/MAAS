export type EffectCode = "ES" | "ZI" | "ZO" | "PA-I" | "PA-D" | "TI-A" | "TI-B" | "PP";

export interface EffectSpec {
  code: EffectCode;
  intensity: number;
  target?: string | null;
  tremor: boolean;
}

export interface TimelineCue {
  id: string;
  type: "scene" | "dialogue" | "sfx" | "transition" | "advice" | "ending";
  startMs: number;
  durationMs: number;
  text?: string;
  speaker?: string;
  effect?: EffectSpec;
  backgroundUrl?: string;
  spriteUrl?: string;
  speakerPosition?: "izquierda" | "derecha";
}

export interface EpisodeManifest {
  schemaVersion: "1.0";
  episodeId: string;
  title: string;
  profile: "legacy-v1" | "canonical-v1";
  durationMs: number;
  timeline: TimelineCue[];
}
