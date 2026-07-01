# Contrato de assets

## Índice

1. Tipos
2. Reglas por tipo
3. IDs y rutas
4. Fallbacks

## 1. Tipos

`background`, `sprite`, `transition`, `font`, `voice`, `sfx`, `music`, `ending`, `other`.

Cada entrada requiere `id`, `type`, `path`, `sha256`, `mimeType` y `allowedForPublish`. Dimensiones y duración son `null` si no pueden medirse sin error.

## 2. Reglas por tipo

- Fondos: lugar y variante/orientación declarados; actualmente seis PNG por lugar.
- Sprites: personaje, emoción y mirada; PNG con alpha preferido.
- Transiciones: imagen de origen, no PNG generado.
- Fuentes: licencia y archivo de licencia asociados.
- Audio: duración en ms, codec/MIME y categoría; la clave narrativa vive en un mapping separado.
- Ending: orientación obligatoria.

## 3. IDs y rutas

Generar IDs ASCII en minúsculas desde la ruta relativa y añadir ocho caracteres del SHA si existe colisión. Usar `/`, prohibir rutas absolutas y `..`. Los nombres originales permanecen en `path` y `aliases`.

## 4. Fallbacks

Los fallbacks son datos explícitos: emoción, mirada, orientación y lugar. No elegir “el primer archivo”. Detectar ciclos y terminar con error si no existe un asset autorizado.

## Overrides revisados

Pasar `--overrides metadata.json`; sus claves son asset IDs y solo puede cambiar procedencia, autor, licencia, autorización, aliases y clasificación visual:

```json
{
  "nanum-gothic-bold": {
    "source": "https://fonts.google.com/specimen/Nanum+Gothic",
    "author": "Sandoll Communications",
    "license": "OFL-1.1",
    "allowedForPublish": true
  }
}
```
