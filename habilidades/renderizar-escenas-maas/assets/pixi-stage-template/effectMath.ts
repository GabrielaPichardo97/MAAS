export type EffectCode = "ES" | "ZI" | "ZO" | "PA-I" | "PA-D" | "TI-A" | "TI-B" | "PP";

export interface CameraTransform {
  scale: number;
  xFraction: number;
  yFraction: number;
}

export function legacyCameraTransform(
  code: EffectCode,
  intensity: number,
  speakerPosition: "izquierda" | "derecha",
  timeSeconds: number,
): CameraTransform {
  const safeIntensity = intensity > 0 ? intensity : 1;
  const base = 0.05;
  const signX = speakerPosition === "izquierda" ? -1 : 1;
  if (code === "ES") return { scale: 1, xFraction: 0, yFraction: 0 };
  if (code === "ZI" || code === "ZO") {
    const zoom = base * safeIntensity * timeSeconds;
    const scale = code === "ZI" ? 1 + zoom : 1 - zoom;
    if (scale <= 0) throw new Error(`E_EFFECT: escala no positiva (${scale})`);
    return { scale, xFraction: signX * base * safeIntensity * timeSeconds / 2, yFraction: 0 };
  }
  if (code === "PA-I" || code === "PA-D") {
    return {
      scale: 1 + base * safeIntensity * timeSeconds / 2,
      xFraction: signX * base * safeIntensity * timeSeconds / 4,
      yFraction: 0,
    };
  }
  if (code === "TI-A" || code === "TI-B") {
    return { scale: 1, xFraction: 0, yFraction: (code === "TI-A" ? 1 : -1) * base * safeIntensity * timeSeconds };
  }
  return { scale: 1 + base * safeIntensity * timeSeconds, xFraction: 0, yFraction: 0 };
}
