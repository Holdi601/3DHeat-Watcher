---
title: "Prieš pradedant"
nav_order: 2
lang: "lt"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Prieš pradedant {#before-you-start}

Nesate įpratę prie komandinės eilutės? Šis puslapis padės nuo nieko iki veikiančio 3DHeat Watcher maždaug per dešimt minučių.
Komandas rašote į *terminalą* – langą, kuriame įrašote eilutę ir paspaudžiate Enter.

## 1. Įdiekite Python {#install-python}

1. Atsisiųskite Python 3.10 ar naujesnę versiją iš <https://www.python.org/downloads/>.
2. Paleiskite diegimo programą. Pirmame ekrane pažymėkite **Add python.exe to PATH**,
   tada spustelėkite **Install Now**.
3. Patikrinkite: atidarykite terminalą (3 žingsnis) ir įrašykite `python --version`. Turėtumėte matyti
   `Python 3.` ir numerį 10 ar didesnį.

Linux ar macOS Python dažniausiai jau įdiegtas: tiesiog, kur šiuose puslapiuose parašyta `python`, rašykite `python3`.

## 2. Gaukite 3DHeat Watcher {#get-3dheat-watcher}

Atsisiųskite zip failą iš
[Releases puslapio](https://github.com/Holdi601/3DHeat-Watcher/releases) ir išskleiskite, pavyzdžiui,
į `C:\Tools\3DHeat-Watcher`. (Jei turite Git, veikia ir `git clone`.)

## 3. Atidarykite terminalą aplanke {#open-a-terminal-in-that-folder}

- **Windows:** atidarykite aplanką Failų naršyklėje, spustelėkite adresų juostą, įrašykite
  `powershell` ir paspauskite Enter. Atsidaro mėlynas ar juodas langas, jau tame
  aplanke.
- **macOS / Linux:** atidarykite *Terminal* ir įrašykite `cd ` (su tarpu), įtempkite
  aplanką į langą, paspauskite Enter.

`cd <folder>` perkelia terminalą į kitą aplanką. Visos šiuose puslapiuose esančios komandos
rašomos įrankio aplanke.

## 4. Įdiekite, ko jam reikia {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Pabaigoje turėtumėte matyti `Successfully installed ...` (arba `Requirement
already satisfied`).

## 5. Patikrinkite, ar veikia {#check-it-works}

```bash
python -m heat3d_watch --version
```

Turėtumėte matyti: `1.0.2 (the version number)`.

## Kaip skaityti šiuose puslapiuose esančias komandas {#how-to-read-the-commands-on-these-pages}

- Žodžiai `<kampiniuose skliaustuose>` yra vietos žymekliai: įrašykite vietoj jų savo failą ar aplanką, be skliaustų.
  `python -m heat3d_watch sessions --game <name>` reiškia, kad pakeičiate skliaustuose esančią dalį.
- Kelias su tarpais dedamas į kabutes: `"C:\My Games\my file"`.
- Eilutės, prasidedančios `#` pavyzdžiuose, yra komentarai; jų nerašote.
- Sėkmė atrodo taip: po `python -m heat3d_watch games` – lentelė su po eilutę kiekvienam žaidimui.

## Dažnos klaidos {#common-errors}

| Matote | Ką daryti |
|---|---|
| `'python' is not recognized` arba `command not found` | Python nėra PATH: paleiskite diegimo programą iš naujo ir pažymėkite **Add python.exe to PATH**, tada atidarykite naują terminalą. macOS/Linux pabandykite `python3`. |
| `No module named ...` | 4 žingsnis praleistas arba vykdytas kitame aplanke: `cd` į įrankio aplanką ir paleiskite dar kartą. |
| `pip is not recognized` | naudokite `python -m pip ...` vietoj `pip ...`. |
| `No such file or directory` / `can't open file` | terminalas yra ne tame aplanke arba kelias parašytas klaidingai: patikrinkite ir kelius su tarpais dėkite į kabutes. |
| raudonas tekstas, baigiantis `error:` eilute | perskaitykite paskutinę eilutę: ji pasako, kas trūksta. Puslapis [Komandos](../commands.md) išvardija pranešimus. |
