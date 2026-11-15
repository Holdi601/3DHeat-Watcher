---
title: "Înainte de a începe"
nav_order: 2
lang: ro
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Înainte de a începe {#before-you-start}

Nu ați mai lucrat în linia de comandă? Această pagină vă duce de la zero la un 3DHeat Watcher care
funcționează, în vreo zece minute. Scrieți comenzi într-un *terminal*, o fereastră în care scrieți
un rând și apăsați Enter.

## 1. Instalați Python {#install-python}

1. Descărcați Python 3.10 sau mai nou de la <https://www.python.org/downloads/>.
2. Rulați programul de instalare. Pe primul ecran bifați **Add python.exe to PATH**,
   apoi apăsați **Install Now**.
3. Verificați: deschideți un terminal (pasul 3) și scrieți `python --version`. Ar trebui
   să vedeți `Python 3.` și un număr de 10 sau mai mare.

Pe Linux sau macOS, Python este de obicei deja instalat: folosiți `python3` acolo unde aceste pagini spun `python`.

## 2. Obțineți 3DHeat Watcher {#get-3dheat-watcher}

Descărcați arhiva de pe [pagina de lansări](https://github.com/Holdi601/3DHeat-Watcher/releases) și dezarhivați-o,
de exemplu în `C:\Tools\3DHeat-Watcher`. (Dacă aveți Git, merge și `git clone`.)

## 3. Deschideți un terminal în acel dosar {#open-a-terminal-in-that-folder}

- **Windows:** deschideți dosarul în File Explorer, faceți clic în bara de adrese, scrieți
  `powershell` și apăsați Enter. Se deschide o fereastră albastră sau neagră, deja în acel dosar.
- **macOS / Linux:** deschideți *Terminal* și scrieți `cd ` (cu un spațiu), trageți dosarul
  în fereastră, apăsați Enter.

`cd <folder>` mută terminalul într-un alt dosar. Toate comenzile din aceste pagini se scriu în
dosarul propriu al instrumentului.

## 4. Instalați ce are nevoie {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Ar trebui să vedeți `Successfully installed ...` la final (sau `Requirement
already satisfied`).

## 5. Verificați că funcționează {#check-it-works}

```bash
python -m heat3d_watch --version
```

Ar trebui să vedeți: `1.0.2 (numărul versiunii)`.

## Cum se citesc comenzile din aceste pagini {#how-to-read-the-commands-on-these-pages}

- Cuvintele între `<paranteze unghiulare>` sunt locuri rezervate: scrieți în loc propriul fișier sau
  dosar, fără paranteze. `python -m heat3d_watch sessions --game <name>` înseamnă că
  înlocuiți partea dintre paranteze.
- O cale cu spații se pune între ghilimele: `"C:\My Games\my file"`.
- Rândurile care încep cu `#` din exemple sunt comentarii; nu le scrieți.
- Succesul arată așa: după `python -m heat3d_watch games`, un tabel cu câte o linie pentru fiecare joc.

## Erori frecvente {#common-errors}

| Ce vedeți | Ce să faceți |
|---|---|
| `'python' is not recognized` sau `command not found` | Python nu este în PATH: rulați din nou programul de instalare și bifați **Add python.exe to PATH**, apoi deschideți un terminal nou. Pe macOS/Linux încercați `python3`. |
| `No module named ...` | pasul 4 a fost sărit sau a rulat într-un alt dosar: `cd` în dosarul instrumentului și rulați din nou. |
| `pip is not recognized` | folosiți `python -m pip ...` în loc de `pip ...`. |
| `No such file or directory` / `can't open file` | terminalul este în alt dosar, sau calea este greșit scrisă: verificați-o și puneți între ghilimele căile cu spații. |
| text roșu care se termină cu o linie `error:` | citiți ultima linie: spune ce lipsește. Pagina [Comenzi](../commands.md) listează mesajele. |
