---
title: "Prije nego počnete"
nav_order: 2
lang: "bs"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Prije nego počnete {#before-you-start}

Komandna linija vam je nova? Ova stranica vas za desetak minuta vodi od ničega do
3DHeat Watchera koji radi. Komande upisujete u *terminal*, prozor
u kojem napišete red i pritisnete Enter.

## 1. Instalirajte Python {#install-python}

1. Preuzmite Python 3.10 ili noviji sa <https://www.python.org/downloads/>.
2. Pokrenite instalacijski program. Na prvom ekranu označite **Add python.exe to PATH**,
   pa kliknite **Install Now**.
3. Provjerite: otvorite terminal (korak 3) i upišite `python --version`. Trebali biste
   vidjeti `Python 3.` i broj 10 ili veći.

Na Linuxu ili macOS-u Python je obično već instaliran: koristite `python3` gdje
ove stranice kažu `python`.

## 2. Nabavite 3DHeat Watcher {#get-3dheat-watcher}

Preuzmite zip sa
[stranice Releases](https://github.com/Holdi601/3DHeat-Watcher/releases) i raspakujte ga, na
primjer u `C:\Tools\3DHeat-Watcher`. (Ako imate Git, radi i `git clone`.)

## 3. Otvorite terminal u tom folderu {#open-a-terminal-in-that-folder}

- **Windows:** otvorite folder u File Exploreru, kliknite u adresnu traku, upišite
  `powershell` i pritisnite Enter. Otvara se plavi ili crni prozor, već u
  tom folderu.
- **macOS / Linux:** otvorite *Terminal* i upišite `cd ` (s razmakom), prevucite
  folder u prozor, pritisnite Enter.

`cd <folder>` premješta terminal u drugi folder. Sve komande na ovim
stranicama upisuju se u folderu samog alata.

## 4. Instalirajte ono što treba {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Na kraju biste trebali vidjeti `Successfully installed ...` (ili `Requirement
already satisfied`).

## 5. Provjerite radi li {#check-it-works}

```bash
python -m heat3d_watch --version
```

Trebali biste vidjeti: `1.0.2 (the version number)`.

## Kako čitati komande na ovim stranicama {#how-to-read-the-commands-on-these-pages}

- Riječi u `<špicastim zagradama>` su rezervirana mjesta: upišite vlastitu datoteku ili folder
  umjesto toga, bez zagrada. `python -m heat3d_watch sessions --game <name>` znači da
  zamijenite dio u zagradama.
- Putanja s razmacima ide u navodnike: `"C:\My Games\my file"`.
- Redovi koji počinju s `#` u primjerima su komentari; ne upisujete ih.
- Uspjeh izgleda ovako: poslije `python -m heat3d_watch games` tabela s po jednim redom za svaku igru.

## Česte greške {#common-errors}

| Vidite | Uradite ovo |
|---|---|
| `'python' is not recognized` ili `command not found` | Python nije na PATH-u: ponovo pokrenite instalacijski program i označite **Add python.exe to PATH**, pa otvorite novi terminal. Na macOS-u/Linuxu probajte `python3`. |
| `No module named ...` | korak 4 je preskočen ili pokrenut u drugom folderu: uradite `cd` u folder alata i pokrenite ga ponovo. |
| `pip is not recognized` | koristite `python -m pip ...` umjesto `pip ...`. |
| `No such file or directory` / `can't open file` | terminal je u pogrešnom folderu ili je putanja pogrešno ukucana: provjerite je i stavite putanje s razmacima u navodnike. |
| crveni tekst koji završava redom `error:` | pročitajte zadnji red: kaže šta nedostaje. Stranica [Komande](commands.md) navodi poruke. |
