---
name: seleccionar-efectos-maas
description: Analiza beats, escenas y guiones de MAAS para recomendar efectos canonical-v2 con parámetros, rol, justificación, contraindicaciones, requisitos y fallback. Usar al decidir qué efecto aplicar, crear un stack dominante/soporte/acabado, revisar si un efecto conviene narrativamente o convertir intención editorial en tokens {{fx ...}} explícitos.
---

# Seleccionar efectos MAAS

1. Leer `references/selection-rules.md` y consultar `references/effects-catalog.json`.
2. Definir por beat: tipo de escena, arousal, continuidad, foco, estilización, tempo y sincronía musical.
3. Descartar efectos cuyas contraindicaciones o requisitos no se cumplan.
4. Ejecutar `scripts/recommend_effects.py CONTEXT.json` para obtener candidatos reproducibles.
5. Elegir como máximo un efecto por rol: `dominant`, `support` y `finish`.
6. Explicar la elección y entregar tokens canonical-v2; no aplicarlos sin aprobación explícita.

## Guardas

- Consumir la intención y el contexto de `$creativa-dirigir-escena-maas`; esta skill decide IDs y parámetros técnicos, no actuación, bloqueo ni encuadre narrativo.
- Priorizar legibilidad y semántica sobre espectacularidad.
- No recomendar `preprocessed` sin el artefacto requerido ni `input-assisted` sin sus inputs.
- Mantener los flashes por debajo de cuatro eventos por segundo; preferir cero.
- Proponer el fallback documentado cuando un requisito no esté disponible.
- Usar IDs exactos y versiones exactas; nunca resolver `latest`.

## Salida

Entregar contexto inferido, hasta tres efectos, razones, riesgos, requisitos, parámetros y tokens como:

```text
{{fx motion.push-in.emphasis.subtle.v1.0.0 role=dominant intensity=0.30 target=speaker}}
```
