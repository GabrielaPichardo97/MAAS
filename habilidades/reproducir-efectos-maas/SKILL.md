---
name: reproducir-efectos-maas
description: Cataloga, implementa y prueba los efectos visuales programables de MAAS en perfiles legacy-v1, canonical-v1 y canonical-v2. Usar al tocar IDs, parámetros, fórmulas, filtros, shaders PixiJS, transiciones, soporte web, fallbacks o fixtures de paridad.
---

# Reproducir efectos MAAS

1. Leer `references/effects-catalog.md` para legado o `references/effects-catalog-v2.md` y su JSON para canonical-v2.
2. Elegir un perfil; usar `legacy-v1` por defecto para paridad.
3. Leer la especificación correspondiente y `references/timing-formulas.md`.
4. Usar `scripts/legacy_effect_math.py` como oráculo numérico de cámara.
5. Regenerar fixtures con `scripts/export_effect_fixtures.py` y comparar inicio, mitad y final.
6. Aplicar los efectos al frame aplanado salvo que el catálogo canonical-v2 declare `targets`; en ese caso aislar `background` o `speaker` y mantener texto/UI fuera del procesamiento.
7. En canonical-v2, ordenar por rol `dominant`, `support`, `finish`; limitar el stack a tres y respetar requisitos y fallbacks.

## Guardas

- Trabajar a tiempo continuo, cuantizando el temblor a 25 FPS.
- Usar clamp-to-edge para igualar `BORDER_REPLICATE`.
- No corregir un accidente legado dentro de `legacy-v1`; documentarlo y corregirlo solo en `canonical-v1`.
- Rechazar zoom-out cuya escala llegue a cero o sea negativa.
- Desactivar o reducir efectos según `reducedMotion` y no permitir más de tres flashes por segundo.
- Mantener sincronizados el catálogo de `$seleccionar-efectos-maas`, este mirror y `/effects-catalog.json`.

# Perfil `canonical-v2`

- Usar IDs exactos `familia.efecto.intencion.variante.vSemver` y parámetros normalizados.
- Ejecutar `native`; etiquetar `approximation`; exigir inputs para `input-assisted` y artefactos para `preprocessed`.
- Aplicar transformaciones a cámara y acabados en una capa separada.
- Usar seed estable para shake, glitch y partículas.
- Fallar ante requisitos ausentes y mostrar el fallback sin sustituirlo.
