# Contrato de `episode.manifest.json`

## Índice

1. Raíz
2. Timeline
3. Efectos y audio
4. Orden y determinismo

## 1. Raíz

El manifiesto contiene `schemaVersion`, `episodeId`, `title`, `language`, `status`, `seed`, `profile`, `orientations`, `characters`, `assets`, `audioPolicy`, `timeline`, `durationMs` y `warnings`.

- `profile`: `legacy-v1`, `canonical-v1` o `canonical-v2`. Este último exige `schemaVersion: 2.0`.
- `orientations`: subconjunto no vacío de `landscape`, `portrait`.
- `assets`: IDs presentes en un manifiesto de assets validado.
- `warnings`: diagnósticos que no impidieron compilar.

## 2. Timeline

Todos los cues comparten:

```json
{
  "id": "cue-0001",
  "type": "dialogue",
  "startMs": 0,
  "durationMs": 2400
}
```

Tipos:

- `scene`: lugar, orientación y rango que agrupa cues.
- `dialogue`: speaker, texto, emoción, dirección actoral, sprite y efecto.
- `sfx`: sound key, asset y efecto.
- `transition`: texto, imagen, duración y audio.
- `advice`: texto seleccionado por seed.
- `ending`: asset por orientación.

`startMs` es absoluto, entero y no negativo. Los cues narrativos no se solapan; las pistas de música sí pueden solaparse mediante `audioPolicy`.

## 3. Efectos y audio

```json
{
  "effect": {
    "code": "ZI",
    "intensity": 1.2,
    "target": null,
    "tremor": true
  },
  "audio": {
    "assetId": "voice-cue-0001",
    "gain": 1.0,
    "fadeInMs": 0,
    "fadeOutMs": 0
  }
}
```

Los assets ausentes se representan como error de compilación, no con una ruta vacía.

En `canonical-v2`, cada cue usa `effects` en lugar de `effect`:

```json
{
  "effects": [{
    "id": "motion.push-in.emphasis.subtle.v1.0.0",
    "role": "dominant",
    "intensity": 0.3,
    "startOffsetMs": 0,
    "durationMs": 1200,
    "target": "speaker",
    "params": {"scaleEnd": 1.1, "easing": "ease-in-out"}
  }]
}
```

Admitir máximo tres efectos y un solo `dominant`, `support` y `finish`. Resolver siempre una versión exacta.

## 4. Orden y determinismo

- Ordenar cues por `startMs`, luego por `id`.
- Numerar IDs según orden del input.
- Serializar JSON con claves ordenadas y newline final.
- Toda elección variable usa un PRNG documentado a partir de `seed`.
- Mismo input, assets, perfil y versión producen el mismo SHA-256.
