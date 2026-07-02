---
name: compilar-guion-maas
description: Normaliza JSON históricos y compila la gramática textual de MAAS a episode.manifest.json determinista, incluidos stacks de efectos canonical-v2. Usar al importar Guiones/capitulos, resolver personajes y emociones, validar tokens {{fx ...}}, calcular cues o diagnosticar errores de parsing sin ejecutar TTS ni render de video.
---

# Compilar guion MAAS

1. Validar el input con `$definir-contratos-maas`.
2. Para JSON históricos, ejecutar `scripts/normalize_legacy_input.py` y conservar el reporte emitido por stderr.
3. Leer `references/parsing-rules.md`; no copiar los efectos secundarios del parser legado.
4. Proporcionar mappings explícitos de personajes y emociones según las referencias.
5. Ejecutar `scripts/compile_episode.py INPUT --profile legacy-v1 --output episode.manifest.json`.
6. Validar el manifiesto producido y conservar warnings.

Para nuevos episodios con efectos descriptivos, usar `--profile canonical-v2 --effect-catalog PATH`. Exigir máximo tres roles únicos y recursos explícitos para efectos asistidos o preprocesados.

## Reglas

- Recibir diálogo ordinario únicamente a través de `$creativa-adaptar-dialogo-maas` y `$creativa-ensamblar-episodio-maas`; el compilador valida gramática, no toma decisiones de puesta.
- No llamar OpenAI ni ElevenLabs durante parsing.
- No escribir scripts intermedios, renombrar inputs ni elegir lugares al azar.
- Mantener orden del documento, seed y serialización estable.
- Tratar aliases no resueltos como identidad solo en `legacy-v1`; en `canonical-v1`, exigir mapping.
