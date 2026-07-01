# Arquitectura PixiJS

Orden de capas:

```text
Application
└── viewportContainer
    └── cameraContainer
        └── flattenedScene(RenderTexture)
            ├── background
            ├── sprites
            └── visualText
```

1. Cargar assets mediante IDs del manifest.
2. Componer en `sceneContainer` con coordenadas lógicas.
3. Renderizar a `RenderTexture` 1920×1080.
4. Mostrar esa textura en `cameraContainer`.
5. Aplicar filtro de temblor al sprite aplanado.
6. Aplicar scale/translation de cámara al contenedor.
7. Escalar `viewportContainer` para el elemento host.

El filtro de temblor recibe edge map, frame index, seed, displacement 14, factor 1.1 y blend 0.8. Usar sampler mirror para remap y clamp-to-edge para cámara.

No meter controles en el canvas. React administra estado, accesibilidad y DOM; Pixi solo dibuja. Liberar RenderTextures antiguas al cambiar cue.
