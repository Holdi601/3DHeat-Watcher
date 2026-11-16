---
title: Hjem
nav_order: 1
lang: "no"
source: index.md
source_hash: "269b4c01a4af"
nav_exclude: true
search_exclude: true
permalink: /no/
---
# 3DHeat Watcher {#dheat-watcher}

**Hva er det?** Du spiller et spill. Dette programmet skriver stille ned hvor du var og hva som skjedde.
Senere kan du se det som et fargelagt kart i 3DHeat-visningsprogrammet.

**Hvorfor skulle jeg bruke det?** For å ha din egen oversikt over hver økt - hvor du kjørte, fløy eller kjempet,
dine totaler per spill - uten noen nettside og uten å endre spillet.

**Eksempel:** du kjører en runde i et racingspill med watcheren i gang; etterpå inneholder en fil i
`sessions\<game>\` linjen du tok, og visningsprogrammet tegner den.

Mer detaljert: 3DHeat Watcher er et bakgrunnsprogram som tar opp det spill publiserer om spillingen din - hvor
du var, hva som skjedde hvor, og tallene bak det - i filer på din egen maskin. Filene er til din egen
statistikk og til varmekartene og rutelinjene i 3DHeat-visningsprogrammet.

Det kjører stille, legger merke til hvilket spill du startet, og leser det spillets egne utdata: en telemetriport
eller delt minne spillet publiserer for dashbord, en spilltilstandsintegrasjon, loggen eller journalen spillet
skriver, replayen det lagrer etter en kamp, statistikken Steam holder, og klippene NVIDIA-appen lagrer.
Opptakene blir på din egen maskin. Programmet kontakter bare to eksterne tjenester, og bare i disse tilfellene:
GitHub, for å se etter en nyere utgivelse (se [Oppdateringer](updates.md)), og Riots Match-V5-API, og bare hvis du
legger inn din egen Riot-API-nøkkel (se [League of Legends-replays](game-lol-replays.md)).

![watcheren: det spill publiserer, inn i filer på maskinen din](../assets/img/no/overview.svg)

## Hva det tar opp {#what-it-records}

- **Posisjoner**: bilen, flyet, helten eller spilleren, flere ganger i sekundet der spillet publiserer dem, med fart,
  kurs og alt annet spillet sender sammen med dem.
- **Hendelser**: spawn, dødsfall, drap, runder, etapper, mål, jobber, start og landinger, sonebytter, prestasjoner,
  høydepunkter. Hver hendelse lagres med tidspunkt, og med sted når spillet gir det.
- **Statistikk per økt**: drap, dødsfall, runder, beste runde, distanse, toppfart, spilletid, og spillets egen
  statistikk der det fører den.

Hva hvert spill gir, og fra hvor, står på sin egen side under [Spill](games.md). En kilde kan ikke ta opp alt:
flerspillerspill tas bare opp gjennom det de publiserer, og watcheren leser aldri deres minne (se
[Kilder og regler](sources-and-rules.md)).

## Installer {#install}

Ny til kommandolinjen? Les [Før du begynner](before-you-start.md) først.

Watcheren er et Python-program for Windows (Python 3.10 eller nyere). Mange av kildene finnes bare på Windows: delt
minne, registeret, Windows-varsler.

```bash
git clone https://github.com/Holdi601/3DHeat-Watcher.git
cd 3DHeat-Watcher
pip install -r requirements.txt
```

En nedlastet utgivelsesarkiv fungerer på samme måte: pakk ut, kjør deretter `pip install -r requirements.txt`
inne i mappen. Detaljene, og tilleggene noen spill trenger, står i
[Installere og kjøre](installing-and-running.md).

## Hurtigstart {#quick-start}

```bash
python -m heat3d_watch games            # what each game gives, and from where
python -m heat3d_watch setup all        # what would have to be switched on (nothing is changed)
python -m heat3d_watch setup f1-25 --apply   # switch one game's output on (the original file is backed up)
python -m heat3d_watch run              # watch; leave it running while you play
python -m heat3d_watch stats            # totals per game
python -m heat3d_watch stats --csv out  # sessions, events and stats as CSV files
```

Du bør se: etter `games`, en tabell med én linje per spill; `run` fortsetter til du trykker Ctrl+C eller lukker vinduet.

Alt skrives til `%LOCALAPPDATA%\3DHeat\Watcher`. For å bruke en annen mappe, sett miljøvariabelen
`HEAT3D_WATCH_HOME`, eller kjør `python -m heat3d_watch config --set data=D:\somewhere`.

- `sessions\<game>\<date>_<adapter>\` - én mappe per økt, med `events.jsonl` (hver hendelse
  etter hvert som den skjer), `heat.parquet` (radene med en posisjon, klare for 3DHeat-visningsprogrammet) og
  `meta.json` (spill, kilde, akser, antall, statistikk)
- `watcher.sqlite` - statistikken for hver økt, i tre enkle tabeller
- `watcher.log` - hva watcheren gjorde

Visningsprogrammet åpner en økts `heat.parquet` direkte, uten noe å sette opp (aksene og enhetene står i filen).
Konverterte replayer skrives som tabeller og kampdokumenter ved siden av den; visningsprogrammets eget format
med én fil per kamp beskrives på siden om [`.3dheat`-beholderen](https://holdi601.github.io/3DHeat/container.html),
og hver tabells kolonner i [Dataene](the-data.md).

## Dokumentasjonen {#the-documentation}

| Side | Hva den dekker |
|---|---|
| [Før du begynner](before-you-start.md) | Python, en terminal, plassholdere, hvordan suksess og de vanlige feilene ser ut |
| [Installere og kjøre](installing-and-running.md) | krav, kjøring i bakgrunnen, start med Windows, låsefilen, loggen, hver innstilling og miljøvariabel |
| [Spill](games.md) | én side per spill: hva som tas opp, hvorfra, hvordan det slås på, hvordan det virker, akser, statistikk, hva som er kontrollert |
| [Dataene](the-data.md) | øktmapper, `events.jsonl`, `heat.parquet` og footeren, `meta.json`, `watcher.sqlite`, gjenoppretting etter krasj, CSV-eksport, åpne en økt i 3DHeat-visningsprogrammet |
| [Kommandoer](commands.md) | hver kommando og hvert alternativ i `python -m heat3d_watch` |
| [Kilder og regler](sources-and-rules.md) | de seks typene kilder, flerspillerreglene, hvilke spill som er utelatt og hvorfor |
| [NVIDIA Highlights](nvidia-highlights.md) | hva NVIDIA Highlights kan og ikke kan levere, og hvordan et høydepunkt får en posisjon |
| [Opptaksmods for servere](server-mods.md) | Arma 3- og Arma Reforger-servermodene som tar opp hele oppdrag for visningsprogrammet |
| [Lese minne](memory-reading.md) | enspillerprofiler for minne: formatet, kontrollene, hvordan man skriver og verifiserer en |
| [Oppdateringer](updates.md) | hvordan watcheren ser etter nye utgivelser og oppdaterer seg selv |
| [Utvikling](development.md) | skrive en adapter: API-et, tester, en ærlig `verified`, regenerering av spillsidene |
| [Alle spill i én tabell](watcher.md) | hvert spill i én tabell, slik `games --markdown` skriver den, pluss spillene som er undersøkt men ikke bygget ennå |
| [Kommandoreferanse](../cli-reference.md) | hver kommandos `--help`, generert fra koden |
| [Vedlikehold](maintaining.md) | utgivelsessjekklisten for disse sidene |

## Del av 3DHeat {#part-of-3dheat}

3DHeat Watcher er ett av de gratis verktøyene rundt 3DHeat-visningsprogrammet (watcheren bruker 3DHeat CS2
til å konvertere CS2-demoer). Hvert er et eget prosjekt, med egne utgivelser og lisens:

| Verktøy | Hva det gjør | Dokumentasjon |
|---|---|---|
| [3DHeat](https://github.com/Holdi601/3DHeat) | visningsprogrammet: varmekart, løpsanalyse og kampgjennomgang i 3D | [nettsted](https://holdi601.github.io/3DHeat/) |
| [GameFiles](https://github.com/Holdi601/3DHeat-GameFiles) | baner og nivåer fra filene spill leveres med, som 3D-modeller | [nettsted](https://holdi601.github.io/3DHeat-GameFiles/) |
| [GameCapture](https://github.com/Holdi601/3DHeat-GameCapture) | rundetelemetri fra racingspill; nivåer rekonstruert fra spillvideo | [nettsted](https://holdi601.github.io/3DHeat-GameCapture/) |
| [Unreal Exporter](https://github.com/Holdi601/3DHeat-UnrealExporter) | et Unreal Editor-tillegg som eksporterer et nivå som én 3D-modell | [nettsted](https://holdi601.github.io/3DHeat-UnrealExporter/) |
| [CS2](https://github.com/Holdi601/3DHeat-CS2) | Counter-Strike 2-demoer til tabeller og kampdokumenter; kart til 3D-modeller | [nettsted](https://holdi601.github.io/3DHeat-CS2/) |
| [Watcher](https://github.com/Holdi601/3DHeat-Watcher) | tar opp hva spill publiserer om spilling din, i bakgrunnen | [nettsted](https://holdi601.github.io/3DHeat-Watcher/) |
| [Ext-WarThunder](https://github.com/Holdi601/3DHeat-Ext-WarThunder) | War Thunder-replays til tabeller og kampdokumenter | [nettsted](https://holdi601.github.io/3DHeat-Ext-WarThunder/) |
| [Ext-WoT](https://github.com/Holdi601/3DHeat-Ext-WoT) | World of Tanks-replays til tabeller og kampdokumenter | [nettsted](https://holdi601.github.io/3DHeat-Ext-WoT/) |
| [Ext-WoWs](https://github.com/Holdi601/3DHeat-Ext-WoWs) | World of Warships-replays til tabeller og kampdokumenter | [nettsted](https://holdi601.github.io/3DHeat-Ext-WoWs/) |
| [Ext-Squad](https://github.com/Holdi601/3DHeat-Ext-Squad) | Squad-serverdemoer til tabeller og kampdokumenter | [nettsted](https://holdi601.github.io/3DHeat-Ext-Squad/) |
| [Ext-DCS](https://github.com/Holdi601/3DHeat-Ext-DCS) | DCS World-kart til 3D-modeller | [nettsted](https://holdi601.github.io/3DHeat-Ext-DCS/) |
| [Ext-IL2](https://github.com/Holdi601/3DHeat-Ext-IL2) | IL-2 Sturmovik-kart til 3D-modeller | [nettsted](https://holdi601.github.io/3DHeat-Ext-IL2/) |
| [Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota) | Dota 2-kartet fra din egen installasjon som et 3D-nivå | [nettsted](https://holdi601.github.io/3DHeat-Ext-Dota/) |
| [Ext-DotaReplay](https://github.com/Holdi601/3DHeat-Ext-DotaReplay) | Dota 2-replays | [nettsted](https://holdi601.github.io/3DHeat-Ext-DotaReplay/) |
| [Ext-Riot](https://github.com/Holdi601/3DHeat-Ext-Riot) | League of Legends- og VALORANT-replays (det de bærer ukryptert) | [nettsted](https://holdi601.github.io/3DHeat-Ext-Riot/) |
| [Ext-Forza](https://github.com/Holdi601/3DHeat-Ext-Forza) | Forza-baner, løp og biler fra din egen installasjon | [nettsted](https://holdi601.github.io/3DHeat-Ext-Forza/) |
| [Ext-Battlefield](https://github.com/Holdi601/3DHeat-Ext-Battlefield) | Battlefield-nivåer (Frostbite) som 3D-nivåer | [nettsted](https://holdi601.github.io/3DHeat-Ext-Battlefield/) |
| [Ext-BeamNG](https://github.com/Holdi601/3DHeat-Ext-BeamNG) | BeamNG.drive-baner | [nettsted](https://holdi601.github.io/3DHeat-Ext-BeamNG/) |
| [Ext-ACRally](https://github.com/Holdi601/3DHeat-Ext-ACRally) | Assetto Corsa Rally-etapper som baner | [nettsted](https://holdi601.github.io/3DHeat-Ext-ACRally/) |
| [Ext-Reforger](https://github.com/Holdi601/3DHeat-Ext-Reforger) | Arma Reforger-verdener (Enfusion) som 3D-nivåer | [nettsted](https://holdi601.github.io/3DHeat-Ext-Reforger/) |
| [Ext-R6](https://github.com/Holdi601/3DHeat-Ext-R6) | Rainbow Six Siege-kampreplays | [nettsted](https://holdi601.github.io/3DHeat-Ext-R6/) |

Hver spilleser er sitt eget lille prosjekt med egen lisensfil, egne utgivelser og egen saksliste, slik
at den kan installeres, oppdateres, vedlikeholdes - eller trekkes tilbake etter ønske fra en
rettighetshaver - for seg selv, uten at det påvirker visningsprogrammet eller de andre verktøyene.

Lisens: MIT ([LICENSE](https://github.com/Holdi601/3DHeat-Watcher/blob/main/LICENSE)). Lisensene til
tredjepartspakkene den bruker, og hva spillene den leser krever, står i
[LICENSES.md](https://github.com/Holdi601/3DHeat-Watcher/blob/main/LICENSES.md).
