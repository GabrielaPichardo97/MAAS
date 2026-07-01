# Reproductor responsivo y accesible

- `orientation=auto` elige portrait si el viewport es más alto que ancho; el usuario puede forzarla.
- ResizeObserver calcula `scale=min(hostWidth/logicalWidth,hostHeight/logicalHeight)`.
- Canvas centrado; controles debajo o sobre una zona segura independiente.
- Botones: iniciar, play/pause, seek, volumen, captions, orientación y pantalla completa.
- Teclado: espacio play/pause; flechas ±5 s; `m` mute; `c` captions.
- `prefers-reduced-motion` apaga temblor y reduce cámara solo si la opción es `system`; la timeline y audio no cambian.
- `aria-live=polite` anuncia speaker y caption sin repetir cada frame.
- Mantener contraste y focus visibles.
- Al desmontar: cancelar animation frame, audio y ResizeObserver.
