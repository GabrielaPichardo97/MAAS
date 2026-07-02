import { describe, expect, it } from "vitest";
import manifest from "../../public/episodes/episodio-0-prueba-renderizar/episode.manifest.json";
import { activeNarrativeCue, clampPosition, formatTime, narrativeCues } from "../../src/timeline";
import type { EpisodeManifest } from "../../src/types";

const episode = manifest as EpisodeManifest;

describe("timeline del Episodio 0", () => {
  it("conserva la duración y los 17 cues narrativos", () => {
    expect(episode.durationMs).toBe(33_900);
    expect(episode.timeline).toHaveLength(19);
    expect(narrativeCues(episode.timeline)).toHaveLength(17);
  });

  it("selecciona la transición y la segunda escena en sus límites", () => {
    expect(activeNarrativeCue(episode.timeline, 16_000)?.id).toBe("cue-0009");
    expect(activeNarrativeCue(episode.timeline, 17_900)?.id).toBe("cue-0010");
    expect(activeNarrativeCue(episode.timeline, 33_900)).toBeUndefined();
  });

  it("incluye PNG reales para todos los cues de personaje", () => {
    const characterCues = narrativeCues(episode.timeline).filter((cue) => cue.type === "dialogue" || cue.type === "sfx");
    expect(characterCues).toHaveLength(16);
    expect(characterCues.every((cue) => cue.media?.spriteAssetId.startsWith("character-") && cue.media?.backgroundAssetId.startsWith("background-"))).toBe(true);
    expect(characterCues.every((cue) => cue.media?.fallbackApplied === null)).toBe(true);
    expect(Object.values(episode.assetUrls).every((url) => /^\/assets\/[a-f0-9]{64}\.png$/.test(url))).toBe(true);
  });
});

describe("utilidades del reproductor", () => {
  it("limita seek y formatea el tiempo", () => {
    expect(clampPosition(-10, 100)).toBe(0);
    expect(clampPosition(110, 100)).toBe(100);
    expect(formatTime(33_900)).toBe("0:33");
  });
});
