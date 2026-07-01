---
name: reproducir-efectos-maas
description: Especifica, implementa y prueba la cámara, paneo, zoom, close-up, tilt, temblor, filtros, rotaciones y transiciones de MAAS en perfiles legacy-v1 y canonical-v1. Usar al tocar fórmulas visuales, shaders PixiJS, duraciones o fixtures de paridad.
---

# Reproducir efectos MAAS

1. Leer `references/effects-catalog.md` completo antes de modificar un efecto.
2. Elegir un perfil; usar `legacy-v1` por defecto para paridad.
3. Leer la especificación correspondiente y `references/timing-formulas.md`.
4. Usar `scripts/legacy_effect_math.py` como oráculo numérico de cámara.
5. Regenerar fixtures con `scripts/export_effect_fixtures.py` y comparar inicio, mitad y final.
6. Aplicar los efectos al frame aplanado, no a sprites individuales, salvo que `canonical-v1` lo indique.

## Guardas

- Trabajar a tiempo continuo, cuantizando el temblor a 25 FPS.
- Usar clamp-to-edge para igualar `BORDER_REPLICATE`.
- No corregir un accidente legado dentro de `legacy-v1`; documentarlo y corregirlo solo en `canonical-v1`.
- Rechazar zoom-out cuya escala llegue a cero o sea negativa.
