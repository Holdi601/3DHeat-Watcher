---
title: "Steam Timeline (platforma)"
nav_order: 44
lang: "hr"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (platforma) {#steam-timeline-platform}

Watcher sprema ono što Steam Timeline čuva o vašim igrama, pa svoju povijest kasnije možete pogledati kao statistiku i vremensku crtu.

*Tehnički podaci: adapter `steam-timeline`, vrsta [`platform`](sources-and-rules.md); radi stalno (ne čeka da igra počne) i traži nove podatke svakih 10 s.*

## Što se bilježi {#what-is-recorded}

- jedna sesija po datoteci vremenske crte: njezin početak i kraj (session_start, session_end)
- postignuća otključana tijekom igre, s vremenom
- promjene načina igre (igranje, priprema, izbornici, ekran učitavanja)
- događaji koje igre dodaju kroz ISteamTimeline, s naslovom i opisom, pod nazivom njihove ikone
- faze igre (utakmica, misija) s njihovim oznakama; događaji unutar njih nose njezin id kao session
- opisi stanja koje igra prikazuje na vremenskoj crti ("Round 3")
- Steamove vlastite pogreške snimanja

## Odakle dolazi {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Kako ga uključiti {#how-to-switch-it-on}

Steam > Settings > Game Recording: snimajte u pozadini ili na zahtjev (tada Steam piše vremenske crte)

## Kako radi {#how-it-works}

Ono što pokretač i upravljački program grafike čuvaju o igranju: Steamova statistika, postignuća, vrijeme igranja i vremenske crte, te NVIDIA-ini istaknuti trenuci i isječci.

Nijedan od ovih izvora ne traži da igra surađuje ili da je pokrenuta, pa su tri adaptera ovdje uvijek uključena i gledaju nekoliko datoteka svakih nekoliko sekundi.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`, piše se dok je Steam snimanje igre uključeno. Datoteka je JSON s brojevima kao nizovima: "daterecorded" (Unix sekunde), "starttime"/"endtime" (ms) i "entries", svaki {"id", "time" (ms od daterecorded), "type", ...}. Vrste viđene u pravim datotekama:
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
Raspored datoteke je Steamov i nedokumentiran; polja su parametri API-ja. Svaka druga vrsta bilježi se pod vlastitim imenom sa svojim poljima.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Isti modul služi i: [NVIDIA istaknuti trenuci (platforma)](game-nvidia-highlights.md), [Steam statistika (platforma)](game-steam-stats.md).

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | ne |
| Os prema gore | `y` |
| Jedinice | metri |
| Zrcaljeno za preglednik | nijedno |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovi podaci idu u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje `heat.parquet`-a, pa preglednik 3DHeat sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igrano na mreži (`multiplayer`): **ne**. `games --markdown` to prikazuje kao "jednoigrač".
- Vrsta `platform`: čita samo ono što igra ili platforma predaje (ono što Steam ili upravljački program grafike čuva), pa bilježi i na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ za svaki tim). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih imena statistike igre nisu na ovom popisu; navedeni su u odjeljku "Što se bilježi" gore.

## Potpunost {#completeness}

Watcher slijedi 3DHeatovo [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži pročita se ili sačuva, ništa se ne baca. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi sačuva se cijeli u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- svaki unos jednom, kao redak u svoje vrijeme: njegova vrsta, svako obično polje (title, description, icon, priority, duration, possible_clip, achievement name, mode, ...), oznake faze po grupi, prikazni naziv postignuća iz sheme statistike; početak i kraj datoteke

**Čuva se sirovo**

- svaki unos cijel kao JSON pod Steamovim vlastitim `type` (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, bilo koja druga vrsta): ugniježđena polja - ikona i prioritet oznake, sve što kasniji Steam doda - samo su ovdje
- `timeline`: vlastita polja datoteke (daterecorded, starttime, endtime, bilo koje drugo), kad se sesija otvori i opet kad se promijene

**Nije dostupno**

- sama snimka (video): Steam je čuva u svojim mapama; sesija se na datoteku vremenske crte upućuje po nazivu
- čitanje datoteke koju Steam piše, a koja se ne može raščlaniti ni kad je njezin kraj zatvoren: broji se (`bad` u stanju adaptera) i ponovno čita pri sljedećoj promjeni, kad se njezini unosi uzmu

**Veličina**: nekoliko stotina unosa od 100-300 bajtova po satu igranja: znatno manje od 1 MB po satu

## Provjereno {#verified}

testirano na pravim datotekama vremenske crte s lokalne instalacije: postignuće, gamemode, error, te vlastiti unosi igara event, state_description i phase; sam format datoteke nije dokumentiran

## Izvor {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i pokrenite ga ponovno umjesto uređivanja ove stranice. -->
