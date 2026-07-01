# Layout de salida

```text
dist/
├── index.html
├── assets/<sha256>.<ext>
└── episodes/<episode-id>/
    ├── index.html
    ├── episode.manifest.json
    └── build-report.json
```

- `index.html` raíz puede actuar como catálogo.
- Cada episodio tiene URL propia y carga assets compartidos por hash.
- No duplicar sprites/audio por episodio.
- `episode.manifest.json` contiene IDs y URLs resueltas same-origin.
- `build-report.json` registra hashes de input/output, perfil, warnings, tiempos y herramientas.
- El bundle debe funcionar desde un servidor estático; no prometer soporte directo de `file://`.
