---
title: Antes de empezar
nav_order: 2
lang: "es"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Antes de empezar {#before-you-start}

¿Nuevo en la línea de comandos? Esta página te lleva de cero a un 3DHeat Watcher funcionando en unos
diez minutos. Escribes comandos en una *terminal*, una ventana donde escribes una línea y pulsas Intro.

## 1. Instalar Python {#install-python}

1. Descarga Python 3.10 o posterior desde <https://www.python.org/downloads/>.
2. Ejecuta el instalador. En la primera pantalla marca **Add python.exe to PATH**,
   y luego haz clic en **Install Now**.
3. Compruébalo: abre una terminal (paso 3) y escribe `python --version`. Deberías ver
   `Python 3.` y un número 10 o superior.

En Linux o macOS, Python suele estar ya instalado: usa `python3` donde estas páginas dicen `python`.

## 2. Conseguir 3DHeat Watcher {#get-3dheat-watcher}

Descarga el zip desde la
[página de versiones](https://github.com/Holdi601/3DHeat-Watcher/releases) y descomprímelo, por ejemplo en
`C:\Tools\3DHeat-Watcher`. (Si tienes Git, `git clone` también sirve.)

## 3. Abrir una terminal en esa carpeta {#open-a-terminal-in-that-folder}

- **Windows:** abre la carpeta en el Explorador de archivos, haz clic en la barra de direcciones, escribe
  `powershell` y pulsa Intro. Se abre una ventana azul o negra, ya en esa carpeta.
- **macOS / Linux:** abre *Terminal* y escribe `cd ` (con un espacio), arrastra la carpeta a la ventana,
  y pulsa Intro.

`cd <folder>` lleva la terminal a otra carpeta. Todos los comandos de estas páginas se escriben en la
carpeta propia de la herramienta.

## 4. Instalar lo que necesita {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Deberías ver `Successfully installed ...` al final (o `Requirement
already satisfied`).

## 5. Comprobar que funciona {#check-it-works}

```bash
python -m heat3d_watch --version
```

Deberías ver: `1.0.2` (el número de versión).

## Cómo leer los comandos de estas páginas {#how-to-read-the-commands-on-these-pages}

- Las palabras entre `<corchetes angulares>` son marcadores: escribe tu propio archivo o carpeta en su
  lugar, sin los corchetes. `python -m heat3d_watch sessions --game <name>` significa que reemplazas la
  parte entre corchetes.
- Una ruta con espacios va entre comillas: `"C:\My Games\my file"`.
- Las líneas que empiezan por `#` en los ejemplos son comentarios; no las escribes.
- El éxito se ve así: tras `python -m heat3d_watch games`, una tabla con una línea por juego.

## Errores habituales {#common-errors}

| Ves | Haz esto |
|---|---|
| `'python' is not recognized` o `command not found` | Python no está en PATH: ejecuta el instalador de nuevo y marca **Add python.exe to PATH**, luego abre una terminal nueva. En macOS/Linux prueba `python3`. |
| `No module named ...` | se saltó el paso 4 o se ejecutó en otra carpeta: haz `cd` a la carpeta de la herramienta y vuelve a ejecutarlo. |
| `pip is not recognized` | usa `python -m pip ...` en lugar de `pip ...`. |
| `No such file or directory` / `can't open file` | la terminal está en la carpeta equivocada, o la ruta está mal escrita: revísala, y pon las rutas con espacios entre comillas. |
| texto rojo que termina en una línea `error:` | lee la última línea: dice qué falta. La página [Comandos](commands.md) enumera los mensajes. |
