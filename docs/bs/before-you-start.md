---
title: "Prije nego počneš"
nav_order: 2
lang: bs
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Prije nego počneš {#before-you-start}

Komandna linija ti je nova? Ova stranica te za desetak minuta vodi od ničega do
3DHeat Watchera koji radi. Naredbe upisuješ u *terminal*, prozor
u kojem napišeš red i pritisneš Enter.

## 1. Instaliraj Python {#install-python}

1. Preuzmi Python 3.10 ili noviji sa <https://www.python.org/downloads/>.
2. Pokreni instalacijski program. Na prvom ekranu označi **Add python.exe to PATH**,
   pa klikni **Install Now**.
3. Provjeri: otvori terminal (korak 3) i upiši `python --version`. Trebao bi
   vidjeti `Python 3.` i broj 10 ili veći.

Na Linuxu ili macOS-u Python je obično već instaliran: koristi `python3` gdje
ove stranice kažu `python`.

## 2. Nabavi 3DHeat Watcher {#get-3dheat-watcher}

Preuzmi zip sa
[stranice Releases](https://github.com/Holdi601/3DHeat-Watcher/releases) i raspakuj ga, na
primjer u `C:\Tools\3DHeat-Watcher`. (Ako imaš Git, radi i `git clone`.)

## 3. Otvori terminal u tom folderu {#open-a-terminal-in-that-folder}

- **Windows:** otvori folder u File Exploreru, klikni u adresnu traku, upiši
  `powershell` i pritisni Enter. Otvara se plavi ili crni prozor, već u
  tom folderu.
- **macOS / Linux:** otvori *Terminal* i upiši `cd ` (s razmakom), prevuci
  folder u prozor, pritisni Enter.

`cd <folder>` premješta terminal u drugi folder. Sve naredbe na ovim
stranicama upisuju se u folderu samog alata.

## 4. Instaliraj ono što treba {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Na kraju bi trebao vidjeti `Successfully installed ...` (ili `Requirement
already satisfied`).

## 5. Provjeri radi li {#check-it-works}

```bash
python -m heat3d_watch --version
```

Trebao bi vidjeti: `1.0.2 (the version number)`.

## Kako čitati naredbe na ovim stranicama {#how-to-read-the-commands-on-these-pages}

- Riječi u `<špicastim zagradama>` su rezervirana mjesta: upiši vlastitu datoteku ili folder
  umjesto toga, bez zagrada. `python -m heat3d_watch sessions --game <name>` znači da
  zamijeniš dio u zagradama.
- Putanja s razmacima ide u navodnike: `"C:\My Games\my file"`.
- Redovi koji počinju s `#` u primjerima su komentari; ne upisuješ ih.
- Uspjeh izgleda ovako: poslije `python -m heat3d_watch games` tabela s po jednim redom za svaku igru.

## Česte greške {#common-errors}

| Vidiš | Uradi ovo |
|---|---|
| `'python' is not recognized` ili `command not found` | Python nije na PATH-u: ponovo pokreni instalacijski program i označi **Add python.exe to PATH**, pa otvori novi terminal. Na macOS-u/Linuxu probaj `python3`. |
| `No module named ...` | korak 4 je preskočen ili pokrenut u drugom folderu: uradi `cd` u folder alata i pokreni ga ponovo. |
| `pip is not recognized` | koristi `python -m pip ...` umjesto `pip ...`. |
| `No such file or directory` / `can't open file` | terminal je u pogrešnom folderu ili je putanja pogrešno ukucana: provjeri je i stavi putanje s razmacima u navodnike. |
| crveni tekst koji završava redom `error:` | pročitaj zadnji red: kaže šta nedostaje. Stranica [Naredbe](../commands.md) navodi poruke. |
