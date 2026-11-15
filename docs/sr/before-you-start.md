---
title: Пре почетка
nav_order: 2
lang: sr
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Пре почетка {#before-you-start}

Први пут у командној линији? Ова страница вас води од нуле до радног
3DHeat Watcher-а за око десет минута. Команде куцате у *терминал*, прозор у који
напишете ред и притиснете Enter.

## 1. Инсталирајте Python {#install-python}

1. Преузмите Python 3.10 или новији са <https://www.python.org/downloads/>.
2. Покрените инсталер. На његовом првом екрану штиклирајте **Add python.exe to PATH**,
   па кликните на **Install Now**.
3. Проверите: отворите терминал (корак 3) и укуцајте `python --version`. Требало би да
   видите `Python 3.` и број 10 или већи.

На Linux-у или macOS-у Python је обично већ инсталиран: користите `python3` тамо где
ове странице кажу `python`.

## 2. Набавите 3DHeat Watcher {#get-3dheat-watcher}

Преузмите zip са [странице издања](https://github.com/Holdi601/3DHeat-Watcher/releases) и
распакујте га, на пример у `C:\Tools\3DHeat-Watcher`. (Ако имате Git, `git clone` такође ради.)

## 3. Отворите терминал у тој фасцикли {#open-a-terminal-in-that-folder}

- **Windows:** отворите фасциклу у File Explorer-у, кликните у адресну траку, укуцајте
  `powershell` и притисните Enter. Отвара се плаво или црно прозорче, већ у
  тој фасцикли.
- **macOS / Linux:** отворите *Terminal* и укуцајте `cd ` (са размаком), превуците
  фасциклу у прозор, притисните Enter.

`cd <folder>` пребацује терминал у другу фасциклу. Све команде на овим
странама куцају се у фасцикли самог алата.

## 4. Инсталирајте што му треба {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

На крају би требало да видите `Successfully installed ...` (или `Requirement
already satisfied`).

## 5. Проверите да ради {#check-it-works}

```bash
python -m heat3d_watch --version
```

Требало би да видите: `1.0.2 (the version number)`.

## Како читати команде на овим страницама {#how-to-read-the-commands-on-these-pages}

- Речи у `<угластим заградама>` су места за попуњавање: уместо њих укуцајте своју
  датотеку или фасциклу, без заграда. `python -m heat3d_watch sessions --game <name>` значи
  да замените део у заградама.
- Путања са размацима иде у наводнике: `"C:\My Games\my file"`.
- Редови који почињу са `#` у примерима су коментари; не куцате их.
- Успех изгледа овако: после `python -m heat3d_watch games`, табела са по једним редом за сваку игру.

## Уобичајене грешке {#common-errors}

| Видите | Урадите ово |
|---|---|
| `'python' is not recognized` или `command not found` | Python није у PATH-у: покрените инсталер поново и штиклирајте **Add python.exe to PATH**, па отворите нови терминал. На macOS/Linux-у пробајте `python3`. |
| `No module named ...` | корак 4 је прескочен или је рађен у другој фасцикли: `cd` до фасцикле алата и покрените га поново. |
| `pip is not recognized` | користите `python -m pip ...` уместо `pip ...`. |
| `No such file or directory` / `can't open file` | терминал је у погрешној фасцикли, или је путања погрешно укуцана: проверите, и ставите путање са размацима под наводнике. |
| црвени текст који се завршава редом `error:` | прочитајте последњи ред: каже шта недостаје. Страница [Команде](../commands.md) наводи поруке. |
