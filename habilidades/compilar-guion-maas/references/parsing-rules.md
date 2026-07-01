# Reglas de compilación

## Índice

1. Fases
2. Estado del parser
3. Tiempos sin audio
4. Recuperación legado

## 1. Fases

1. Normalizar encoding y saltos de línea.
2. Validar el contenedor.
3. Tokenizar headers, diálogo, OSD, lugares y transiciones conservando línea original.
4. Formar una escena desde el primer header hasta `**LUGAR**`.
5. Resolver personaje, emoción, sprite y sonido mediante manifests explícitos.
6. Calcular tiempos y producir cues.
7. Serializar con claves ordenadas.

## 2. Estado del parser

Un header activa personaje, duración, emoción y dirección actoral. Cada diálogo hereda esos valores hasta el siguiente header. El lugar cierra la escena completa; una transición genera un cue independiente entre escenas.

No eliminar apóstrofes, OSD consecutivos ni líneas repetidas. No usar Pandas para asignar posiciones: el manifest registra `speakerOrder` y el renderer decide layout.

## 3. Tiempos sin audio

Si no existe duración de audio, repartir la duración declarada entre las líneas del header y aplicar mínimo 2000 ms por cue en `legacy-v1`. En `canonical-v1`, repartir sin mínimo y exigir al menos 40 ms. Cuando haya audio, `$sincronizar-audio-maas` recalcula `resolvedDurationMs`.

## 4. Recuperación legado

- Normalizar `ZO1.2` a `ZO*1.2` con warning.
- Reconocer `N segundo(s)` y `MM:SS`.
- Permitir prefijos numéricos `1. ` solo en importación y eliminarlos del texto final.
- Conservar header editorial como metadata, no como diálogo.
- Si falta lugar, fallar; el comportamiento histórico aleatorio no es reproducible.
