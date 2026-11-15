---
title: "Áður en þú byrjar"
nav_order: 2
lang: "is"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Áður en þú byrjar {#before-you-start}

Hefurðu aldrei notað skipanalínu? Þessi síða kemur þér frá engu að virku
3DHeat Watcher á um tíu mínútum. Þú skrifar skipanir í *skipanalínu* (terminal), glugga
þar sem þú skrifar línu og ýtir á Enter.

## 1. Settu upp Python {#install-python}

1. Sæktu Python 3.10 eða nýrra á <https://www.python.org/downloads/>.
2. Keyrðu uppsetningarforritið. Á fyrsta skjánum skaltu haka við **Add python.exe to PATH**
   og smella síðan á **Install Now**.
3. Athugaðu: opnaðu skipanalínu (skref 3) og skrifaðu `python --version`. Þú ættir að
   sjá `Python 3.` og töluna 10 eða hærri.

Á Linux eða macOS er Python yfirleitt þegar uppsett: notaðu `python3` þar sem
þessar síður segja `python`.

## 2. Náðu í 3DHeat Watcher {#get-3dheat-watcher}

Sæktu zip-skrána af
[útgáfusíðunni](https://github.com/Holdi601/3DHeat-Watcher/releases) og pakkaðu henni upp, til dæmis
í `C:\Tools\3DHeat-Watcher`. (Ef þú ert með Git virkar `git clone` líka.)

## 3. Opnaðu skipanalínu í þeirri möppu {#open-a-terminal-in-that-folder}

- **Windows:** opnaðu möppuna í File Explorer, smelltu í vistfangastikuna, skrifaðu
  `powershell` og ýttu á Enter. Blár eða svartur gluggi opnast, þegar í
  þeirri möppu.
- **macOS / Linux:** opnaðu *Terminal* og skrifaðu `cd ` (með bili), dragðu
  möppuna inn í gluggann, ýttu á Enter.

`cd <folder>` færir skipanalínuna í aðra möppu. Allar skipanir á þessum
síðum eru skrifaðar í eigin möppu verkfærisins.

## 4. Settu upp það sem það þarf {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Þú ættir að sjá `Successfully installed ...` í lokin (eða `Requirement
already satisfied`).

## 5. Athugaðu að það virki {#check-it-works}

```bash
python -m heat3d_watch --version
```

Þú ættir að sjá: `1.0.2 (the version number)`.

## Hvernig á að lesa skipanirnar á þessum síðum {#how-to-read-the-commands-on-these-pages}

- Orð í `<oddklofum>` eru staðgenglar: skrifaðu þína eigin skrá eða möppu
  í staðinn, án klofanna. `python -m heat3d_watch sessions --game <name>` þýðir að
  þú skiptir út hlutanum í klofunum.
- Slóð með bilum fer innan gæsalappa: `"C:\My Games\my file"`.
- Línur sem byrja á `#` í dæmunum eru athugasemdir; þú skrifar þær ekki.
- Árangur lítur svona út: eftir `python -m heat3d_watch games`, tafla með einni línu fyrir hvern leik.

## Algengar villur {#common-errors}

| Þú sérð | Gerðu þetta |
|---|---|
| `'python' is not recognized` eða `command not found` | Python er ekki á PATH: keyrðu uppsetningarforritið aftur og hakaðu við **Add python.exe to PATH**, opnaðu síðan nýja skipanalínu. Á macOS/Linux prófaðu `python3`. |
| `No module named ...` | skrefi 4 var sleppt eða það var keyrt í annarri möppu: farðu með `cd` í möppu verkfærisins og keyrðu það aftur. |
| `pip is not recognized` | notaðu `python -m pip ...` í stað `pip ...`. |
| `No such file or directory` / `can't open file` | skipanalínan er í rangri möppu, eða slóðin er rangt skrifuð: athugaðu hana, og settu slóðir með bilum innan gæsalappa. |
| rauður texti sem endar á `error:` línu | lestu síðustu línuna: hún segir hvað vantar. Á síðunni [Skipanir](commands.md) eru skilaboðin talin upp. |
