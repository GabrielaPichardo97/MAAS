# Arquitectura del repositorio nuevo

## Índice

1. Capas
2. Estructura
3. Flujo
4. Decisiones

## 1. Capas

- `content/`: fuentes editoriales inmutables.
- `schemas/`: contratos JSON 2020-12.
- `tools/maas_builder/`: CLI Python y automatización de build.
- `tools/scripts/`: implementaciones deterministas aportadas por las skills.
- `src/`: shell React, renderer PixiJS, timeline y Web Audio.
- `public/assets/`: assets autorizados y hasheados.
- `dist/`: salida generada, nunca fuente.
- `tests/`: unitarias Python/TypeScript, golden y E2E.

## 2. Estructura

```text
maas-html/
├── content/episodes/
├── schemas/
├── public/assets/
├── src/{audio,renderer}/
├── tools/{maas_builder,scripts}/
├── tests/{python,typescript,e2e,golden}/
├── package.json
├── pyproject.toml
└── vite.config.ts
```

## 3. Flujo

```text
episode-source.json
  → validate
  → compile + asset manifest
  → episode.manifest.json
  → Vite static build
  → browser validation
  → PixiJS + Web Audio
  → parity report
```

El renderer nunca parsea el guion libre. El compilador nunca genera video. La publicación nunca obtiene secretos del navegador.

## 4. Decisiones

- React controla UI/estado; PixiJS dibuja.
- Coordenadas lógicas 1920×1080; salida portrait mediante composición legada rotada.
- JSON Schema es autoridad de contratos.
- Build reproducible con seed, claves ordenadas y assets por SHA-256.
- Carpeta estática por episodio con assets compartidos.
