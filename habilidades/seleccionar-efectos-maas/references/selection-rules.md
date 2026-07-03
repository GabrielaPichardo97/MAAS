# Reglas de selección editorial

## Índice

1. Contexto
2. Elegibilidad
3. Puntuación
4. Roles
5. Intensidad
6. Escenarios frecuentes

## 1. Contexto

Normalizar `sceneType`, `arousal`, `continuity`, `focus`, `stylization`, `tempo`, `musicSync`, `textNeed` y `availableInputs`. Los valores numéricos usan `0..1`; `tempo` es BPM.

## 2. Elegibilidad

Excluir un efecto si coincide una contraindicación, no está disponible en MAAS web, exige un input ausente o contradice movimiento reducido. Los efectos `preprocessed` requieren una ruta de artefacto aprobada. No sustituirlos silenciosamente.

## 3. Puntuación

Puntuar cada candidato elegible:

```text
score = 0.30*sceneFit + 0.20*continuityFit + 0.20*energyFit
      + 0.15*focusFit + 0.10*musicFit + 0.05*platformFit
```

Restar `0.35` por cada contraindicación blanda. Una contraindicación dura o requisito ausente hace al candidato inelegible. En empate ordenar por menor costo y luego por ID.

## 4. Roles

- `dominant`: expresa la intención principal del beat.
- `support`: mejora foco, continuidad o legibilidad sin competir.
- `finish`: acabado breve de color, textura o impacto.

Usar hasta tres entradas, una por rol. Evitar dos efectos dominantes o dos transformaciones que controlen simultáneamente la misma propiedad.

Para el stack artesanal, usar `line-boil` como dominante, `cutout-wobble` como soporte y `paper-grain` como acabado. No combinar line boil y wobble con intensidad alta sobre el mismo personaje; mantener el texto fuera de las capas afectadas.

## 5. Intensidad

```text
intensity = clamp(0.35*arousal + 0.20*tempoNorm + 0.20*stylization
                  + 0.10*musicHit - 0.25*continuity, 0, 1)
```

Limitar entrevistas a `0.35`, tutoriales a `0.45` y piezas institucionales a `0.30`, salvo instrucción explícita.

## 6. Escenarios frecuentes

| Escenario | Dominante | Soporte | Evitar |
|---|---|---|---|
| Entrevista | morph cut o corte limpio | push-in sutil | glitch, shake, ramp agresivo |
| Acción/deporte | speed ramp o punch edit | motion blur | disolución lenta, texto largo |
| Tutorial/producto | callout o split-screen | color limpio | shake, flare intrusivo |
| Música/branding | kinetic type o audio-reactive | partículas/light leak | neutralidad total |
| Suspenso/sci-fi | glitch o jump cut | color/aberración | acabado amable sin tensión |
