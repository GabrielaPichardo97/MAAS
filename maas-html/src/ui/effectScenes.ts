import type { EffectCatalogEntry } from "../types";

export type SceneMood = "office" | "night" | "stage" | "memory" | "digital" | "street";

export interface EffectScene {
  title: string;
  location: string;
  dialogue: string;
  leftActor: string;
  rightActor: string;
  prop: string;
  mood: SceneMood;
}

export const EFFECT_SCENES: Record<string, EffectScene> = {
  "transition.cut.continuity.clean.v1.0.0": { title: "La decisión", location: "Oficina · 08:42", dialogue: "Cortamos aquí. Lo demás sobra.", leftActor: "Pato", rightActor: "Cactus", prop: "CONTRATO", mood: "office" },
  "transition.match-cut.continuity.visual-rhyme.v1.0.0": { title: "La misma luna", location: "Azotea / Andén", dialogue: "Parece otra ciudad, pero es la misma noche.", leftActor: "Kiwi", rightActor: "Coneja", prop: "LUNA", mood: "night" },
  "transition.jump-cut.compression.fragmented.v1.0.0": { title: "Lunes en treinta segundos", location: "Cubículo · Todo el día", dialogue: "Café. Correo. Reunión. Café otra vez.", leftActor: "Pato", rightActor: "Roca", prop: "09:00 → 18:00", mood: "office" },
  "transition.morph-cut.continuity.interview-clean.v1.0.0": { title: "La pausa imposible", location: "Sala de entrevistas", dialogue: "Nunca dudé… bueno, casi nunca.", leftActor: "Gata", rightActor: "Entrevistador", prop: "REC", mood: "stage" },
  "transition.whip-pan.energy.directional.v1.0.0": { title: "El último vagón", location: "Estación · 23:58", dialogue: "¡Corre, todavía alcanzamos!", leftActor: "Conejo", rightActor: "Pata", prop: "TREN", mood: "street" },
  "transition.glitch.disruption.digital.v1.0.0": { title: "Señal intrusa", location: "Centro de monitoreo", dialogue: "Eso no estaba en la transmisión.", leftActor: "Cactus", rightActor: "Operadora", prop: "ERROR 07", mood: "digital" },
  "transition.split-screen.comparison.clean.v1.0.0": { title: "Dos versiones del plan", location: "Casa / Oficina", dialogue: "Tú improvisa. Yo llevo una lista.", leftActor: "Pato", rightActor: "Pata", prop: "VS", mood: "office" },
  "motion.push-in.emphasis.subtle.v1.0.0": { title: "La letra pequeña", location: "Oficina · Mediodía", dialogue: "Aquí dice que el jefe paga la cena.", leftActor: "Cactus", rightActor: "Pato", prop: "CLÁUSULA 9", mood: "office" },
  "motion.ken-burns.exposition.documentary.v1.0.0": { title: "El mapa de la fuga", location: "Archivo municipal · 1978", dialogue: "Todo empezó con una línea dibujada a lápiz.", leftActor: "Narradora", rightActor: "Roca", prop: "MAPA", mood: "memory" },
  "motion.virtual-dolly.reveal.parallax.v1.0.0": { title: "Detrás de la puerta", location: "Pasillo norte", dialogue: "La oficina siempre fue más grande por dentro.", leftActor: "Kiwi", rightActor: "Conejo", prop: "PUERTA 7", mood: "night" },
  "motion.camera-3d.world-building.parallax.v1.0.0": { title: "Ciudad de cartón", location: "Maqueta central", dialogue: "Si mueves una calle, cambia toda la historia.", leftActor: "Arquitecta", rightActor: "Cactus", prop: "MAQUETA", mood: "stage" },
  "motion.rack-focus.attention.depth-shift.v1.0.0": { title: "La taza y la llave", location: "Cafetería", dialogue: "No mires el café. Mira lo que dejé detrás.", leftActor: "Pata", rightActor: "Pato", prop: "LLAVE", mood: "office" },
  "motion.stabilize.clarity.smooth.v1.0.0": { title: "Reporte desde la tormenta", location: "Avenida central", dialogue: "Seguimos al aire, aunque todo se mueva.", leftActor: "Reportera", rightActor: "Camarógrafo", prop: "EN VIVO", mood: "street" },
  "motion.camera-shake.impact.decay.v1.0.0": { title: "El archivo cayó", location: "Sótano de datos", dialogue: "Eso no fue un trueno.", leftActor: "Gata", rightActor: "Rinoceronte", prop: "¡BUM!", mood: "night" },
  "motion.motion-blur.continuity.directional.v1.0.0": { title: "Mensajería urgente", location: "Cruce Reforma", dialogue: "Entrega primero, pregunta después.", leftActor: "Kiwi", rightActor: "Mensajero", prop: "PAQUETE", mood: "street" },
  "time.remap.rhythm.variable.v1.0.0": { title: "Cinco minutos prestados", location: "Elevador", dialogue: "El tiempo corre distinto entre pisos.", leftActor: "Pato", rightActor: "Relojera", prop: "00:05", mood: "digital" },
  "time.speed-ramp.energy.snap.v1.0.0": { title: "La carrera del café", location: "Cafetería / Sala", dialogue: "Si llega caliente, ganamos.", leftActor: "Cactus", rightActor: "Pata", prop: "CAFÉ", mood: "street" },
  "time.freeze-frame.emphasis.hold.v1.0.0": { title: "Exactamente ahí", location: "Recepción", dialogue: "Ese fue el segundo en que entendió todo.", leftActor: "Narrador", rightActor: "Conejo", prop: "PAUSA", mood: "stage" },
  "time.reverse.stylization.circular.v1.0.0": { title: "Devuelve el pastel", location: "Fiesta de oficina", dialogue: "Retrocede. Nadie tiene que saberlo.", leftActor: "Pato", rightActor: "Gata", prop: "PASTEL", mood: "memory" },
  "time.trails.energy.decay.v1.0.0": { title: "Ensayo de medianoche", location: "Escenario vacío", dialogue: "Cada paso deja otro bailarín atrás.", leftActor: "Bailarina", rightActor: "Kiwi", prop: "ECO", mood: "stage" },
  "time.flash-frame.impact.single.v1.0.0": { title: "La foto prohibida", location: "Archivo oscuro", dialogue: "Sólo vimos el rostro durante un instante.", leftActor: "Coneja", rightActor: "Roca", prop: "FLASH", mood: "night" },
  "time.punch-edit.impact.snap.v1.0.0": { title: "Sello de aprobado", location: "Ventanilla 4", dialogue: "Tres semanas de espera. Un golpe de tinta.", leftActor: "Pata", rightActor: "Funcionario", prop: "APROBADO", mood: "office" },
  "compositing.chroma-key.environment.clean.v1.0.0": { title: "Clima desde Marte", location: "Estudio verde", dialogue: "Hoy habrá polvo rojo con probabilidad de meteoritos.", leftActor: "Presentadora", rightActor: "Robot", prop: "MARTE", mood: "digital" },
  "compositing.rotoscope.isolation.object-matte.v1.0.0": { title: "La silueta fugitiva", location: "Museo nocturno", dialogue: "Recorta al sospechoso. Deja la sombra.", leftActor: "Detective", rightActor: "Gata", prop: "SILUETA", mood: "night" },
  "compositing.blend.layering.clean.v1.0.0": { title: "Planos superpuestos", location: "Mesa de estrategia", dialogue: "La ruta, el clima y el riesgo: todo a la vez.", leftActor: "Cactus", rightActor: "Kiwi", prop: "CAPAS", mood: "digital" },
  "compositing.match-move.integration.planar-3d.v1.0.0": { title: "El anuncio que camina", location: "Calle principal", dialogue: "El mensaje sigue la pared, incluso cuando corremos.", leftActor: "Pato", rightActor: "Pata", prop: "TRACK 01", mood: "street" },
  "graphics.kinetic-type.emphasis.sequenced.v1.0.0": { title: "Palabras con prisa", location: "Cabina de radio", dialogue: "HOY. AQUÍ. AHORA.", leftActor: "Locutora", rightActor: "Cactus", prop: "AHORA", mood: "stage" },
  "graphics.lower-third.identification.clean.v1.0.0": { title: "La experta inesperada", location: "Laboratorio", dialogue: "Dra. Pata, especialista en problemas imposibles.", leftActor: "Pata", rightActor: "Entrevistador", prop: "DRA. PATA", mood: "office" },
  "stylize.color-grade.coherence.clean.v1.0.0": { title: "Dos amaneceres", location: "Parque · 06:10", dialogue: "El día era frío, pero el recuerdo no.", leftActor: "Coneja", rightActor: "Kiwi", prop: "AMANECER", mood: "memory" },
  "stylize.light-leak.atmosphere.film.v1.0.0": { title: "Verano en Super 8", location: "Parque · 1996", dialogue: "La cámara falló justo cuando fuimos felices.", leftActor: "Pato", rightActor: "Pata", prop: "RECUERDO", mood: "memory" },
  "stylize.lens-flare.hero.optical.v1.0.0": { title: "Entrada triunfal", location: "Hangar al amanecer", dialogue: "No llegó tarde. Esperó la luz correcta.", leftActor: "Rinoceronte", rightActor: "Operadora", prop: "HÉROE", mood: "stage" },
  "stylize.particles.atmosphere.dynamic.v1.0.0": { title: "Nieve en la oficina", location: "Piso 12", dialogue: "El aire acondicionado se tomó muy en serio diciembre.", leftActor: "Cactus", rightActor: "Gata", prop: "NIEVE", mood: "office" },
  "stylize.glitch.disruption.retro-tv.v1.0.0": { title: "Canal 0", location: "Televisor abandonado", dialogue: "La transmisión conoce nuestros nombres.", leftActor: "Conejo", rightActor: "Señal", prop: "NO SIGNAL", mood: "digital" },
  "stylize.audio-reactive.rhythm.pulse.v1.0.0": { title: "La pared escucha", location: "Club subterráneo", dialogue: "Cada bajo enciende otra parte del mural.", leftActor: "DJ Kiwi", rightActor: "Pata", prop: "BPM 128", mood: "stage" },
};

const FALLBACK_SCENE: EffectScene = { title: "Prueba de cámara", location: "Set MAAS", dialogue: "Una escena nueva espera dirección.", leftActor: "A", rightActor: "B", prop: "TAKE 1", mood: "stage" };

export function sceneForEffect(effect: EffectCatalogEntry): EffectScene {
  return EFFECT_SCENES[effect.id] ?? FALLBACK_SCENE;
}
