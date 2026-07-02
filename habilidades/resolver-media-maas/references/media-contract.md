# Contrato de media canónica

`media-catalog.json` referencia fuentes legadas inmutables mediante IDs semánticos.

## Campos comunes

- `id`, `type`, `sourcePath`, `sha256`, `mimeType`, `width`, `height`.
- `licenseId`, `allowedForPublish` y `sourceAssetId`.
- `contentBox` y `anchor` cuando pueden medirse.

## Sprites

- `characterId`, `emotion` y `gaze` normalizados.
- Aliases: `angy → angry`, `condused → confused`; `Correct_` no forma parte del ID.
- La mirada canónica es `left`; el renderer refleja mediante `mirrorX`.

## Fondos

- `placeId`, `orientation`, `layout` y `profile`.
- Sin sufijo: center; `(1)`: character-left; `(2)`: character-right.
- `(3)` a `(5)` son variantes portrait laterales de `legacy-v1`, no portrait canónico nativo.

Los IDs no dependen de rutas públicas. El staging produce `/assets/<sha256>.<ext>`.
