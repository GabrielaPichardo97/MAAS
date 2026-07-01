---
name: definir-contratos-maas
description: Define, documenta y valida los contratos versionados de entrada, assets y manifiestos de MAAS HTML. Usar al crear o cambiar episode-source.json, asset-manifest.json, episode.manifest.json, la gramática textual de guiones o los diagnósticos del compilador.
---

# Definir contratos MAAS

1. Leer `references/input-contract.md` y `references/script-grammar.md` antes de aceptar un input.
2. Tratar los schemas de `assets/schemas/` como fuente de verdad; no inferir campos nuevos desde ejemplos.
3. Ejecutar `scripts/validate_episode.py INPUT --mode strict` para inputs nuevos y `--mode legacy` para importar JSON históricos.
4. Corregir errores antes de compilar. Conservar advertencias en el `build-report.json`.
5. Leer `references/canonical-manifest.md` al producir o consumir una timeline.
6. Usar exclusivamente los códigos de `references/validation-errors.md`.

## Invariantes

- Mantener UTF-8, tiempos enteros en milisegundos y rutas relativas con `/`.
- No modificar el archivo fuente durante validación o compilación.
- No resolver silenciosamente personajes, lugares, emociones, assets ni efectos desconocidos.
- Conservar `declaredDurationMs` y calcular `resolvedDurationMs` por separado.
- Escapar el contenido al mostrarlo; nunca tratar `content` como HTML.

## Salida mínima

Entregar diagnósticos ordenados por línea y columna con `code`, `severity`, `message` y `suggestion`. Un error produce exit code 1; solo advertencias producen exit code 0.
