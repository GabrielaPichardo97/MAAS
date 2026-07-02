# Contrato de dirección cinematográfica

`cinematic-direction.json` usa `schemaVersion: 1.0` y referencia por SHA-256 el archivo de adaptación exacto.

- `direction` describe puesta y cámara; no contiene decisiones del renderer.
- `effectContext` usa los campos aceptados por `seleccionar-efectos-maas/scripts/recommend_effects.py`.
- `effects` sólo admite IDs versionados del catálogo, roles únicos y parámetros válidos.
- `verbatimText`, speaker y beat ID deben coincidir con la adaptación.
- `approval.status` permanece `proposed` hasta que el usuario acepte el plan. La aprobación exige `approvedBy` y `approvedAt` ISO 8601.

El efecto expresa la intención del beat; no reemplaza una dirección de actuación o composición débil.
