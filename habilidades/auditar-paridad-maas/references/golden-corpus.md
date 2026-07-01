# Corpus golden

Seleccionar al menos:

1. Escena corta con cada código de cámara.
2. Escena con PP, sprite grande y ambos lados.
3. OSD corto, largo y silencio.
4. Dos escenas con transición.
5. Landscape y portrait del mismo episodio.
6. Un episodio extenso con múltiples speakers.

Por cada caso guardar únicamente lo necesario:

```text
tests/golden/<case>/
├── source.json
├── character-map.json
├── asset-manifest.slice.json
├── expected-timeline.json
├── expected-frames/<timestamp>.png
└── provenance.json
```

`provenance.json` registra video/frame legado, SHA-256, comando de extracción y relación demostrada con el input. Si no puede demostrarse la relación, marcar `referenceOnly=true` y excluir de gates automáticos.

No migrar videos completos cuando basten frames y pequeños fragmentos autorizados.
