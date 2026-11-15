---
title: Pirms sākat
nav_order: 2
lang: "lv"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Pirms sākat {#before-you-start}

Vai nekad neesat strādājis ar komandrindu? Šī lapa palīdzēs jums no nulles nonākt līdz strādājošam
3DHeat Watcher apmēram desmit minūtēs. Komandas rakstiet *terminālī* - logā, kurā ierakstāt rindu un nospiežat Enter.

## 1. Uzstādiet Python {#install-python}

1. Lejupielādējiet Python 3.10 vai jaunāku no <https://www.python.org/downloads/>.
2. Palaidiet instalētāju. Pirmajā ekrānā atzīmējiet **Add python.exe to PATH**,
   tad noklikšķiniet **Install Now**.
3. Pārbaudiet: atveriet termināli (3. solis) un ierakstiet `python --version`. Jums vajadzētu redzēt
   `Python 3.` un numuru 10 vai lielāku.

Linux vai macOS Python parasti jau ir uzstādīts: lietojiet `python3` tur, kur šajās lapās rakstīts `python`.

## 2. Iegūstiet 3DHeat Watcher {#get-3dheat-watcher}

Lejupielādējiet zip failu no
[Releases lapas](https://github.com/Holdi601/3DHeat-Watcher/releases) un izpakojiet to, piemēram,
mapē `C:\Tools\3DHeat-Watcher`. (Ja jums ir Git, darbojas arī `git clone`.)

## 3. Atveriet termināli šajā mapē {#open-a-terminal-in-that-folder}

- **Windows:** failu pārlūkā atveriet mapi, noklikšķiniet adreses joslā, ierakstiet
  `powershell` un nospiediet Enter. Atveras zils vai melns logs, jau šajā mapē.
- **macOS / Linux:** atveriet *Terminal* un ierakstiet `cd ` (ar atstarpi), ievelciet
  mapi logā, nospiediet Enter.

`cd <folder>` pārvieto termināli uz citu mapi. Visas komandas šajās lapās tiek rakstītas rīka pašā mapē.

## 4. Uzstādiet, ko tas vajag {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Beigās jums vajadzētu redzēt `Successfully installed ...` (vai `Requirement
already satisfied`).

## 5. Pārbaudiet, ka tas darbojas {#check-it-works}

```bash
python -m heat3d_watch --version
```

Jums vajadzētu redzēt: `1.0.2 (the version number)`.

## Kā lasīt komandas šajās lapās {#how-to-read-the-commands-on-these-pages}

- Vārdi `<leņķiekavās>` ir vietturi: ierakstiet savu failu vai mapi bez leņķiekavām. `python -m heat3d_watch sessions --game <name>` nozīmē, ka jūs nomainiet iekavās ieslēgto daļu.
- Ceļš ar atstarpēm ieliek pēdiņās: `"C:\My Games\my file"`.
- Rindas, kas piemēros sākas ar `#`, ir komentāri; tās nerakstiet.
- Veiksme izskatās šādi: pēc `python -m heat3d_watch games` parādās tabula ar vienu rindu katrai spēlei.

## Biežākās kļūdas {#common-errors}

| Jūs redzat | Ko darīt |
|---|---|
| `'python' is not recognized` vai `command not found` | Python nav PATH: palaidiet instalētāju vēlreiz un atzīmējiet **Add python.exe to PATH**, tad atveriet jaunu termināli. Macos/Linux izmēģiniet `python3`. |
| `No module named ...` | 4. solis netika izpildīts vai tika izpildīts citā mapē: ar `cd` ieejiet rīka mapē un palaidiet vēlreiz. |
| `pip is not recognized` | rakstiet `python -m pip ...` `pip ...` vietā. |
| `No such file or directory` / `can't open file` | termināls ir nepareizā mapē, vai ceļš ir pārrakstīts: pārbaudiet to un ieliekiet ceļus ar atstarpēm pēdiņās. |
| sarkans teksts, kas beidzas ar `error:` rindu | izlasiet pēdējo rindu: tajā teikts, kas trūkst. Lapa [Komandas](../commands.md) uzskaita ziņojumus. |
