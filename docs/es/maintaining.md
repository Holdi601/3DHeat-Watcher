---
title: "Mantenimiento de estas páginas"
nav_order: 15
lang: es
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Mantenimiento de estas páginas {#maintaining-these-pages}

La lista de comprobación de cada versión. Las páginas deben decir lo que hace el código, leerse bien para un principiante, un
niño de 8 años y un profesional, y existir en todas las lenguas que admite el visor 3DHeat.

## Lista de comprobación de versión {#release-checklist}

1. **Regenerar las páginas generadas** a partir del código:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Antes de confirmar, los mismos comandos con `--check` deben terminar con 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Comparar las funciones desde la última versión.** `VERSION` contiene la versión; su etiqueta es `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Cada comando, opción, columna, salida o comportamiento nuevo recibe una línea en la página que lo cubre, y una
   línea en `CHANGELOG.md` bajo **Docs** que nombre esa página.

3. **Revisión independiente.** Alguien que no haya escrito el cambio lee las páginas modificadas - diagramas e
   imágenes incluidos - tres veces: como principiante (nunca ha usado una terminal), como niño de 8 años (¿dice el
   primer párrafo qué es y por qué, con palabras sencillas?) y como profesional (¿son las opciones, los valores por defecto y las
   columnas exactamente lo que hace el código?).

4. **Corregir lo que encontró la revisión.** Las imágenes miden como máximo unos 900 px de ancho, con texto de al menos 12 px
   tal como se muestra; los diagramas se generan a partir de `tools/diagrams/*.json` con `tools/flow2svg.py`. Los ejemplos usan
   solo nombres inventados (`de_x`, «Demo Valley», `<map>`): nunca un mapa, jugador, id de partida o cifra reales
   de archivos reales.

5. **Traducciones.** Cada página traducida guarda el hash de la fuente inglesa de la que procede.
   Vuelva a traducir las páginas cuyo hash de la fuente inglesa ha cambiado y haga revisar cada lengua de las tres mismas
   maneras (sencilla, principiante, profesional), incluidas las etiquetas de los diagramas.

6. **Publicar solo con el visto bueno del propietario.** Confirme en local; el propietario decide cuándo se hace público.

## Traducciones: los comandos {#translations-the-commands}

El sitio está traducido a las 40 lenguas del visor 3DHeat: el inglés en `docs/`, cada otra
lengua en `docs/<lang>/` con los mismos nombres de archivo. `tools/docs_i18n.py` lleva la contabilidad:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Traduzca solo lo que `todo` lista: deje el Markdown, los enlaces, el código y los nombres de archivos y de columnas tal cual,
traduzca los títulos y las descripciones de las imágenes, y use las palabras propias del visor 3DHeat para sus botones
y paneles (su carpeta `src/i18n/locales/<lang>/`). Las páginas de referencia generadas y las imágenes de terminal siguen
en inglés. En el sitio, una traducción desactualizada lo indica y enlaza la página en inglés; una página que falta
recurre al inglés. El menú de idioma de la cabecera y la redirección de la página de inicio según el idioma del navegador
vienen de `docs/_includes/`.
