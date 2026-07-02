import { describe, expect, it } from "vitest";
import { canonicalEffectFrame } from "../../src/renderer/effectEngine";
import type { EffectInstance } from "../../src/types";

const effect = (id: string, params: EffectInstance["params"] = {}): EffectInstance => ({ id, role: "dominant", intensity: 1, startOffsetMs: 0, durationMs: 1000, params });

describe("canonicalEffectFrame", () => {
  it("aplica push-in con progreso continuo", () => {
    expect(canonicalEffectFrame([effect("motion.push-in.emphasis.subtle.v1.0.0", { scaleEnd: 1.2 })], 500, 1, false).scale).toBeCloseTo(1.1);
  });
  it("el shake es determinista", () => {
    const stack = [effect("motion.camera-shake.impact.decay.v1.0.0", { amplitudePx: 10, frequencyHz: 8 })];
    expect(canonicalEffectFrame(stack, 250, 42, false)).toEqual(canonicalEffectFrame(stack, 250, 42, false));
  });
  it("respeta movimiento reducido", () => {
    expect(canonicalEffectFrame([effect("motion.camera-shake.impact.decay.v1.0.0")], 250, 42, true)).toMatchObject({ scale: 1, x: 0, y: 0, rotation: 0 });
  });
});
