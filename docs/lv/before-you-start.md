---
title: Pirms sākat
nav_order: 2
lang: lv
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Pirms sākat {#before-you-start}

Vai nekad neesi strādājis ar komandrindu? Šī lapa palīdzēs tev no nulles nonākt līdz strādājošam
3DHeat Watcher apmēram desmit minūtēs. Komandas raksti *terminālī* - logā, kurā ieraksti rindu un nospied Enter.

## 1. Uzstādi Python {#install-python}

1. Lejupielādē Python 3.10 vai jaunāku no <https://www.python.org/downloads/>.
2. Palaid instalētāju. Pirmajā ekrānā atzīmē **Add python.exe to PATH**,
   tad noklikšķini **Install Now**.
3. Pārbaudi: atver terminali (3. solis) un ieraksti `python --version`. Tev vajadzētu redzēt
   `Python 3.` un numuru 10 vai lielāku.

Linux vai macOS Python parasti jau ir uzstādīts: lieto `python3` tur, kur šajās lapās rakstīts `python`.

## 2. Iegūsti 3DHeat Watcher {#get-3dheat-watcher}

Lejupielādē zip failu no
[Releases lapas](https://github.com/Holdi601/3DHeat-Watcher/releases) un izpako to, piemēram,
mapē `C:\Tools\3DHeat-Watcher`. (Ja tev ir Git, darbojas arī `git clone`.)

## 3. Atver terminali šajā mapē {#open-a-terminal-in-that-folder}

- **Windows:** failu pārlūkā atver mapi, noklikšķini adreses joslā, ieraksti
  `powershell` un nospied Enter. Atveras zils vai melns logs, jau šajā mapē.
- **macOS / Linux:** atver *Terminal* un ieraksti `cd ` (ar atstarpi), ievelc
  mapi logā, nospied Enter.

`cd <folder>` pārvieto terminali uz citu mapi. Visas komandas šajās lapās tiek rakstītas rīka pašā mapē.

## 4. Uzstādi, ko tas vajag {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Beigās tev vajadzētu redzēt `Successfully installed ...` (vai `Requirement
already satisfied`).

## 5. Pārbaudi, ka tas darbojas {#check-it-works}

```bash
python -m heat3d_watch --version
```

Tev vajadzētu redzēt: `1.0.2 (the version number)`.

## Kā lasīt komandas šajās lapās {#how-to-read-the-commands-on-these-pages}

- Vārdi `<leņķiekavās>` ir vietturi: ieraksti savu failu vai mapi bez leņķiekavām. `python -m heat3d_watch sessions --game <name>` nozīmē, ka tu nomaini iekavās ieslēgto daļu.
- Ceļš ar atstarpēm ieliek pēdiņās: `"C:\My Games\my file"`.
- Rindas, kas piemēros sākas ar `#`, ir komentāri; tās nerakstīt.
- Veiksme izskatās šādi: pēc `python -m heat3d_watch games` parādās tabula ar vienu rindu katrai spēlei.

## Biežākās kļūdas {#common-errors}

| Tu redzi | Dari šo |
|---|---|
| `'python' is not recognized` vai `command not found` | Python nav PATH: palaid instalētāju vēlreiz un atzīmē **Add python.exe to PATH**, tad atver jaunu terminali. Macos/Linux pamēģini `python3`. |
| `No module named ...` | 4. solis netika izpildīts vai tika izpildīts citā mapē: ar `cd` ieej rīka mapē un palaid vēlreiz. |
| `pip is not recognized` | raksti `python -m pip ...` `pip ...` vietā. |
| `No such file or directory` / `can't open file` | terminālis ir nepareizā mapē, vai ceļš ir pārrakstīts: pārbaudi to un ieliec ceļus ar atstarpēm pēdiņās. |
| sarkans teksts, kas beidzas ar `error:` rindu | izlasi pēdējo rindu: tajā teikts, kas trūkst. Lapa [Komandas](../commands.md) uzskaita ziņojumus. |
