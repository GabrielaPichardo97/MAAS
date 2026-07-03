# Catálogo canonical-v2 de efectos MAAS

Fuente de verdad: `effects-catalog.json`. Los IDs son exactos y no resuelven versiones implícitas.

## Niveles de soporte

- `native`: ejecución directa en MAAS web.
- `approximation`: aproximación 2.5D o visual documentada.
- `input-assisted`: requiere material o metadata declarada.
- `preprocessed`: consume un artefacto calculado fuera del navegador.

## transition

### Corte, fade y disolución

- **ID:** `transition.cut.continuity.clean.v1.0.0`
- **Qué hace:** Cambia de plano directamente o mezcla opacidad durante un intervalo configurable.
- **Mejor momento:** Continuidad limpia, respiración o cambio de escena sin llamar la atención.
- **Evitar:** Un beat de impacto necesita un corte seco; La mezcla crea una imagen confusa.
- **Soporte:** `native` · costo `low` · móvil `sí`.
- **Movimiento reducido:** `preserve` · riesgo fotosensible `none`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `mode` (enum, cut, fade, dissolve); default `cut`.
  - `durationMs` (integer, 0..2000); default `0`.
### Match cut

- **ID:** `transition.match-cut.continuity.visual-rhyme.v1.0.0`
- **Qué hace:** Alinea dos planos por forma, posición, movimiento o significado antes del corte.
- **Mejor momento:** Cambios elegantes de escena, revelaciones o humor con una rima visual real.
- **Evitar:** No existe una correspondencia visual verificable.
- **Soporte:** `input-assisted` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `none`.
- **Requisitos:** `matchAnchors`.
- **Fallback:** `transition.cut.continuity.clean.v1.0.0`.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `matchType` (enum, shape, motion, graphic, theme); default `shape`.
  - `tolerance` (number, 0..1); default `0.8`.
### Jump cut

- **ID:** `transition.jump-cut.compression.fragmented.v1.0.0`
- **Qué hace:** Salta tiempo o posición dentro de una continuidad inmediata para hacer visible la edición.
- **Mejor momento:** Compresión temporal, comedia, ansiedad, vlog o pensamiento fragmentado.
- **Evitar:** Se necesita continuidad invisible; El salto rompe información espacial necesaria.
- **Soporte:** `native` · costo `low` · móvil `sí`.
- **Movimiento reducido:** `preserve` · riesgo fotosensible `low`.
- **Requisitos:** ninguno.
- **Fallback:** `transition.cut.continuity.clean.v1.0.0`.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `skipMs` (integer, 40..10000); default `400`.
### Morph cut

- **ID:** `transition.morph-cut.continuity.interview-clean.v1.0.0`
- **Qué hace:** Interpola dos fragmentos faciales semejantes para ocultar la eliminación de una pausa.
- **Mejor momento:** Entrevistas y talking heads con postura, luz y fondo casi idénticos.
- **Evitar:** Giro rápido de cabeza; Manos cruzan el rostro; Cambia la iluminación o el fondo.
- **Soporte:** `preprocessed` · costo `low` · móvil `sí`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `none`.
- **Requisitos:** `morphClip`.
- **Fallback:** `transition.cut.continuity.clean.v1.0.0`.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `durationMs` (integer, 240..800); default `480`.
### Whip pan

- **ID:** `transition.whip-pan.energy.directional.v1.0.0`
- **Qué hace:** Oculta el corte dentro de una traslación rápida con blur direccional continuo.
- **Mejor momento:** Acción, comedia, viaje y cambios de lugar con dirección compatible.
- **Evitar:** Hay texto que debe leerse; La pieza exige elegancia estática.
- **Soporte:** `native` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `low`.
- **Requisitos:** ninguno.
- **Fallback:** `transition.cut.continuity.clean.v1.0.0`.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `direction` (enum, left, right, up, down); default `right`.
  - `blurPx` (number, 0..180); default `80`.
  - `durationMs` (integer, 120..600); default `280`.
### Transición glitch

- **ID:** `transition.glitch.disruption.digital.v1.0.0`
- **Qué hace:** Corrompe brevemente bloques, canales RGB y scanlines durante el cambio de plano.
- **Mejor momento:** Tecnología, señal fallando, memoria degradada o ruptura deliberada.
- **Evitar:** Drama íntimo; Marca institucional sobria; Fotosensibilidad sin modo seguro.
- **Soporte:** `native` · costo `high` · móvil `no`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `medium`.
- **Requisitos:** ninguno.
- **Fallback:** `transition.cut.continuity.clean.v1.0.0`.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `rgbOffsetPx` (number, 0..20); default `6`.
  - `noise` (number, 0..1); default `0.25`.
  - `durationMs` (integer, 80..600); default `240`.
### Split-screen

- **ID:** `transition.split-screen.comparison.clean.v1.0.0`
- **Qué hace:** Muestra dos o más encuadres simultáneos con márgenes y sincronización controlados.
- **Mejor momento:** Comparación, simultaneidad, llamadas, antes/después o tutorial.
- **Evitar:** Pantalla móvil con demasiados paneles; La emoción necesita intimidad.
- **Soporte:** `native` · costo `medium` · móvil `no`.
- **Movimiento reducido:** `preserve` · riesgo fotosensible `none`.
- **Requisitos:** ninguno.
- **Fallback:** `transition.cut.continuity.clean.v1.0.0`.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `panes` (integer, 2..6); default `2`.
  - `gapPct` (number, 0..8); default `2`.

## motion

### Push-in

- **ID:** `motion.push-in.emphasis.subtle.v1.0.0`
- **Qué hace:** Escala progresivamente el encuadre hacia un rostro, objeto o texto.
- **Mejor momento:** Pensamiento, revelación, frase importante o cierre emocional.
- **Evitar:** La imagen no resiste recorte; Ya existe movimiento fuerte de cámara.
- **Soporte:** `native` · costo `low` · móvil `sí`.
- **Movimiento reducido:** `reduce` · riesgo fotosensible `none`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `scaleEnd` (number, 0.75..1.5); default `1.1`.
  - `easing` (enum, linear, ease-in, ease-out, ease-in-out); default `ease-in-out`.
### Panorámica / Ken Burns

- **ID:** `motion.ken-burns.exposition.documentary.v1.0.0`
- **Qué hace:** Interpola entre dos regiones del frame para recorrer una imagen fija.
- **Mejor momento:** Fotografía, archivo, mapas, documental y B-roll explicativo.
- **Evitar:** Sustituye repetidamente cobertura viva; El recorrido no tiene foco claro.
- **Soporte:** `native` · costo `low` · móvil `sí`.
- **Movimiento reducido:** `reduce` · riesgo fotosensible `none`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `endX` (number, -1..1); default `0.1`.
  - `endY` (number, -1..1); default `0`.
  - `scaleEnd` (number, 1..1.5); default `1.12`.
### Dolly virtual

- **ID:** `motion.virtual-dolly.reveal.parallax.v1.0.0`
- **Qué hace:** Simula profundidad mediante escalas y desplazamientos distintos en capas 2.5D.
- **Mejor momento:** Producto, títulos integrados, maquetas y reveals controlados.
- **Evitar:** No existen capas de profundidad; El movimiento parece un zoom plano.
- **Soporte:** `approximation` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `none`.
- **Requisitos:** ninguno.
- **Fallback:** `motion.push-in.emphasis.subtle.v1.0.0`.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `depth` (number, 0..1); default `0.35`.
  - `travel` (number, -1..1); default `0.25`.
### Cámara 3D / parallax

- **ID:** `motion.camera-3d.world-building.parallax.v1.0.0`
- **Qué hace:** Aproxima una cámara 3D mediante capas 2.5D, profundidad declarada y punto de interés.
- **Mejor momento:** World-building, títulos espaciales y hero shots con profundidad separada.
- **Evitar:** No hay paralaje; El solve o la profundidad son ambiguos.
- **Soporte:** `approximation` · costo `high` · móvil `no`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `low`.
- **Requisitos:** ninguno.
- **Fallback:** `motion.virtual-dolly.reveal.parallax.v1.0.0`.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `depth` (number, 0..1); default `0.5`.
  - `rollDeg` (number, -15..15); default `0`.
### Rack focus

- **ID:** `motion.rack-focus.attention.depth-shift.v1.0.0`
- **Qué hace:** Desplaza el foco aparente entre capas usando máscaras y desenfoque graduado.
- **Mejor momento:** Cambiar atención entre primer plano, objeto, rostro o fondo.
- **Evitar:** Texto pequeño; Material comprimido; No existe separación de capas.
- **Soporte:** `approximation` · costo `high` · móvil `no`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `none`.
- **Requisitos:** ninguno.
- **Fallback:** `motion.push-in.emphasis.subtle.v1.0.0`.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `blurPx` (number, 0..80); default `18`.
  - `focusTo` (enum, foreground, subject, background); default `subject`.
### Estabilización

- **ID:** `motion.stabilize.clarity.smooth.v1.0.0`
- **Qué hace:** Consume un track preprocesado de transformación para compensar movimiento no deseado.
- **Mejor momento:** B-roll, documental, dron o handheld que distrae.
- **Evitar:** El handheld expresa el POV; La corrección produce wobble.
- **Soporte:** `preprocessed` · costo `low` · móvil `sí`.
- **Movimiento reducido:** `preserve` · riesgo fotosensible `none`.
- **Requisitos:** `stabilizationTrack`.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `strength` (number, 0..1); default `0.5`.
### Camera shake

- **ID:** `motion.camera-shake.impact.decay.v1.0.0`
- **Qué hace:** Añade desplazamiento y rotación pseudoaleatorios con frecuencia y caída deterministas.
- **Mejor momento:** Golpes, horror, trailers, drops musicales y urgencia.
- **Evitar:** Educación; Producto premium; Movimiento reducido.
- **Soporte:** `native` · costo `low` · móvil `sí`.
- **Movimiento reducido:** `disable` · riesgo fotosensible `medium`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `amplitudePx` (number, 0..40); default `8`.
  - `frequencyHz` (number, 1..20); default `8`.
  - `decayMs` (integer, 100..1500); default `500`.
### Motion blur

- **ID:** `motion.motion-blur.continuity.directional.v1.0.0`
- **Qué hace:** Simula integración temporal mediante blur direccional asociado a la velocidad visual.
- **Mejor momento:** Ramps, whip pans, títulos rápidos y movimientos con strobing.
- **Evitar:** Ya existe blur real; El texto debe permanecer nítido.
- **Soporte:** `native` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `disable` · riesgo fotosensible `low`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `blurPx` (number, 0..120); default `24`.
  - `angleDeg` (number, -180..180); default `0`.
### Wobble de recorte

- **ID:** `motion.cutout-wobble.presence.puppet-idle.v1.0.0`
- **Qué hace:** Anima un personaje como una pieza física recortada mediante poses sostenidas, microasentamiento y movimiento anclado a los pies.
- **Mejor momento:** Planos de diálogo, reacciones contenidas y escenas artesanales que necesitan vida sin cambiar de pose.
- **Evitar:** El personaje ya tiene animación corporal; La actuación exige inmovilidad absoluta; Se aplicaría a texto o interfaz.
- **Soporte:** `native` · costo `low` · móvil `sí`.
- **Movimiento reducido:** `disable` · riesgo fotosensible `none`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** `speaker`; default `speaker`.
- **Parámetros:**
  - `travelPx` (number, 0..18); default `4`.
  - `rotationDeg` (number, 0..3); default `0.45`.
  - `rateFps` (integer, 2..12); default `6`.

## time

### Time remapping

- **ID:** `time.remap.rhythm.variable.v1.0.0`
- **Qué hace:** Mapea el tiempo de salida a una curva de tiempo fuente con interpolación configurable.
- **Mejor momento:** Manipular percepción temporal o sincronizar acciones con beats.
- **Evitar:** Diálogo sin plan de audio; El flujo óptico produciría artefactos.
- **Soporte:** `native` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `low`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `speed` (number, -4..20); default `1`.
  - `preservePitch` (boolean, boolean); default `True`.
### Speed ramp

- **ID:** `time.speed-ramp.energy.snap.v1.0.0`
- **Qué hace:** Interpola gradualmente entre velocidades para acelerar o desacelerar alrededor de un gesto.
- **Mejor momento:** Acción, deporte, dance edit, reveal y drop musical.
- **Evitar:** No existe dirección física clara; Cabello o agua generan artefactos.
- **Soporte:** `native` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `medium`.
- **Requisitos:** ninguno.
- **Fallback:** `time.remap.rhythm.variable.v1.0.0`.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `peakSpeed` (number, 1..20); default `4`.
  - `rampMs` (integer, 80..1000); default `320`.
### Freeze frame

- **ID:** `time.freeze-frame.emphasis.hold.v1.0.0`
- **Qué hace:** Mantiene un frame para detener la acción y abrir espacio a énfasis o texto.
- **Mejor momento:** Punchline, introducción de personaje, análisis, moda o producto.
- **Evitar:** La emoción depende de continuidad orgánica.
- **Soporte:** `native` · costo `low` · móvil `sí`.
- **Movimiento reducido:** `preserve` · riesgo fotosensible `none`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `holdMs` (integer, 120..10000); default `800`.
### Reversa temporal

- **ID:** `time.reverse.stylization.circular.v1.0.0`
- **Qué hace:** Reproduce un intervalo hacia atrás con rampas opcionales de entrada y salida.
- **Mejor momento:** Ironía, memoria, explicación de causa o estructura circular.
- **Evitar:** Continuidad naturalista; Audio verbal sin tratamiento.
- **Soporte:** `native` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `low`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `speed` (number, 0.1..4); default `1`.
### Trails

- **ID:** `time.trails.energy.decay.v1.0.0`
- **Qué hace:** Acumula frames previos con opacidad decreciente para producir estelas.
- **Mejor momento:** Música, sci-fi, energía y secuencias abstractas.
- **Evitar:** Información factual; La estela oculta el sujeto.
- **Soporte:** `native` · costo `high` · móvil `no`.
- **Movimiento reducido:** `disable` · riesgo fotosensible `medium`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `frames` (integer, 2..16); default `4`.
  - `decay` (number, 0..1); default `0.65`.
### Flash frame

- **ID:** `time.flash-frame.impact.single.v1.0.0`
- **Qué hace:** Inserta un destello único de color durante uno o pocos frames.
- **Mejor momento:** Hit musical, moda, trailer o impacto físico puntual.
- **Evitar:** Fotosensibilidad; Tono institucional; Narrativa contemplativa.
- **Soporte:** `native` · costo `low` · móvil `sí`.
- **Movimiento reducido:** `disable` · riesgo fotosensible `high`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `color` (color, color); default `#ffffff`.
  - `durationMs` (integer, 40..160); default `40`.
  - `opacity` (number, 0..1); default `0.8`.
### Punch edit

- **ID:** `time.punch-edit.impact.snap.v1.0.0`
- **Qué hace:** Combina pre-hold, micro-ramp, blur y corte en el gesto crítico.
- **Mejor momento:** Golpe, dance edit, anuncio corto o acción comprimida.
- **Evitar:** Más de tres impactos consecutivos; No existe un gesto crítico.
- **Soporte:** `native` · costo `high` · móvil `no`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `medium`.
- **Requisitos:** ninguno.
- **Fallback:** `time.speed-ramp.energy.snap.v1.0.0`.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `peakSpeed` (number, 2..8); default `4`.
  - `blurBoost` (number, 0..1); default `0.35`.

## compositing

### Chroma key

- **ID:** `compositing.chroma-key.environment.clean.v1.0.0`
- **Qué hace:** Convierte un color dominante en alfa y controla tolerancia, spill y bordes.
- **Mejor momento:** Sets virtuales, explainers, pantallas y contenido de marca.
- **Evitar:** Spill severo; Sombras duras; Compresión que destruye el borde.
- **Soporte:** `input-assisted` · costo `high` · móvil `no`.
- **Movimiento reducido:** `preserve` · riesgo fotosensible `none`.
- **Requisitos:** `keyedSource`.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `keyColor` (color, color); default `#00ff00`.
  - `tolerance` (number, 0..1); default `0.25`.
  - `spill` (number, 0..1); default `0.5`.
### Rotoscopía / object matte

- **ID:** `compositing.rotoscope.isolation.object-matte.v1.0.0`
- **Qué hace:** Consume un matte animado para aislar un sujeto sin chroma.
- **Mejor momento:** Blur selectivo, reemplazo de fondo, relighting o texto detrás del sujeto.
- **Evitar:** El matte no cubre oclusiones; Regrabar cuesta menos que limpiar.
- **Soporte:** `preprocessed` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `preserve` · riesgo fotosensible `none`.
- **Requisitos:** `objectMatte`.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `featherPx` (number, 0..50); default `3`.
  - `expansionPx` (number, -20..20); default `0`.
### Compositing y blend modes

- **ID:** `compositing.blend.layering.clean.v1.0.0`
- **Qué hace:** Superpone capas con alfa, orden y modos de fusión definidos.
- **Mejor momento:** Overlays, HUD, texturas, dobles y VFX simples.
- **Evitar:** Luma y color no están integrados; El stack pierde legibilidad.
- **Soporte:** `native` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `preserve` · riesgo fotosensible `none`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `blendMode` (enum, normal, add, multiply, screen, overlay); default `screen`.
  - `opacity` (number, 0..1); default `0.65`.
### Match move / tracking

- **ID:** `compositing.match-move.integration.planar-3d.v1.0.0`
- **Qué hace:** Consume un track planar, de objeto o cámara para vincular una capa al plano.
- **Mejor momento:** Reemplazo de pantalla, carteles, callouts espaciales y set extensions.
- **Evitar:** No hay features confiables; Oclusiones sin matte.
- **Soporte:** `preprocessed` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `none`.
- **Requisitos:** `trackingData`.
- **Fallback:** `graphics.lower-third.identification.clean.v1.0.0`.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `trackType` (enum, planar, object, camera); default `planar`.

## graphics

### Tipografía cinética

- **ID:** `graphics.kinetic-type.emphasis.sequenced.v1.0.0`
- **Qué hace:** Anima texto por bloque, línea, palabra o carácter con entrada y salida secuenciadas.
- **Mejor momento:** Slogans, citas, lyric videos y explainers sociales.
- **Evitar:** Más de un gesto tipográfico compite en el mismo beat; El texto excede el tiempo de lectura.
- **Soporte:** `native` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `low`.
- **Requisitos:** ninguno.
- **Fallback:** `graphics.lower-third.identification.clean.v1.0.0`.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `unit` (enum, block, line, word, character); default `word`.
  - `staggerMs` (integer, 0..500); default `80`.
### Lower third / callout

- **ID:** `graphics.lower-third.identification.clean.v1.0.0`
- **Qué hace:** Presenta información breve en área segura y puede apuntar a una persona u objeto.
- **Mejor momento:** Identificación, educación, datos de producto y contexto.
- **Evitar:** El fondo es demasiado activo; La actuación requiere atención exclusiva.
- **Soporte:** `native` · costo `low` · móvil `sí`.
- **Movimiento reducido:** `fallback` · riesgo fotosensible `none`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `safeMarginPct` (number, 5..12); default `8`.
  - `enterMs` (integer, 0..1000); default `320`.

## stylize

### Color grade / LUT

- **ID:** `stylize.color-grade.coherence.clean.v1.0.0`
- **Qué hace:** Ajusta temperatura, contraste, saturación y matriz de color para empatar o estilizar.
- **Mejor momento:** Corregir y empatar planos antes de definir el look.
- **Evitar:** La LUT sustituye corrección primaria; Se recortan altas luces o negros.
- **Soporte:** `native` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `preserve` · riesgo fotosensible `none`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `contrast` (number, -1..1); default `0.15`.
  - `saturation` (number, 0..2); default `1.12`.
  - `tint` (number, -1..1); default `0.1`.
### Light leak / film burn

- **ID:** `stylize.light-leak.atmosphere.film.v1.0.0`
- **Qué hace:** Superpone fugas de luz suaves con mezcla screen o add.
- **Mejor momento:** Calidez, memoria, moda, nostalgia o acento de transición.
- **Evitar:** Se usa como muleta repetitiva; Oculta contraste o texto.
- **Soporte:** `native` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `reduce` · riesgo fotosensible `low`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `intensity` (number, 0..1); default `0.25`.
  - `color` (color, color); default `#ff8a4c`.
### Lens flare / light rays

- **ID:** `stylize.lens-flare.hero.optical.v1.0.0`
- **Qué hace:** Genera reflejos, halos y rayos enlazados a una posición luminosa.
- **Mejor momento:** Hero shot, sci-fi, automotriz, concierto o energía de marca.
- **Evitar:** Entrevista sobria; Se usa para disfrazar una imagen débil.
- **Soporte:** `native` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `reduce` · riesgo fotosensible `medium`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `intensity` (number, 0..1); default `0.2`.
  - `x` (number, 0..1); default `0.75`.
  - `y` (number, 0..1); default `0.25`.
### Partículas

- **ID:** `stylize.particles.atmosphere.dynamic.v1.0.0`
- **Qué hace:** Emite elementos con vida, velocidad, tamaño, turbulencia y gravedad controlados.
- **Mejor momento:** Polvo, nieve, chispas, UI espacial, títulos e impactos.
- **Evitar:** No coinciden luz y profundidad; Las partículas genéricas compiten con el sujeto.
- **Soporte:** `native` · costo `high` · móvil `no`.
- **Movimiento reducido:** `disable` · riesgo fotosensible `low`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `rate` (number, 0..500); default `40`.
  - `lifeMs` (integer, 100..10000); default `1800`.
  - `gravity` (number, -2..2); default `0.2`.
### Glitch / retro TV

- **ID:** `stylize.glitch.disruption.retro-tv.v1.0.0`
- **Qué hace:** Mantiene interferencia, scanlines, ruido, jitter y separación RGB durante el plano.
- **Mejor momento:** Pantalla diegética, señal rota, identidad digital o memoria corrupta.
- **Evitar:** Pulcritud institucional; Duelo íntimo; Texto crítico.
- **Soporte:** `native` · costo `high` · móvil `no`.
- **Movimiento reducido:** `disable` · riesgo fotosensible `high`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `corruption` (number, 0..1); default `0.25`.
  - `rgbOffsetPx` (number, 0..20); default `4`.
  - `scanlines` (number, 0..1); default `0.35`.
### Visual audio-reactivo

- **ID:** `stylize.audio-reactive.rhythm.pulse.v1.0.0`
- **Qué hace:** Mapea amplitud o bandas de frecuencia a escala, opacidad, glow o partículas.
- **Mejor momento:** Lyric video, concierto, ID de canal y motion branding guiado por música.
- **Evitar:** La música no conduce el montaje; Falta smoothing y aparece jitter.
- **Soporte:** `input-assisted` · costo `high` · móvil `no`.
- **Movimiento reducido:** `disable` · riesgo fotosensible `medium`.
- **Requisitos:** `audioEnvelope`.
- **Fallback:** sin sustitución automática.
- **Objetivos:** contrato heredado.
- **Parámetros:**
  - `band` (enum, bass, mid, treble, full); default `full`.
  - `sensitivity` (number, 0..2); default `0.8`.
  - `smoothing` (number, 0..1); default `0.75`.
### Line boil

- **ID:** `stylize.line-boil.handmade.edge-jitter.v1.0.0`
- **Qué hace:** Redibuja ópticamente los contornos con una deformación UV cuantizada y guiada por bordes, conservando estables las masas de color.
- **Mejor momento:** Diálogo ilustrado, recuerdos, nervios contenidos y escenas con identidad dibujada a mano.
- **Evitar:** Hay texto pequeño dentro de la capa; La imagen necesita precisión geométrica; Se combina con wobble fuerte sobre el mismo personaje.
- **Soporte:** `native` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `reduce` · riesgo fotosensible `low`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** `speaker`, `background`; default `speaker`.
- **Parámetros:**
  - `amplitudePx` (number, 0..4); default `1.25`.
  - `rateFps` (integer, 2..15); default `8`.
  - `wavelengthPx` (number, 8..96); default `36`.
### Grano de papel vivo

- **ID:** `stylize.paper-grain.texture.living-fiber.v1.0.0`
- **Qué hace:** Hace respirar la superficie con grano monocromático y fibras procedurales, preservando alfa, color y legibilidad.
- **Mejor momento:** Fondos estáticos, secuencias de memoria y acabados artesanales usados como textura de soporte.
- **Evitar:** La compresión ya produce ruido; El acabado debe ser clínicamente limpio; La textura reduce contraste crítico.
- **Soporte:** `native` · costo `medium` · móvil `sí`.
- **Movimiento reducido:** `reduce` · riesgo fotosensible `low`.
- **Requisitos:** ninguno.
- **Fallback:** sin sustitución automática.
- **Objetivos:** `background`, `speaker`; default `background`.
- **Parámetros:**
  - `amount` (number, 0..0.25); default `0.06`.
  - `grainPx` (number, 1..12); default `3`.
  - `fiber` (number, 0..1); default `0.35`.
  - `rateFps` (integer, 1..12); default `6`.
