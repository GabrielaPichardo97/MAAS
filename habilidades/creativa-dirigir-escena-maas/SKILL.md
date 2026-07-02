---
name: creativa-dirigir-escena-maas
description: Diseña la dirección cinematográfica de una adaptación MAAS mediante actuación, bloqueo, foco, encuadre, movimiento, ritmo, transiciones y propuestas de efectos canonical-v2. Usar después de adaptar diálogo y antes de aprobar tokens o compilar HTML; no usar para implementar efectos ni modificar el renderer.
---

# Creativa · Dirigir escena MAAS

1. Validar la entrada con `$creativa-adaptar-dialogo-maas`.
2. Leer `references/direction-contract.md` y ejecutar `scripts/prepare_direction.py ADAPTATION --output cinematic-direction.json`.
3. Definir por beat actuación, bloqueo, plano, foco, continuidad, energía, estilización y ritmo sin cambiar `verbatimText`.
4. Convertir esa intención a `effectContext` y usar `$seleccionar-efectos-maas` para obtener IDs exactos del catálogo.
5. Elegir como máximo un efecto `dominant`, uno `support` y uno `finish`; documentar razón, riesgos, requisitos y fallback.
6. Mantener `approval.status: proposed`. Presentar el plan al usuario sin insertar tokens en el guion.
7. Después de una aprobación explícita, ejecutar `scripts/approve_direction.py DIRECTION --approved-by IDENTIDAD --output DIRECTION_APPROVED`.
8. Ejecutar `scripts/validate_direction.py DIRECTION --adaptation ADAPTATION --catalog EFFECTS_CATALOG`.

## Guardas

- Priorizar claridad, actuación y continuidad sobre cantidad de efectos.
- No recomendar efectos asistidos o preprocesados sin inputs explícitos.
- No sustituir automáticamente un efecto ni afirmar que existe media.
- Dejar música, mezcla y sincronía sonora a `$sincronizar-audio-maas`.
