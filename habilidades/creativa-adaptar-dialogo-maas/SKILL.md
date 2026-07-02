---
name: creativa-adaptar-dialogo-maas
description: Convierte diálogo ordinario, teatral o etiquetado en una adaptación MAAS estructurada sin reescribir los parlamentos. Usar al recibir conversación en bruto y necesitar speakers, escenas, beats, emociones, acciones, duraciones, lugares y ambigüedades antes de dirigir o compilar un episodio HTML.
---

# Creativa · Adaptar diálogo MAAS

1. Leer `references/adaptation-contract.md`.
2. Ejecutar `scripts/adapt_dialogue.py INPUT --title TITLE --output dialogue-adaptation.json`; proporcionar `--place` cuando el usuario ya haya fijado el lugar.
3. Revisar cada beat y mejorar únicamente campos inferidos: emoción, acción, duración, escena y lugar.
4. Mantener `verbatimText`, `sourceFragment`, `sourceText` y sus hashes sin cambios.
5. Si existe `E_SPEAKER_AMBIGUOUS`, pedir la atribución de hablantes antes de continuar.
6. Ejecutar `scripts/validate_adaptation.py dialogue-adaptation.json`.
7. Entregar la adaptación a `$creativa-dirigir-escena-maas`; no añadir tokens `{{fx ...}}` aquí.

## Guardas

- No corregir, resumir ni embellecer un parlamento; presentar alternativas editoriales fuera del artefacto.
- No inventar identidades de personajes ni sustituir lugares para hacerlos coincidir con la media disponible.
- Marcar toda deducción con `inferred: true` y una confianza `0..1`.
- Usar `es-MX`, `draft`, slug del título y seed SHA-256 cuando falten metadatos.
