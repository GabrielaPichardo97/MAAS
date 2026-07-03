import { describe, expect, it } from "vitest";
import { EFFECT_SCENES } from "../../src/ui/effectScenes";

describe("EFFECT_SCENES", () => {
  it("define una escena narrativa única para cada efecto canonical-v2", () => {
    const scenes = Object.values(EFFECT_SCENES);
    expect(scenes).toHaveLength(37);
    expect(new Set(scenes.map((scene) => scene.title)).size).toBe(37);
    expect(scenes.every((scene) => scene.dialogue && scene.location && scene.leftActor && scene.rightActor)).toBe(true);
  });
});
