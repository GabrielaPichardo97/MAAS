# Contrato de audio

## Índice

1. Tipos
2. TTS legado
3. Mezcla
4. Assets ausentes

## 1. Tipos

- `voice`: diálogo sintetizado o grabado.
- `sfx`: onomatopeya/efecto puntual.
- `music`: fondo de escena o transición.
- `ending`: audio incluido en el cierre audiovisual.

Cada cue referencia `assetId`, `gain`, `fadeInMs` y `fadeOutMs`. El asset manifest aporta `durationMs`.

## 2. TTS legado

Referencia histórica para comparación, no obligación del producto:

- Modelo `eleven_multilingual_v2`.
- Stability 0.78.
- Similarity boost 0.91.
- Style 0.0.
- Speaker boost activo.
- Un archivo por línea de diálogo.

La espera artificial de seis segundos no forma parte del resultado y se elimina. Cachear por SHA-256 de proveedor, modelo, voz, settings, idioma y texto normalizado.

## 3. Mezcla

`legacy-v1`: voz/SFX gain 1, música de escena 0.15, transición 0.5, fade-out de transición 500 ms, sample rate objetivo 44100. La música se silencia durante SFX y reinicia desde cero en cada escena.

`canonical-v1`: música continua por episodio y ducking configurable, default -12 dB durante voz/SFX.

## 4. Assets ausentes

- Voz ausente: error en publicación; en preview mostrar texto y silencio explícito.
- SFX ausente: error si la clave fue solicitada.
- Música ausente: warning si el perfil permite silencio.
- Nunca buscar por “parecido” en nombres durante reproducción.
