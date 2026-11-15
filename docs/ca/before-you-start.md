---
title: Abans de començar
nav_order: 2
lang: ca
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Abans de començar {#before-you-start}

Si és nou amb la línia d'ordres, aquesta pàgina el porta de no tenir res a un 3DHeat Watcher
en funcionament en uns deu minuts. Escriu ordres en un *terminal*, una finestra on
escriu una línia i prem Intro.

## 1. Instal·lar Python {#install-python}

1. Descarregui Python 3.10 o posterior des de <https://www.python.org/downloads/>.
2. Executi l'instal·lador. A la primera pantalla marqui **Add python.exe to PATH**,
   i després faci clic a **Install Now**.
3. Comprovi-ho: obri una terminal (pas 3) i escrigui `python --version`. Hauria de veure
   `Python 3.` i un número 10 o superior.

A Linux o macOS, Python sol estar ja instal·lat: faci servir `python3` on aquestes pàgines
diuen `python`.

## 2. Obtenir 3DHeat Watcher {#get-3dheat-watcher}

Descarregui el zip de la [pàgina de versions](https://github.com/Holdi601/3DHeat-Watcher/releases) i
descomprimeixi'l, per exemple a `C:\Eines\3DHeat-Watcher`. (Si té Git, `git clone` també funciona.)

## 3. Obrir una terminal en aquesta carpeta {#open-a-terminal-in-that-folder}

- **Windows:** obri la carpeta a l'Explorador de fitxers, faci clic a la barra d'adreces, escrigui
  `powershell` i premi Intro. S'obre una finestra blava o negra, ja en aquesta carpeta.
- **macOS / Linux:** obri *Terminal* i escrigui `cd ` (amb un espai), arrossegui la
  carpeta a la finestra, i premi Intro.

`cd <carpeta>` mou la terminal a una altra carpeta. Totes les ordres d'aquestes
pàgines s'escriuen a la carpeta de l'eina.

## 4. Instal·lar el que necessita {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Al final hauria de veure `Successfully installed ...` (o `Requirement
already satisfied`).

## 5. Comprovar que funciona {#check-it-works}

```bash
python -m heat3d_watch --version
```

Hauria de veure: `1.0.2 (el número de versió)`.

## Com llegir les ordres d'aquestes pàgines {#how-to-read-the-commands-on-these-pages}

- Les paraules entre `<angles>` són marcadors de posició: escrigui el seu propi fitxer o carpeta en
  lloc seu, sense els angles. `python -m heat3d_watch sessions --game <nom>` vol dir que
  substitueixi la part entre angles.
- Una ruta amb espais va entre cometes: `"C:\My Games\my file"`.
- Les línies que comencen amb `#` als exemples són comentaris; no els escrigui.
- Un èxit té aquest aspecte: després de `python -m heat3d_watch games`, una taula amb una línia per joc.

## Errors habituals {#common-errors}

| Veu | Què fer |
|---|---|
| `'python' is not recognized` o `command not found` | Python no és al PATH: torni a executar l'instal·lador i marqui **Add python.exe to PATH**, i després obri una terminal nova. A macOS/Linux provi `python3`. |
| `No module named ...` | s'ha saltat el pas 4 o s'ha executat en una altra carpeta: feu `cd` a la carpeta de l'eina i torneu-la a executar. |
| `pip is not recognized` | faci servir `python -m pip ...` en lloc de `pip ...`. |
| `No such file or directory` / `can't open file` | la terminal és a la carpeta equivocada, o la ruta està mal escrita: comproveu-la, i posi entre cometes les rutes amb espais. |
| text vermell que acaba en una línia `error:` | llegeixi l'última línia: diu què falta. La pàgina [Ordres](../commands.md) enumera els missatges. |
