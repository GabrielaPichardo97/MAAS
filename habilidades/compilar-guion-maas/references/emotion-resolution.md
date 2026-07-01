# Resolución de emociones

Normalizar trim y Unicode casefold, pero conservar el valor original en `sourceEmotion`.

Categorías visuales: `happy`, `sad`, `angry`, `serious`, `worried`, `surprised`, `dizzy`, `confused`, `scared`, `cute`, `realistic`, `a`.

El mapping debe estar versionado. Si el sprite exacto falta, recorrer un fallback declarado y finito, por ejemplo `worried → sad → serious → realistic → a`. Detectar ciclos.

- `legacy-v1`: emoción desconocida puede usar `happy` con warning explícito.
- `canonical-v1`: emoción desconocida es error.
- Nunca seleccionar el primer archivo del directorio ni usar aleatoriedad.
