# Catálogo total de efectos

## Índice

1. Pipeline activo
2. Cámara
3. Temblor
4. Composición
5. Transiciones
6. Audio y velocidad
7. Código inactivo

## 1. Pipeline activo

El renderer histórico crea un JPEG aplanado de 1920×1080, lo transforma en clip de 25 FPS, aplica temblor, después cámara y finalmente audio. Fondo, sprite y texto se mueven juntos.

## 2. Cámara

| Código | Resultado legado | Frecuencia observada |
|---|---|---:|
| `PP` | Sprite grande y zoom centrado. El objetivo se ignora para la cámara. | 473 |
| `ZO` | Zoom negativo y paneo según lado del speaker. | 133 |
| `PA-D` | Se convierte a zoom-in suave; no usa `D`. | 104 |
| `PA-I` | Idéntico a `PA-D`; no usa `I`. | 96 |
| `ES` | Sin cámara; conserva temblor global. | 81 |
| `ZI` | Zoom-in y paneo según lado del speaker. | 72 |
| `TI-B` | Traslada contenido hacia arriba. | 17 |
| `TI-A` | Traslada contenido hacia abajo. | 14 |

Todos comienzan en `t=0`, no tienen easing y usan intensidad 1.0 si se omite o es no positiva.

## 3. Temblor

Parámetros activos:

- 25 FPS y seed igual al índice de frame `floor(t*25)`.
- Canny bajo 30, alto 120.
- Desplazamiento aleatorio uniforme ±14 px, multiplicado por 1.1.
- Kernel 10 corregido a 11 por requerir impar.
- Remap bilinear con borde reflejado dentro del temblor.
- Blur gaussiano 3×3.
- Máscara de bordes normalizada y blur 3×3.
- Mezcla máxima 0.8 entre frame original y desplazado.

El navegador genera el edge map en build con Python/OpenCV y usa shader WebGL. La cámara usa clamp-to-edge; el shader de temblor usa mirror/repeat para igualar `BORDER_REFLECT`.

## 4. Composición

- Landscape lógico: 1920×1080 a partir de fondos 960×540.
- Portrait legado: componer lateralmente en 1920×1080 con variantes `(3)` a `(5)`, rotar assets/texto 270° y el resultado final 90°.
- Reflejar sprites horizontalmente en layouts `H C` y `H D`; verticalmente en `V C` y `V D` según reglas de layout.
- Texto Nanum Gothic ExtraBold, negro, sin burbuja, wrapping por ancho medido.
- `Bip bip` se presenta como `%!&$# >:(`.
- `PP` selecciona coordenadas `G` antes del zoom.

## 5. Transiciones

- Elegir fondo entre 23 WebP mediante seed.
- Nueve pasadas `PIL.ImageFilter.BLUR` en legado.
- Aplicar resize-cover y crop centrado.
- Dividir texto a máximo 3 palabras o 17 caracteres por línea.
- Ajustar cada línea al ancho menos 40 px.
- Blanco, centrado horizontal y vertical, separación 20 px.
- Duración 1900 ms, música gain 0.5 y fade-out 500 ms.
- Consejo final histórico: 40 ms; se conserva solo en legacy.

## 6. Audio y velocidad

- Fondo de escena gain 0.15 y 44.1 kHz.
- Silenciar fondo durante SFX/onomatopeya.
- La llamada actual fija `speed_factor=1`; el default 1.05 está inactivo.
- Ending sin aceleración efectiva.

## 7. Código inactivo

Documentar, pero no incluir por defecto: blanco y negro, sepia, contorno, sharpen, emboss, inversión, brillo ×1.5, contraste ×1.5 y edge-enhance. Solo `difuso` participa en transiciones.
