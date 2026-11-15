---
title: "Mielőtt elkezded"
nav_order: 2
lang: "hu"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Mielőtt elkezded {#before-you-start}

Még nem használt parancssort? Ez az oldal a semmitől egy működő 3DHeat Watcherig vezet, körülbelül tíz perc alatt.
Parancsokat egy *terminálba* gépelsz be: ez egy ablak, ahol egy sort írsz, és Entert nyomsz.

## 1. Telepítsd a Pythont {#install-python}

1. Töltsd le a Python 3.10 vagy újabb verzióját innen: <https://www.python.org/downloads/>.
2. Futtasd a telepítőt. Az első képernyőn pipáld be a **Add python.exe to PATH** lehetőséget, majd
   kattints az **Install Now** gombra.
3. Ellenőrizd: nyiss terminált (3. lépés), és gépeld be a `python --version` parancsot. Ezt kell látnod:
   `Python 3.`, és egy 10 vagy annál nagyobb szám.

Linuxon vagy macOS-en a Python általában már telepítve van: ahol ezek az oldalak `python`-t írnak, ott `python3`-at használj.

## 2. Szerezd meg a 3DHeat Watchert {#get-3dheat-watcher}

Töltsd le a zip-et a [Kiadások oldaláról](https://github.com/Holdi601/3DHeat-Watcher/releases), és csomagold ki,
például ide: `C:\Tools\3DHeat-Watcher`. (Ha van Gitje, a `git clone` is működik.)

## 3. Nyiss terminált abban a mappában {#open-a-terminal-in-that-folder}

- **Windows:** nyisd meg a mappát a Fájlkezelőben, kattints a címsorba, gépeld be a `powershell`-t, és
  nyomj Entert. Egy kék vagy fekete ablak nyílik meg, már abban a mappában.
- **macOS / Linux:** nyisd meg a *Terminal* alkalmazást, gépeld be a `cd ` parancsot (szóközzel), húzd a
  mappát az ablakba, nyomj Entert.

A `cd <folder>` egy másik mappába viszi a terminált. Ezeken az oldalakon minden parancsot az eszköz saját
mappájában gépelj be.

## 4. Telepítsd, amire szükséged van {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

A végén `Successfully installed ...` kezdetű sor jelenik meg (vagy `Requirement already satisfied`).

## 5. Ellenőrizd, hogy működik {#check-it-works}

```bash
python -m heat3d_watch --version
```

Ezt kell látnod: `1.0.2 (a verziószám)`.

## Hogyan olvasd a parancsokat ezeken az oldalakon {#how-to-read-the-commands-on-these-pages}

- A `<szögletes zárójelben>` álló szavak **helyőrzők**: a zárójel nélkül írd be a saját fájlját vagy mappáját.
  A `python -m heat3d_watch sessions --game <name>` azt jelenti, hogy a zárójelben lévő részt cseréld ki.
- Szóközt tartalmazó útvonalat idézőjelbe tegyél: `"C:\My Games\my file"`.
- A példákban a `#`-tel kezdődő sorok megjegyzések; ezeket nem kell beírni.
- A siker így néz ki: a `python -m heat3d_watch games` után egy táblázat, játékonként egy sorral.

## Gyakori hibák {#common-errors}

| Amit lát | Mit tegyél |
|---|---|
| `'python' is not recognized` vagy `command not found` | a Python nincs a PATH-ban: futtasd újra a telepítőt, és pipáld be az **Add python.exe to PATH** lehetőséget, majd nyiss új terminált. Macen/Linuxon próbáld a `python3`-at. |
| `No module named ...` | a 4. lépés kimaradt, vagy másik mappában futott: lépj az eszköz mappájába a `cd` paranccsal, és futtasd újra. |
| `pip is not recognized` | a `pip ...` helyett használd a `python -m pip ...`-t. |
| `No such file or directory` / `can't open file` | a terminál rossz mappában van, vagy az útvonal elgépelt: ellenőrizd, és a szóközös útvonalakat tedd idézőjelbe. |
| piros szöveg, amely `error:` sorral végződik | olvasd el az utolsó sort: megmondja, mi hiányzik. A [Parancsok](../commands.md) oldal felsorolja az üzeneteket. |
