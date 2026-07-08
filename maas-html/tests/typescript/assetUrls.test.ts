import { describe, expect, it } from "vitest";
import { rebaseAssetUrl, rebaseManifestAssets } from "../../src/assetUrls";
import type { EpisodeManifest } from "../../src/types";

describe("rebaseAssetUrl", () => {
  it("mantiene rutas locales en desarrollo", () => {
    expect(rebaseAssetUrl("/assets/demo.png", "/")).toBe("/assets/demo.png");
  });

  it("publica assets bajo el subpath de GitHub Pages", () => {
    expect(rebaseAssetUrl("/assets/demo.png", "/MAAS/")).toBe("/MAAS/assets/demo.png");
    expect(rebaseAssetUrl("/MAAS/assets/demo.png", "/MAAS/")).toBe("/MAAS/assets/demo.png");
  });

  it("no altera URLs externas", () => {
    expect(rebaseAssetUrl("https://example.test/demo.png", "/MAAS/")).toBe("https://example.test/demo.png");
  });

  it("publica tracks de subtitulos bajo el subpath", () => {
    const manifest = {
      assetUrls: {},
      subtitleTracks: [{ id: "subtitles-es-mx", kind: "subtitles", format: "webvtt", language: "es-MX", label: "Espanol", url: "/episodes/demo/subtitles.es-mx.vtt", sha256: "0".repeat(64) }],
    } as EpisodeManifest;
    expect(rebaseManifestAssets(manifest, "/MAAS/").subtitleTracks?.[0].url).toBe("/MAAS/episodes/demo/subtitles.es-mx.vtt");
  });
});
