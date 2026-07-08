import type { Interaction, SubtitleCue, TimelineCue } from "./types";

export function narrativeCues(timeline: TimelineCue[]): TimelineCue[] {
  return timeline.filter((cue) => cue.type !== "scene");
}

export function activeNarrativeCue(timeline: TimelineCue[], positionMs: number): TimelineCue | undefined {
  return narrativeCues(timeline).find(
    (cue) => positionMs >= cue.startMs && positionMs < cue.startMs + cue.durationMs,
  );
}

export function fallbackSubtitleFromCue(cue: TimelineCue | undefined): SubtitleCue | undefined {
  if (!cue?.text) return undefined;
  const kind = cue.type === "sfx" ? "sound" : cue.type === "transition" ? "transition" : cue.type === "advice" ? "advice" : "dialogue";
  return {
    id: `fallback-${cue.id}`,
    cueId: cue.id,
    startMs: cue.startMs,
    endMs: cue.startMs + cue.durationMs,
    speakerLabel: cue.speakerLabel ?? cue.speakerAlias ?? cue.speaker ?? "",
    text: cue.text,
    kind,
  };
}

export function activeSubtitle(subtitles: SubtitleCue[] | undefined, timeline: TimelineCue[], positionMs: number): SubtitleCue | undefined {
  const current = subtitles?.find((subtitle) => positionMs >= subtitle.startMs && positionMs < subtitle.endMs);
  return current ?? fallbackSubtitleFromCue(activeNarrativeCue(timeline, positionMs));
}

export function activeInteractions(interactions: Interaction[] | undefined, positionMs: number): Interaction[] {
  return (interactions ?? []).filter(
    (interaction) => positionMs >= interaction.startMs && positionMs < interaction.startMs + interaction.durationMs,
  );
}

export function clampPosition(positionMs: number, durationMs: number): number {
  return Math.max(0, Math.min(durationMs, positionMs));
}

export function formatTime(positionMs: number): string {
  const seconds = Math.max(0, Math.floor(positionMs / 1000));
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}
