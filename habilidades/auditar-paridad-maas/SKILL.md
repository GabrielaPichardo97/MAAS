---
name: auditar-paridad-maas
description: Mide y documenta paridad visual, temporal, sonora y funcional entre el reproductor MAAS HTML y los outputs legados. Usar para golden tests, SSIM, drift de cues, aceptación de perfiles y generación de evidencia auditable.
---

# Auditar paridad MAAS

1. Leer `references/golden-corpus.md` y fijar input, assets, seed, orientación y perfil.
2. Comparar timelines con `scripts/compare_timelines.py`.
3. Comparar frames con `scripts/compare_frames.py`; usar umbrales de `references/acceptance-criteria.md`.
4. Registrar excepciones únicamente en `references/known-differences.md`, con causa y aprobación.
5. Consolidar reportes mediante `scripts/generate_audit_report.py`.
6. No aprobar `canonical-v1` por resultados de `legacy-v1`; cada perfil tiene baseline independiente.

## Guardas

- No comparar archivos sin demostrar que pertenecen al mismo episodio/seed.
- Conservar capturas originales y hashes.
- Reportar fallos; nunca redondear métricas para ocultar desviaciones.
- Requerir revisión humana de transiciones, captions y audio además de métricas.
