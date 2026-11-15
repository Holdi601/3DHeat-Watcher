---
title: "Steam Timeline (platforma)"
nav_order: 44
lang: "bs"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (platforma) {#steam-timeline-platform}

Watcher sprema ono što Steam Timeline čuva o vašim igrama, pa svoju historiju poslije možete pogledati kao statistiku i vremensku liniju.

*Tehnički detalji: adapter `steam-timeline`, vrsta [`platform`](sources-and-rules.md); radi stalno (ne čeka da igra krene) i svakih 10 s traži nove podatke.*

## Šta se snima {#what-is-recorded}

- jedna sesija po datoteci vremenske linije: njen početak i kraj (session_start, session_end)
- postignuća otključana tokom igranja, s vremenom
- promjene načina igre (igranje, priprema, meniji, ekran učitavanja)
- događaji koje igre dodaju preko ISteamTimeline, s naslovom i opisom, pod imenom svoje ikone
- faze igre (meč, misija) s njihovim oznakama; događaji unutar jedne nose njen id kao session
- opisi stanja koje igra prikazuje na vremenskoj liniji ("Round 3")
- Steamove vlastite greške snimanja

## Odakle dolazi {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Kako to uključiti {#how-to-switch-it-on}

Steam > Settings > Game Recording: snimajte u pozadini ili na zahtjev (tada Steam piše vremenske linije)

## Kako radi {#how-it-works}

Ono što pokretač i grafički drajver čuvaju o igranju: Steamova statistika,
postignuća, vrijeme igranja i vremenske linije, te NVIDIA-ini highlighti i klipovi.

Nijedan od ovih izvora ne traži da igra sarađuje niti da radi, pa su tri
adaptera ovdje uvijek uključena i svakih nekoliko sekundi gledaju nekoliko datoteka.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`,
piše se dok je Steam Game Recording uključen. Datoteka je JSON s brojevima
kao stringovima: "daterecorded" (Unix sekunde), "starttime"/"endtime" (ms) i
"entries", svaki {"id", "time" (ms od daterecorded), "type", ...}. Tipovi
viđeni na pravim datotekama:
```text
achievement        achievement_name - Steam adds these for every game
gamemode           mode, an ETimelineGameMode: 1 playing, 2 staging, 3 menus,
                   4 loading screen
error              description - Steam's own ("#GameRecording_RecordingFailed")
event              a game's AddInstantaneousTimelineEvent/AddRangeTimelineEvent:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              a StartGamePhase..EndGamePhase span: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```
Raspored datoteke je Steamov i nedokumentiran; polja su parametri
API-ja. Svaki drugi tip se snima pod svojim imenom sa svojim poljima.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Isti modul služi i: [NVIDIA highlighti (platforma)](game-nvidia-highlights.md), [Steam statistika (platforma)](game-steam-stats.md).

## Pozicije i ose {#positions-and-axes}

| | |
|---|---|
| Pozicije se snimaju | ne |
| Osa gore | `y` |
| Jedinice | metri |
| Zrcaljeno za preglednik | nema |
| Skala jedinica (`scale`: preglednik njome množi pozicije) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam rotira i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označeno kao igrano online (`multiplayer`): **ne**. `games --markdown` to prikazuje kao "singleplayer".
- Vrsta `platform`: čita samo ono što igra ili platforma daje (ono što Steam ili grafički drajver čuva), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj adapter je **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i to nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježene statistike {#statistics-recorded}

Ključevi statistika koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Ključ u vitičastim zagradama dovršava se za vrijeme rada (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz igrinih vlastitih imena statistika nisu na ovoj listi; "Šta se snima" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeatovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor drži čita se ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, zatim svako polje čuvano po imenu; `used` označava šta je postalo i redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- svaki unos jednom, kao red u svom vremenu: njegov tip, svako obično polje (title, description, icon, priority, duration, possible_clip, ime postignuća, mode, ...), oznake faze po grupi, prikazno ime postignuća iz sheme statistike; početak i kraj datoteke

**Čuva se sirovo**

- svaki unos cijel kao JSON pod Steamovim vlastitim `type` (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, bilo koji drugi): ugniježđena polja - ikona i prioritet oznake, sve što kasniji Steam doda - nalaze se samo ovdje
- `timeline`: vlastita polja datoteke (daterecorded, starttime, endtime, bilo koje drugo), kad se sesija otvori i opet kad se promijene

**Nije dostupno**

- samo snimanje (video): Steam ga čuva u svojim folderima; sesija upućuje na datoteku vremenske linije po imenu
- čitanje datoteke koju Steam piše, a koja se ne može parsirati ni sa zatvorenim krajem: broji se (`bad` u stanju adaptera) i čita ponovo pri sljedećoj promjeni, kad se njeni unosi preuzmu

**Veličina**: nekoliko stotina unosa od 100-300 bajtova po satu igranja: znatno manje od 1 MB po satu

## Provjereno {#verified}

testirano na pravim datotekama vremenske linije s lokalne instalacije: unosi achievement, gamemode, error, te vlastiti event, state_description i phase unosi igara; sam format datoteke je nedokumentiran

## Izvor {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
