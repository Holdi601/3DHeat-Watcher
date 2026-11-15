---
title: "Ennen aloittamista"
nav_order: 2
lang: fi
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Ennen aloittamista {#before-you-start}

Uusi komentorivin kanssa? Tämä sivu vie sinut nollasta toimivaan 3DHeat Watcheriin noin
kymmenessä minuutissa. Kirjoitat komentoja *päätteeseen*, ikkunaan, johon kirjoitat rivin ja painat Enter.

## 1. Asenna Python {#install-python}

1. Lataa Python 3.10 tai uudempi osoitteesta <https://www.python.org/downloads/>.
2. Suorita asennusohjelma. Ensimmäisellä näytöllä rastita **Add python.exe to PATH**,
   ja napsauta sitten **Install Now**.
3. Tarkista: avaa pääte (vaihe 3) ja kirjoita `python --version`. Pitäisi näkyä `Python 3.` ja luku 10 tai suurempi.

Linuxissa tai macOS:ssä Python on yleensä jo asennettu: käytä `python3`:a siellä, missä nämä sivut sanovat `python`.

## 2. Hae 3DHeat Watcher {#get-3dheat-watcher}

Lataa zip [Releases-sivulta](https://github.com/Holdi601/3DHeat-Watcher/releases) ja pura se
esimerkiksi kansioon `C:\Tools\3DHeat-Watcher`. (Jos sinulla on Git, `git clone` käy myös.)

## 3. Avaa pääte kyseisessä kansiossa {#open-a-terminal-in-that-folder}

- **Windows:** avaa kansio Resurssienhallinnassa, napsauta osoitepalkkiin, kirjoita `powershell` ja
  paina Enter. Sininen tai musta ikkuna aukeaa, jo kyseisessä kansiossa.
- **macOS / Linux:** avaa *Terminal* ja kirjoita `cd ` (välilyönnin kanssa), vedä kansio
  ikkunaan ja paina Enter.

`cd <folder>` siirtää päätteen toiseen kansioon. Kaikki komennot näillä sivuilla kirjoitetaan
työkalun omassa kansiossa.

## 4. Asenna tarvittavat {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Lopussa pitäisi näkyä `Successfully installed ...` (tai `Requirement already satisfied`).

## 5. Tarkista, että se toimii {#check-it-works}

```bash
python -m heat3d_watch --version
```

Pitäisi näkyä: `1.0.2 (versionumero)`.

## Miten näitä komentoja luetaan {#how-to-read-the-commands-on-these-pages}

- Sanat `<kulmasulkeissa>` ovat paikanpitäjiä: kirjoita oma tiedosto tai kansio niiden tilalle, ilman sulkeita.
  `python -m heat3d_watch sessions --game <name>` tarkoittaa, että korvaat sulkeissa olevan osan.
- Välilyöntejä sisältävä polku kirjoitetaan lainausmerkkeihin: `"C:\My Games\my file"`.
- Esimerkkien rivit, jotka alkavat `#`-merkillä, ovat kommentteja; et kirjoita niitä.
- Onnistuminen näyttää tältä: `python -m heat3d_watch games`-komennon jälkeen taulukko, jossa on yksi rivi per peli.

## Yleiset virheet {#common-errors}

| Näet | Tee näin |
|---|---|
| `'python' is not recognized` tai `command not found` | Python ei ole PATH:ssa: suorita asennusohjelma uudelleen ja rastita **Add python.exe to PATH**, avaa sitten uusi pääte. Macissa/Linuxissa kokeile `python3`. |
| `No module named ...` | vaihe 4 jäi väliin tai ajettiin toisessa kansiossa: `cd` työkalun kansioon ja aja se uudelleen. |
| `pip is not recognized` | käytä `python -m pip ...` komennon `pip ...` sijaan. |
| `No such file or directory` / `can't open file` | pääte on väärässä kansiossa tai polku on kirjoitettu väärin: tarkista se, ja laita välilyöntejä sisältävät polut lainausmerkkeihin. |
| punaista tekstiä, joka päättyy `error:`-riviin | lue viimeinen rivi: se kertoo, mitä puuttuu. [Komennot](../commands.md)-sivu luettelee viestit. |
