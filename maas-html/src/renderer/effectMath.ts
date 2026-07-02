import type { EffectCode } from "../types";

export function legacyCameraTransform(code: EffectCode, intensity: number, position: "izquierda" | "derecha", seconds: number) {
  const i = intensity > 0 ? intensity : 1;
  const b = 0.05;
  const sign = position === "izquierda" ? -1 : 1;
  if (code === "ES") return { scale: 1, x: 0, y: 0 };
  if (code === "ZI" || code === "ZO") {
    const scale = 1 + (code === "ZI" ? 1 : -1) * b * i * seconds;
    if (scale <= 0) throw new Error("E_EFFECT: escala no positiva");
    return { scale, x: sign * b * i * seconds / 2, y: 0 };
  }
  if (code === "PA-I" || code === "PA-D") return { scale: 1 + b * i * seconds / 2, x: sign * b * i * seconds / 4, y: 0 };
  if (code === "TI-A" || code === "TI-B") return { scale: 1, x: 0, y: (code === "TI-A" ? 1 : -1) * b * i * seconds };
  return { scale: 1 + b * i * seconds, x: 0, y: 0 };
}
