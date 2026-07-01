# Perfil `canonical-v1`

- `ES`: scale 1, x/y 0 y temblor apagado salvo solicitud explícita.
- `ZI`/`ZO`: misma magnitud base, anchor centrado o personaje declarado.
- `PA-I`: cámara hacia izquierda; contenido se desplaza a la derecha.
- `PA-D`: cámara hacia derecha; contenido se desplaza a la izquierda.
- `TI-A`: cámara hacia arriba; contenido baja.
- `TI-B`: cámara hacia abajo; contenido sube.
- `PP`: exige target, usa layout `G` y zoom centrado en su bounding box.
- Clamp de escala mínimo 0.1.
- Las transformaciones siguen siendo lineales por compatibilidad; easing solo puede añadirse en un perfil futuro.
- Temblor, filtros y transición son propiedades explícitas del cue.
- Toda aleatoriedad usa `seed` del episodio más ID del cue.
