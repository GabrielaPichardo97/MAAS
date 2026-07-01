---
name: sincronizar-audio-maas
description: Construye y sincroniza voces, onomatopeyas, música, transiciones y endings de MAAS mediante manifiestos y Web Audio API. Usar al medir audio, recalcular resolvedDurationMs, mezclar ganancias, manejar autoplay o diagnosticar drift temporal.
---

# Sincronizar audio MAAS

1. Leer `references/audio-contract.md` y `references/timeline-model.md`.
2. Generar TTS solo en build y registrar el asset resultante; no incluir credenciales en la salida.
3. Ejecutar `scripts/build_audio_cues.py MANIFEST DURATIONS --profile legacy-v1` para recalcular tiempos.
4. Validar que todos los cues tengan duración y que `durationMs` coincida con el final real.
5. Implementar scheduling según `references/browser-audio-policy.md`.

## Guardas

- Usar un único reloj de `AudioContext`; no encadenar timers.
- Reprogramar cues después de seek, pause o suspensión del contexto.
- Silenciar música durante SFX únicamente en `legacy-v1`; canonical usa ducking configurable.
- Exigir gesto del usuario antes de autoplay con sonido.
