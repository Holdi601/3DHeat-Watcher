---
title: "BeamNG.drive (direkte data)"
nav_order: 7
lang: "no"
source: game-beamng.md
source_hash: "1c23a869a62f"
nav_exclude: true
search_exclude: true
---
# BeamNG.drive (direkte data) {#beamngdrive-live-data}

Mens du spiller BeamNG.drive, lagrer watcheren dataene spillet selv sender ut, slik at du senere kan se på dem på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `beamng`, type [`telemetry`](sources-and-rules.md); den kjører mens `BeamNG.drive.x64.exe` eller `BeamNG.drive.exe` går og ser etter nye data hvert 0,1 s.*

## Hva som tas opp {#what-is-recorded}

- egen bils posisjon (verden, m, dreid til Y opp) 10 ganger i sekundet, med fart, gir, gass og brems
- kjørestart, tilbakestillinger (respawn), runder forbi der kjøringen begynte
- runder, beste runde, distanse, toppfart

## Hvor det kommer fra {#where-it-comes-from}

UDP 127.0.0.1:4460 fra heat3d-protokollmodden (mods/beamng/heat3d i dette repositoriet)

## Slik slår du det på {#how-to-switch-it-on}

`python -m heat3d_watch setup beamng --apply` installerer modden; deretter Options > Other > Protocols > "others"

Skriv kommandoen i en terminal åpnet i watcherens mappe (se [Før du starter](before-you-start.md)). Hvis den feiler, sier siste linje hvorfor; [Installere og kjøre](installing-and-running.md) dekker de vanlige årsakene.

`python -m heat3d_watch setup beamng` lister filene den ville endret; `python -m heat3d_watch setup beamng --apply` endrer dem og beholder originalen som `<fil>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `beamng: changed: ...` for hver endring, eller `beamng: nothing to change` når den allerede er på.

## Slik fungerer det {#how-it-works}

Racingspillenes egen telemetri: Forza, Assetto Corsa-spillene, rallyspillene og BeamNG, tatt opp som ruter, runder og etapper.

Alle spill her publiserer telemetrien sin med vilje, for dashbord og bevegelsesrigger; ingenting injiseres, og ingenting spillet ikke gir ut, leses. Dekodingen er ikke skrevet to ganger: det er gamecapture sine rundeopptakere i 3DHeat GameCapture sin `heat3d_capture/telemetry`, kopiert til `heat3d_watch/decoders` (testet der mot pakker bygd fra de publiserte layoutene), og denne modulen gjør rammene deres om til watcherens rader - bilens posisjon noen ganger i sekundet med fart, gir og pedaler, en hendelse per runde eller etappe, og tallene en sjåfør holder styr på: runder, beste runde, distanse og toppfart.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, slått på i spillets HUD- og spillinnstillinger, til 127.0.0.1 port 5300, format Dash. Én pakke per simuleringstikk; blokkens forskyvning i dash-dataene finnes ut fra pakkene (`forza.detect_layout`). Verdens meter, Y opp; verdenen er venstrehåndet og tegnes slik den sendes, som rundeopptakeren gjør (Forza Motorsports og Forza Horizons "Data Out"-dokumentasjon).
Spillet sender til én port, og FH Companion og andre Data Out-apper lytter på den samme. To programmer kan ikke dele den: på Windows får socketen som er bundet til 127.0.0.1 pakkene, og en som er bundet til alle adresser på samme port får ingen, uansett hvem som kom først. Derfor venter watcheren litt etter at spillet har startet før den tar porten, tar den aldri fra en app som holder den, og slipper den så snart en annen app begynner å lytte der. Mens den holder porten, sender den hver pakke videre uendret til 127.0.0.1:5301 - sett FH Companions portfelt (fanen for telemetri) til 5301, så tar begge opp.

#### BeamNG.drive {#beamngdrive}

Heat3d-protokollmodden som gamecapture leverer (UDP 4460, Options > Other > Protocols > "others"); BeamNGs Z-opp-verden dreid til Y opp, som `beamng.py` gjør.

#### Alt som tas vare på {#everything-kept}

Radene er få i sekundet; spillene sender langt flere. Hver UDP-pakke som kommer inn - i menyene, mellom runder, de en dekoder ikke leser - tas vare på hel i øktens `heat.raw.parquet` under sitt format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), og hver delte minneside (hele området, ikke bare bytene som dekodes) hver gang den endrer seg, under navnet på sitt område (`acpmf_physics`, ...). `used` markerer det som også ble rader; `meta.json`s `selfCheck.completeness` teller hver type (3DHeats konverteringsregel).

Samme modul brukes også av: [Assetto Corsa (direkte data)](game-assetto-corsa.md), [Assetto Corsa Competizione (direkte data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (direkte data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (direkte data)](game-assetto-corsa-rally.md), [DiRT Rally 2.0 (direkte data)](game-dirt-rally-2.md), [EA SPORTS WRC (direkte data)](game-ea-wrc.md), [Forza Horizon 4 (direkte data)](game-forza-horizon-4.md), [Forza Horizon 5 (direkte data)](game-forza-horizon-5.md), [Forza Horizon 6 (direkte data)](game-forza-horizon-6.md), [Forza Motorsport (direkte data)](game-forza-motorsport.md), [Richard Burns Rally (direkte data)](game-richard-burns-rally.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | ja |
| Opp-akse | `y` |
| Enheter | meter (BeamNGs Z-opp-verden dreid om X, slik rundeopptakeren gjør) |
| Speilet for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse legges i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s fotnote, slik at 3DHeat-vieweren selv vender og skalerer radene - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **nei**. `games --markdown` viser dette som "enkeltspiller".
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne spillet publiserer), så den tar opp også i nettspill, ikke bare frakoblet; flagget avgjør bare om minne noensinne får leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `top_speed_kmh`

En nøkkel i klammer fullføres ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt, eller fra spillets egne statistikknavn, står ikke på denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slippes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt tatt vare på med navn; `used` markerer det som også ble rader), og `meta.json`s `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Leses**

- rader 10 ganger i sekundet: posisjon, fart, gir, gass, brems, yaw, turtall, styring; kjørestart, tilbakestillinger, runder

**Tatt vare på rått**

- hver pakke som når porten, hel, med modens 100 Hz: `H3D1` (modens 160-byte struct: klokke, posisjon, hastighet, bilens akser, giringshastighet, ni innganger, overflatehastighet per hjul, rotasjon, last og bakkemateriale), `<n>-byte` for alt annet

**Ikke tilgjengelig**

- det modden ikke sender: BeamNG har ingen fast telemetripakke, så kanalene er de heat3d-modden valgte (andre kjøretøy, skade og kartets navn er ikke med)

**Størrelse**: omtrent 80 MB i timen før komprimering (100 pakker i sekundet på 160 byte pluss en 70-byte elementheader)

## Verifisert {#verified}

dekodingen er rundeopptakerens i gamecapture (testet på pakker bygd fra modens struct); adapteren testet på slike pakker; modden er ikke testet i spillet

## Kilde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
