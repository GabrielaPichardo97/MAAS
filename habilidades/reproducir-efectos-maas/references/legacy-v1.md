# Perfil `legacy-v1`

Sea `i` la intensidad, `t` los segundos y `p` el lado del speaker.

```text
base = 0.05
signX = -1 si p == izquierda; +1 en otro caso
```

| Código | `scale` | `x` como fracción del ancho | `y` como fracción del alto |
|---|---:|---:|---:|
| `ES` | 1 | 0 | 0 |
| `ZI` | `1 + base*i*t` | `signX*(base*i/2)*t` | 0 |
| `ZO` | `1 - base*i*t` | `signX*(base*i/2)*t` | 0 |
| `PA-I` | `1 + (base/2)*i*t` | `signX*(base*i/4)*t` | 0 |
| `PA-D` | Igual a `PA-I` | Igual a `PA-I` | 0 |
| `TI-A` | 1 | 0 | `+base*i*t` |
| `TI-B` | 1 | 0 | `-base*i*t` |
| `PP` | `1 + base*i*t` | 0 | 0 |

El resize del zoom es centrado y luego se recorta al tamaño original. El paneo ocurre antes del zoom. Una escala `<=0` es inválida y debe detener el build.

El temblor se aplica incluso a `ES`. Efectos desconocidos conservan únicamente temblor y emiten warning.
