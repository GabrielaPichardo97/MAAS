# Layouts observados

## Índice

1. Orientaciones
2. Fondos
3. Personajes
4. Texto
5. Reflejos

## 1. Orientaciones

- Landscape: stage 1920×1080.
- Portrait legado: componer un stage lateral 1920×1080 con fondos V y rotar el contenedor completo 90° para salida 1080×1920.
- Usar `contain` y barras del color de fondo; no estirar.

## 2. Fondos

| Speaker/layout | Landscape | Portrait lateral |
|---|---|---|
| centro | `Fondos de personajes.png` (`H C`) | `(3).png` (`V C`) |
| izquierda | `(1).png` (`H D`) | `(4).png` (`V D`) |
| derecha | `(2).png` (`H I`) | `(5).png` (`V I`) |

## 3. Personajes a 1920×1080

| Layout | Normal | Grande `PP` |
|---|---|---|
| H C izquierda | 1144,364,854,854 | 92,-62,1500,1500 |
| H C derecha | 120,364,854,854 | 92,-62,1500,1500 |
| H D | 300,308,854,854 | 92,-62,1500,1500 |
| H I | 968,308,854,854 | 620,-62,1500,1500 |
| V C/V D | 252,186,814,814 | -136,-150,1382,1382 |
| V I | 170,234,692,692 | -310,-182,1474,1474 |

Formato: `left,top,width,height`. Las posiciones pueden salir del lienzo y deben recortarse.

## 4. Texto

- H C: 762,12; ancho máximo 500; fuente 80.
- H D: 1054,98; ancho 500; fuente 80.
- H I: 348,70; ancho 500; fuente 84.
- V C/V D/V I: 1092,232; ancho 600; fuente 84; rotación 270°.
- Nanum Gothic ExtraBold, negro, sin fondo.
- En legacy, `PP` no cambia el layout del texto.

## 5. Reflejos

- `H C`: reflejar el último sprite horizontalmente.
- `H D`: reflejar horizontalmente.
- `V C` y `V D`: reflejar verticalmente antes de la rotación final.
- Seleccionar mirada `left` como base y aplicar fallback explícito si falta.
