# Contrato de adaptación creativa

`dialogue-adaptation.json` usa `schemaVersion: 1.0` y el schema de `assets/schemas/dialogue-adaptation.schema.json`.

- `sourceText` conserva el input con saltos normalizados a LF; `sourceTextSha256` se calcula sobre UTF-8.
- Cada beat incluye `sourceFragment`, rango de líneas y `verbatimText`. El último es la única fuente del diálogo hablado posterior.
- `speaker` conserva la etiqueta editorial y `characterId` propone un ID semántico; no afirma que exista media.
- `emotion`, `stageDirection`, `durationMs`, `placeId` y `placeLabel` registran valor, inferencia y confianza.
- `unresolved` contiene diagnósticos bloqueantes. `E_SPEAKER_AMBIGUOUS` impide dirección y ensamblado.

Usar emociones fuente comprendidas por el compilador: `felicidad`, `tristeza`, `enojo`, `seriedad`, `preocupación`, `miedo`, `sorpresa`, `confusión` o sus aliases documentados. La base conservadora usa `seriedad`.

Formatos reconocidos por el parser inicial:

```text
Pato: ¿Ya llegaste?
[Cactus] Apenas.

PATO
No me mires así.
```

El parser produce una base conservadora. La skill puede mejorar la puesta leyendo la semántica, pero nunca modificar `verbatimText`.
