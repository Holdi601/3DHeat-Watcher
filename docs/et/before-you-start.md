---
title: "Enne alustamist"
nav_order: 2
lang: et
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Enne alustamist {#before-you-start}

Pole sul käsurealt kogemust? See leht viib sind nullist töötava 3DHeat Watcheri juurde umbes kümne minutiga.
Kirjutad käske *terminali* — aknasse, kuhu kirjutad rea ja vajutad Enter.

## 1. Paigalda Python {#install-python}

1. Laadi alla Python 3.10 või uuem lehelt <https://www.python.org/downloads/>.
2. Käivita installer. Esimesel ekraanil märgi **Add python.exe to PATH**,
   seejärel klõpsa **Install Now**.
3. Kontrolli: ava terminal (samm 3) ja kirjuta `python --version`. Peaksid nägema
   `Python 3.` ja numbrit 10 või rohkem.

Linuxis või macOS-is on Python tavaliselt juba paigaldatud: kus need lehed ütlevad `python`, kasuta `python3`.

## 2. Hangi 3DHeat Watcher {#get-3dheat-watcher}

Laadi zip-fail alla [väljalasete lehelt](https://github.com/Holdi601/3DHeat-Watcher/releases) ja paki lahti,
näiteks kausta `C:\Tools\3DHeat-Watcher`. (Kui sul on Git, töötab ka `git clone`.)

## 3. Ava terminal selles kaustas {#open-a-terminal-in-that-folder}

- **Windows:** ava kaust Exploreris, klõpsa aadressiribale, kirjuta `powershell` ja vajuta Enter.
  Avaneb sinine või must aken, mis on juba selles kaustas.
- **macOS / Linux:** ava *Terminal* ja kirjuta `cd ` (tühikuga), lohista kaust
  aknasse ja vajuta Enter.

`cd <folder>` viib terminali teise kausta. Kõik käsud neil lehtedel kirjutatakse tööriista enda kaustas.

## 4. Paigalda, mida see vajab {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Lõpus peaksid nägema `Successfully installed ...` (või `Requirement
already satisfied`).

## 5. Kontrolli, et see töötab {#check-it-works}

```bash
python -m heat3d_watch --version
```

Peaksid nägema: `1.0.2 (the version number)`.

## Kuidas neid käske nendel lehtedel lugeda {#how-to-read-the-commands-on-these-pages}

- Sõnad `<nurksulgudes>` on **kohatäited**: kirjuta oma fail või kaust selle asemel, ilma sulgudeta.
  `python -m heat3d_watch sessions --game <name>` tähendab, et asendad sulgudes oleva osa.
- Tee tühikutega läheb jutumärkidesse: `"C:\My Games\my file"`.
- Näidetes algavad `#`-iga read on kommentaarid; neid ei kirjuta.
- Edu näeb välja nii: pärast `python -m heat3d_watch games` on tabel, kus on üks rida mängu kohta.

## Levinud vead {#common-errors}

| Näed | Tee nii |
|---|---|
| `'python' is not recognized` või `command not found` | Python pole PATH-is: käivita installer uuesti ja märgi **Add python.exe to PATH**, seejärel ava uus terminal. macOS/Linuxis proovi `python3`. |
| `No module named ...` | samm 4 jäi vahele või käivitati teises kaustas: `cd` tööriista kausta ja käivita uuesti. |
| `pip is not recognized` | kasuta `python -m pip ...` asemel `pip ...`. |
| `No such file or directory` / `can't open file` | terminal on valesti kaustas või tee on valesti kirjutatud: kontrolli seda ja pane tühikuga teed jutumärkidesse. |
| punane tekst, mis lõpeb reaga `error:` | loe viimast rida: see ütleb, mis puudu on. [Käsud](../commands.md) lehel on veateated loetletud. |
