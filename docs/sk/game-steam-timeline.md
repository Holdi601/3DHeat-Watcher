---
title: "Časová os Steamu (platforma)"
nav_order: 44
lang: "sk"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Časová os Steamu (platforma) {#steam-timeline-platform}

Watcher ukladá to, čo Časová os Steamu uchováva o vašich hrách, aby ste si históriu mohli neskôr pozrieť ako štatistiky a časovú os.

*Technické podrobnosti: adaptér `steam-timeline`, druh [`platform`](sources-and-rules.md); beží stále (nečaká, kým sa spustí hra) a hľadá nové dáta každých 10 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- jedna relácia na každý súbor časovej osi: jej začiatok a koniec (session_start, session_end)
- úspechy odomknuté počas hry, s časom
- zmeny herného režimu (hranie, príprava, menu, obrazovka načítania)
- udalosti, ktoré hry pridávajú cez ISteamTimeline, s názvom a popisom, pod menom ich ikony
- herné fázy (zápas, misia) s ich značkami; udalosti vnútri nej nesú jej id ako session
- popisy stavu, ktoré hra zobrazuje na časovej osi ("Kolo 3")
- vlastné chyby nahrávania zo Steamu

## Odkiaľ to pochádza {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Ako to zapnúť {#how-to-switch-it-on}

Steam > Nastavenia > Nahrávanie hry: nahrávať na pozadí alebo na požiadanie (Steam potom zapisuje časové osi)

## Ako to funguje {#how-it-works}

To, čo si launcher a grafický ovládač uchovávajú o hraní: štatistiky Steamu,
úspechy, čas hrania a časové osi a highlighty a klipy NVIDIA.

Žiaden z týchto zdrojov nepotrebuje, aby hra spolupracovala alebo bežala, takže
tri tu uvedené adaptéry sú vždy zapnuté a každých niekoľko sekúnd čítajú pár súborov.

#### Časová os Steamu (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`,
zapisovaný, kým je zapnuté nahrávanie hier v Steame. Súbor je JSON s číslami ako
reťazce: "daterecorded" (sekundy Unixu), "starttime"/"endtime" (ms) a
"entries", každý {"id", "time" (ms od daterecorded), "type", ...}. Typy
videné v skutočných súboroch:
```text
achievement        achievement_name - Steam pridáva pre každú hru
gamemode           mode, ETimelineGameMode: 1 hranie, 2 príprava,
                   3 menu, 4 obrazovka načítania
error              description - Steamova vlastná ("#GameRecording_RecordingFailed")
event              AddInstantaneousTimelineEvent/AddRangeTimelineEvent hry:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "Zabil si <name>" / "pomocou <weapon>"
state_description  title - SetTimelineTooltip ("Kolo 3")
phase              rozsah StartGamePhase..EndGamePhase: duration (ms), tags
                   [{name, icon, group, priority}] (režim, mapa ...)
```
Rozloženie súboru je Steamovo a nie je zdokumentované; polia sú parametre API.
Každý iný typ sa zaznamená pod svojím menom s vlastnými poľami.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Ten istý modul slúži aj pre: [NVIDIA highlighty (platforma)](game-nvidia-highlights.md), [Štatistiky Steamu (platforma)](game-steam-stats.md).

## Pozície a osi {#positions-and-axes}

| | |
|---|---|
| Pozície sa zaznamenávajú | nie |
| Os nahor | `y` |
| Jednotky | metre |
| Zrkadlené pre viewer | žiadne |
| Mierka jednotiek (`scale`: viewer násobí pozície touto hodnotou) | 1 |

Tieto hodnoty sa zapíšu do `meta.json` každej relácie (`axes`) a, ak relácia obsahuje pozície, do päty `heat.parquet`, takže viewer 3DHeat otáča a mierni riadky sám - pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **nie**. `games --markdown` to zobrazí ako "jednohráčová".
- Druh `platform`: číta len to, čo hra alebo platforma vydáva (čo uchováva Steam alebo grafický ovládač), takže zaznamenáva aj online hru, aj hru offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Kľúč v zložených zátvorkách sa dopĺňa pri behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z mien štatistík hry, v tomto zozname nie sú; "Čo sa zaznamenáva" vyššie ich uvádza.

## Úplnosť {#completeness}

Watcher dodržiava [pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo zdroj obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text`, a potom každé pole uchované podľa mena; `used` označuje, čo sa stalo aj riadkom), a `selfCheck.completeness` v `meta.json` počíta každý `type` - `lost` je 0.

**Prečítané**

- každá položka raz, ako riadok v jej čase: jej typ, každé jednoduché pole (title, description, icon, priority, duration, possible_clip, názov úspechu, režim, ...), značky fázy podľa skupiny, zobrazovaný názov úspechu zo schémy štatistík; začiatok a koniec súboru

**Uchované surové**

- každá položka celá ako JSON pod Steamovým vlastným `type` (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, ľubovoľný iný): vnorené polia - ikona a priorita značky, čokoľvek, čo neskorší Steam pridá - sú len tu
- `timeline`: vlastné polia súboru (daterecorded, starttime, endtime, ľubovoľné iné), keď sa relácia otvorí a znova, keď sa zmenia

**Nedostupné**

- samotné nahrávanie (video): Steam ho uchováva vo vlastných priečinkoch; relácia odkazuje na súbor časovej osi menom
- čítanie súboru, ktorý Steam zapisuje a ktorý sa nedá spracovať ani po uzavretí jeho konca: počíta sa (`bad` v stave adaptéra) a číta sa znova pri ďalšej zmene, kde sa jeho položky zoberú

**Veľkosť**: niekoľko stoviek položiek po 100-300 bajtoch na hodinu hrania: ďaleko pod 1 MB na hodinu

## Overené {#verified}

otestované na skutočných súboroch časovej osi z lokálnej inštalácie: položky úspechov, gamemode, error a vlastné položky hier event, state_description a phase; samotný formát súboru nie je zdokumentovaný

## Zdroj {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
