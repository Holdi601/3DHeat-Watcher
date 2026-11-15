---
title: "Steam Timeline (platforma)"
nav_order: 44
lang: "sl"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (platforma) {#steam-timeline-platform}

Watcher shrani, kar Steam Timeline hrani o vaših igrah, da lahko kasneje pogledate svojo zgodovino kot statistiko in časovnico.

*Tehnične podrobnosti: adapter `steam-timeline`, vrsta [`platform`](sources-and-rules.md); deluje ves čas (ne čaka, da se igra začne) in išče nove podatke na vsakih 10 s.*

## Kaj se zapiše {#what-is-recorded}

- ena seja na datoteko časovnice: njen začetek in konec (session_start, session_end)
- dosežki, odklenjeni med igranjem, s časom
- spremembe načina igre (igranje, pripravljanje, meniji, nalagalni zaslon)
- dogodki, ki jih igre dodajo prek ISteamTimeline, z naslovom in opisom, pod imenom ikone
- faze igre (tekma, misija) z oznakami; dogodki znotraj nje nosijo njen id kot session
- opisi stanj, ki jih igra prikazuje na časovnici ("Round 3")
- Steamove lastne napake pri snemanju

## Od kod prihaja {#where-it-comes-from}

%STEAM%\userdata\\&lt;account&gt;\gamerecordings\timelines\timeline_&lt;appid&gt;&lt;date&gt;_&lt;time&gt;.json

## Kako ga vklopiti {#how-to-switch-it-on}

Steam > Settings > Game Recording: snemanje v ozadju ali na zahtevo (Steam takrat zapisuje časovnice)

## Kako deluje {#how-it-works}

Kar zagonski program in grafični gonilnik hranita o igranju: Steamove statistike, dosežki, čas igranja in časovnice ter NVIDIA-ini posnetki in klipi.

Nobeden od teh virov ne potrebuje, da igra sodeluje ali teče, zato so trije adapterji tukaj vedno vklopljeni in vsakih nekaj sekund preberejo nekaj datotek.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`, zapisana med vklopljenim Steam Game Recording. Datoteka je JSON z nizi za številke: "daterecorded" (sekunde po Unixu), "starttime"/"endtime" (ms) in "entries", vsak {"id", "time" (ms od daterecorded), "type", ...}. Vrste, videne v pravih datotekah:
```text
achievement        achievement_name - Steam to doda za vsako igro
gamemode           mode, ETimelineGameMode: 1 igranje, 2 pripravljanje, 3 meniji,
                   4 nalagalni zaslon
error              description - Steamova lastna napaka ("#GameRecording_RecordingFailed")
event              igrin AddInstantaneousTimelineEvent/AddRangeTimelineEvent:
                   naslov, opis, ikona, prioriteta, trajanje (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  naslov - SetTimelineTooltip ("Round 3")
phase              razpon StartGamePhase..EndGamePhase: trajanje (ms), oznake
                   [{name, icon, group, priority}] (mode, map ...)
```
Postavitev datoteke je Steamova in ni dokumentirana; polja so parametri API-ja. Vsaka druga vrsta se zapiše pod svojim imenom s svojimi polji.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Isti modul streže tudi: [NVIDIA highlights (platforma)](game-nvidia-highlights.md), [Statistika Steam (platforma)](game-steam-stats.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zapisani | ne |
| Os navzgor | `y` |
| Enote | metri |
| Zrcaljeno za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Ti podatki gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, tako da pregledovalnik 3DHeat vrstice sam obrne in prilagodi merilo - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igrano na spletu (`multiplayer`): **ne**. `games --markdown` to prikaže kot "enoigralska".
- Vrsta `platform`: bere samo, kar igra ali platforma izda (kar hrani Steam ali grafični gonilnik), zato zapisuje tudi v spletni igri, ne le brez povezave; zastavica odloča samo, ali sme pomnilnik sploh kdaj biti branjen.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji `memory` berejo pomnilnik, in nikoli za igro, označeno kot igrano na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Ključi statistike, ki jih koda tega adapterja nastavi po imenu (`stats` vsake seje v `meta.json` in tabela `stats` v `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz lastnih imen statistik igre, na tem seznamu niso; zgoraj v »Kaj se zapiše« so našteti.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali ohrani, nikoli ni izpuščeno. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, ohrani celoten v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in vsako polje, ohranjeno po imenu; `used` označuje, kar je postalo tudi vrstica), `meta.json` pa v `selfCheck.completeness` šteje vsak `type` - `lost` je 0.

**Prebrano**

- vsak vnos enkrat, kot vrstica ob svojem času: njegova vrsta, vsako navadno polje (naslov, opis, ikona, prioriteta, trajanje, possible_clip, ime dosežka, način, ...), oznake faze po skupinah, prikazno ime dosežka iz sheme statistik; začetek in konec datoteke

**Ohranjeno surovo**

- vsak vnos celoten kot JSON pod Steamovo vrsto `type` (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, katerakoli druga): ugnezdena polja - ikona in prioriteta oznake, vse, kar kasnejši Steam doda - so samo tukaj
- `timeline`: lastna polja datoteke (daterecorded, starttime, endtime, katerakoli druga), ob odprtju seje in ob vsaki spremembi

**Ni na voljo**

- samo snemanje (video): Steam ga hrani v svojih mapah; seja se sklicuje na datoteko časovnice po imenu
- branje datoteke, ki jo Steam piše in je ni mogoče razčleniti tudi z zaprtim koncem: šteje se (`bad` v stanju adapterja) in se prebere znova ob naslednji spremembi, kjer se njeni vnosi vzamejo

**Velikost**: nekaj sto vnosov po 100-300 bajtov na uro igranja: daleč pod 1 MB na uro

## Preverjeno {#verified}

Preizkušeno na pravih datotekah časovnic iz lokalne namestitve: dosežek, gamemode, error ter lastni dogodki, opisi stanj in faze iger; format datoteke sam ni dokumentiran.

## Vir {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
