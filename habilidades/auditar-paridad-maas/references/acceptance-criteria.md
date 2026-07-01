# Criterios de aceptación

## Legacy-v1

- Drift de inicio/duración visual: máximo 40 ms.
- Drift de audio: máximo 20 ms.
- Posiciones y tamaños: máximo 2 px a resolución lógica.
- SSIM escena estática: mínimo 0.97.
- SSIM durante temblor: mínimo 0.93.
- Mismo input/assets/seed: mismos hashes de manifiesto.
- Cero secretos, assets bloqueados o errores de consola.

## Funcional

- Play, pause, seek, mute, volumen, captions y orientación.
- Teclado y focus visibles.
- `prefers-reduced-motion` no altera tiempos/audio.
- Recuperación de autoplay bloqueado y `AudioContext` suspendido.
- Landscape, portrait y resize sin deformación.

## Reporte

Cada caso incluye ID, input SHA, asset manifest SHA, profile, orientación, navegador, viewport, frame/cue, expected, actual, métrica, umbral, pass/fail y enlace relativo a evidencia.
