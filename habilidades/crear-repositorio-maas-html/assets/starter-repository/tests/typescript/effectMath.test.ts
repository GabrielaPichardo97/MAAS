import { describe, expect, it } from "vitest";
import { legacyCameraTransform } from "../../src/renderer/effectMath";

describe("legacyCameraTransform", () => {
  it("reproduce ZI a los dos segundos", () => {
    expect(legacyCameraTransform("ZI", 1, "izquierda", 2)).toEqual({ scale: 1.1, x: -0.05, y: 0 });
  });
  it("mantiene PA-I y PA-D idénticos en legacy", () => {
    expect(legacyCameraTransform("PA-I", 1.2, "derecha", 5)).toEqual(legacyCameraTransform("PA-D", 1.2, "derecha", 5));
  });
});
