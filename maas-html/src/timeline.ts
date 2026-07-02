import type { TimelineCue } from "./types";

export function narrativeCues(timeline: TimelineCue[]): TimelineCue[] {
  return timeline.filter((cue) => cue.type !== "scene");
}

export function activeNarrativeCue(timeline: TimelineCue[], positionMs: number): TimelineCue | undefined {
  return narrativeCues(timeline).find(
    (cue) => positionMs >= cue.startMs && positionMs < cue.startMs + cue.durationMs,
  );
}

export function clampPosition(positionMs: number, durationMs: number): number {
  return Math.max(0, Math.min(durationMs, positionMs));
}

export function formatTime(positionMs: number): string {
  const seconds = Math.max(0, Math.floor(positionMs / 1000));
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}
