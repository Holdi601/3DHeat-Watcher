---
title: "Richard Burns Rally (direkte data)"
nav_order: 38
lang: "no"
source: game-richard-burns-rally.md
source_hash: "4f2a2e46f8c8"
nav_exclude: true
search_exclude: true
---
# Richard Burns Rally (direkte data) {#richard-burns-rally-live-data}

Mens du spiller Richard Burns Rally, lagrer watcheren dataene spillet selv sender ut, slik at du senere kan se på dem på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `richard-burns-rally`, type [`telemetry`](sources-and-rules.md); den kjører mens `RichardBurnsRally_SSE.exe` eller `RichardBurnsRally.exe` går og ser etter nye data hvert 0,1 s.*

## Hva som tas opp {#what-is-recorded}

- egen bils posisjon (verdensposisjon XYZ, m) 10 ganger i sekundet, med fart, gir, gass, brems og etappedistanse
- etappestart (etappeklokken starter), målgang med etappetid, omstarter
- teleporteringer (en tilbakestilling til veien): `teleport` der bilen var, `spawn` der den er nå
- etapper, beste etappetid, distanse, toppfart

## Hvor det kommer fra {#where-it-comes-from}

NGP-pluginens UDP-telemetri, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1)

## Slik slår du det på {#how-to-switch-it-on}

RSF/NGP: i RichardBurnsRally.ini, under seksjonen [NGP], sett udpTelemetry=1 og endepunktet til 127.0.0.1:6776

## Slik fungerer det {#how-it-works}

Racingspillenes egen telemetri: Forza, Assetto Corsa-spillene, rallyspillene og BeamNG, tatt opp som ruter, runder og etapper.

Alle spill her publiserer telemetrien sin med vilje, for dashbord og bevegelsesrigger; ingenting injiseres, og ingenting spillet ikke gir ut, leses. Dekodingen er ikke skrevet to ganger: det er gamecapture sine rundeopptakere i 3DHeat GameCapture sin `heat3d_capture/telemetry`, kopiert til `heat3d_watch/decoders` (testet der mot pakker bygd fra de publiserte layoutene), og denne modulen gjør rammene deres om til watcherens rader - bilens posisjon noen ganger i sekundet med fart, gir og pedaler, en hendelse per runde eller etappe, og tallene en sjåfør holder styr på: runder, beste runde, distanse og toppfart.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, slått på i spillets HUD- og spillinnstillinger, til 127.0.0.1 port 5300, format Dash. Én pakke per simuleringstikk; blokkens forskyvning i dash-dataene finnes ut fra pakkene (`forza.detect_layout`). Verdens meter, Y opp; verdenen er venstrehåndet og tegnes slik den sendes, som rundeopptakeren gjør (Forza Motorsports og Forza Horizons "Data Out"-dokumentasjon).
Spillet sender til én port, og FH Companion og andre Data Out-apper lytter på den samme. To programmer kan ikke dele den: på Windows får socketen som er bundet til 127.0.0.1 pakkene, og en som er bundet til alle adresser på samme port får ingen, uansett hvem som kom først. Derfor venter watcheren litt etter at spillet har startet før den tar porten, tar den aldri fra en app som holder den, og slipper den så snart en annen app begynner å lytte der. Mens den holder porten, sender den hver pakke videre uendret til 127.0.0.1:5301 - sett FH Companions portfelt (fanen for telemetri) til 5301, så tar begge opp.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: WRCs `Documents/My Games/WRC/telemetry/config.json` (strukturen `wrc`s `session_update`-pakke), DiRTs `hardware_settings_config.xml` (`<udp enabled="true" extradata="3" port="20777">`), RBRs NGP-plugin (`udpTelemetry=1`, port 6776). Etapper etter spillets etappeklokke (`rally.StageSplitter`). RBR dokumenterer ikke sine akser: opp-aksen er den aksen etappen varierer minst langs, avgjort når økten avsluttes.

#### Alt som tas vare på {#everything-kept}

Radene er få i sekundet; spillene sender langt flere. Hver UDP-pakke som kommer inn - i menyene, mellom runder, de en dekoder ikke leser - tas vare på hel i øktens `heat.raw.parquet` under sitt format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), og hver delte minneside (hele området, ikke bare bytene som dekodes) hver gang den endrer seg, under navnet på sitt område (`acpmf_physics`, ...). `used` markerer det som også ble rader; `meta.json`s `selfCheck.completeness` teller hver type (3DHeats konverteringsregel).

Samme modul brukes også av: [Assetto Corsa (direkte data)](game-assetto-corsa.md), [Assetto Corsa Competizione (direkte data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (direkte data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (direkte data)](game-assetto-corsa-rally.md), [BeamNG.drive (direkte data)](game-beamng.md), [DiRT Rally 2.0 (direkte data)](game-dirt-rally-2.md), [EA SPORTS WRC (direkte data)](game-ea-wrc.md), [Forza Horizon 4 (direkte data)](game-forza-horizon-4.md), [Forza Horizon 5 (direkte data)](game-forza-horizon-5.md), [Forza Horizon 6 (direkte data)](game-forza-horizon-6.md), [Forza Motorsport (direkte data)](game-forza-motorsport.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | ja |
| Opp-akse | `y` |
| Enheter | meter; opp-akse avgjort fra kjøringen (RBR dokumenterer ikke sine akser) |
| Speilet for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse legges i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s fotnote, slik at 3DHeat-vieweren selv vender og skalerer radene - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **nei**. `games --markdown` viser dette som "enkeltspiller".
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne spillet publiserer), så den tar opp også i nettspill, ikke bare frakoblet; flagget avgjør bare om minne noensinne får leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

En nøkkel i klammer fullføres ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt, eller fra spillets egne statistikknavn, står ikke på denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slippes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt tatt vare på med navn; `used` markerer det som også ble rader), og `meta.json`s `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Leses**

- rader 10 ganger i sekundet: posisjon, fart, gir, gass, brems, etappedistanse, yaw, turtall, styring; etappestart, målgang med etappetid, omstarter

**Tatt vare på rått**

- hver pakke som når porten, hel, i spillets rate, under sitt format: `telemetry` (NGPs 664-byte TelemetryData), `rbr <n>-byte` ellers
- i pakken utover radene: holdning, bilens egne hastigheter og akselerasjoner, fjærutslag og kraft per hjul, etappens fremdrift og distanse til slutt; resten av de 664 bytene (motor-, dekk- og bremseblokker per hjul) er ikke dekodet noe sted ennå

**Ikke tilgjengelig**

- andre biler: spillene sender bare spillerens bil
- dens fartsenhet og akser: ikke dokumentert - fart tas fra posisjonene, opp fra kjøringen

**Størrelse**: omtrent 160 MB i timen ved 60 pakker i sekundet (664 byte pluss en 70-byte elementheader); zstd beholder en brøkdel

## Verifisert {#verified}

dekodingen er rundeopptakerens i gamecapture (testet på pakker bygd fra de dokumenterte layoutene); adapteren testet på pakker bygd i testen og sendt over UDP; ikke testet mot spillet

## Kilde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
