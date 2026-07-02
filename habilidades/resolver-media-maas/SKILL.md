---
name: resolver-media-maas
description: Cataloga, valida, resuelve y prepara personajes, fondos y demás media real para episodios MAAS HTML. Usar al sustituir placeholders, vincular cues con PNG existentes, generar reportes/fichas de media faltante o preparar assets hasheados para preview y publicación.
---

# Resolver media MAAS

1. Leer `references/media-contract.md` y `references/resolution-policy.md`.
2. Ejecutar `scripts/media_pipeline.py catalog RAW_MANIFEST --root LEGACY_ROOT --output media-catalog.json`.
3. Ejecutar `validate`; corregir IDs ambiguos, hashes o metadata antes de resolver episodios.
4. Ejecutar `report-gaps` para generar JSON, Markdown y fichas de producción. Los huecos generales no bloquean episodios que no los usan.
5. Ejecutar `resolve MANIFEST CATALOG PRESENTATION EMOTIONS --mode preview|publication`.
6. Ejecutar `stage` para copiar únicamente assets referenciados, autorizados y verificados por SHA-256.

## Guardas

- Aceptar `character-map.json` y `presentation.json` producidos por `$creativa-ensamblar-episodio-maas`, pero volver a comprobar cada ID contra el catálogo.
- Usar PNG existentes sin exigir conversión, reescalado o renombrado.
- Resolver siempre por ID semántico; nunca pasar rutas legadas al navegador.
- En preview, permitir sólo fallbacks declarados y reportarlos.
- En publicación, fallar ante fallback o media requerida ausente.
- No marcar audio, transiciones o endings como autorizados por inferencia.
- No modificar ni reorganizar `media/`.
