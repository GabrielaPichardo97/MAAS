import { describe, expect, it } from "vitest";
import { rebaseAssetUrl } from "../../src/assetUrls";

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
});
