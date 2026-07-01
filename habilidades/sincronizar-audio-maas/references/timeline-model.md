# Modelo temporal de audio

`legacy-v1`:

```text
dialogue = max(2000, floor((audioMs + 200) / 1000) * 1000)
sfx      = duración del cue visual; cortar audio si excede, no repetir si es corto
transition = 1900 ms
```

`canonical-v1`:

```text
dialogue = max(declaredDurationMs, audioMs + 200)
sfx      = max(40, audioMs)
```

Recalcular `startMs` secuencialmente con enteros. Actualizar las escenas a partir de sus `cueIds`. La desviación aceptable es ≤20 ms para audio y ≤40 ms para imagen a 25 FPS.

El seek cancela nodos programados, calcula el offset dentro del cue actual y programa los siguientes contra un nuevo origen monotónico.
