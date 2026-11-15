---
title: "Assetto Corsa Rally (direkte data)"
nav_order: 5
lang: "no"
source: game-assetto-corsa-rally.md
source_hash: "09b8a6d66e31"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa Rally (direkte data)

Mens du spiller Assetto Corsa Rally, lagrer watcheren dataene spillet selv sender ut, slik at du senere kan se på dem på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `assetto-corsa-rally`, type [`telemetry`](sources-and-rules.md); den kjører mens `acr.exe`, `ACR-Win64-Shipping.exe`, `AssettoCorsaRally.exe` eller `acrally-Win64-Shipping.exe` går og ser etter nye data hvert 0,1 s.*

## Hva som tas opp

- egen bils posisjon (verdensposisjon XYZ, m: gjennomsnittet av dekkenes kontaktpunkter) 10 ganger i sekundet, med fart, gir, gass og brems
- øktstart og -slutt med banen og bilen spillet oppgir
- etapper: en slutter der bilen stopper etter den, med tiden den tok
- teleporteringer (tilbake til boksen, en omstart): `teleport` der bilen var, `spawn` der den er nå
- runder, beste runde, distanse, toppfart

## Hvor det kommer fra

delt minne Local\acpmf_physics, Local\acpmf_static (de samme sidene som AC og ACC)

## Slik slår du det på

Ingenting må slås på: watcheren leser kilden slik spillet eller plattformen gir den.

## Slik fungerer det

Racingspillenes egen telemetri: Forza, Assetto Corsa-spillene, rallyspillene og BeamNG, tatt opp som ruter, runder og etapper.

Alle spill her publiserer telemetrien sin med vilje, for dashbord og bevegelsesrigger; ingenting injiseres, og ingenting spillet ikke gir ut, leses. Dekodingen er ikke skrevet to ganger: det er gamecapture sine rundeopptakere i 3DHeat GameCapture sin `heat3d_capture/telemetry`, kopiert til `heat3d_watch/decoders` (testet der mot pakker bygd fra de publiserte layoutene), og denne modulen gjør rammene deres om til watcherens rader - bilens posisjon noen ganger i sekundet med fart, gir og pedaler, en hendelse per runde eller etappe, og tallene en sjåfør holder styr på: runder, beste runde, distanse og toppfart.

#### Forza (Horizon 4/5/6, Motorsport)

"Data Out" UDP, slått på i spillets HUD- og spillinnstillinger, til 127.0.0.1 port 5300, format Dash. Én pakke per simuleringstikk; blokkens forskyvning i dash-dataene finnes ut fra pakkene (`forza.detect_layout`). Verdens meter, Y opp; verdenen er venstrehåndet og tegnes slik den sendes, som rundeopptakeren gjør (Forza Motorsports og Forza Horizons "Data Out"-dokumentasjon).
Spillet sender til én port, og FH Companion og andre Data Out-apper lytter på den samme. To programmer kan ikke dele den: på Windows får socketen som er bundet til 127.0.0.1 pakkene, og en som er bundet til alle adresser på samme port får ingen, uansett hvem som kom først. Derfor venter watcheren litt etter at spillet har startet før den tar porten, tar den aldri fra en app som holder den, og slipper den så snart en annen app begynner å lytte der. Mens den holder porten, sender den hver pakke videre uendret til 127.0.0.1:5301 - sett FH Companions portfelt (fanen for telemetri) til 5301, så tar begge opp.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally

UDP: WRCs `Documents/My Games/WRC/telemetry/config.json` (strukturen `wrc`s `session_update`-pakke), DiRTs `hardware_settings_config.xml` (`<udp enabled="true" extradata="3" port="20777">`), RBRs NGP-plugin (`udpTelemetry=1`, port 6776). Etapper etter spillets etappeklokke (`rally.StageSplitter`). RBR dokumenterer ikke sine akser: opp-aksen er den aksen etappen varierer minst langs, avgjort når økten avsluttes.

#### Alt som tas vare på

Radene er få i sekundet; spillene sender langt flere. Hver UDP-pakke som kommer inn - i menyene, mellom runder, de en dekoder ikke leser - tas vare på hel i øktens `heat.raw.parquet` under sitt format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), og hver delte minneside (hele området, ikke bare bytene som dekodes) hver gang den endrer seg, under navnet på sitt område (`acpmf_physics`, ...). `used` markerer det som også ble rader; `meta.json`s `selfCheck.completeness` teller hver type (3DHeats konverteringsregel).

Samme modul brukes også av: [Assetto Corsa (direkte data)](game-assetto-corsa.md), [Assetto Corsa Competizione (direkte data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (direkte data)](game-assetto-corsa-evo.md), [BeamNG.drive (direkte data)](game-beamng.md), [DiRT Rally 2.0 (direkte data)](game-dirt-rally-2.md), [EA SPORTS WRC (direkte data)](game-ea-wrc.md), [Forza Horizon 4 (direkte data)](game-forza-horizon-4.md), [Forza Horizon 5 (direkte data)](game-forza-horizon-5.md), [Forza Horizon 6 (direkte data)](game-forza-horizon-6.md), [Forza Motorsport (direkte data)](game-forza-motorsport.md), [Richard Burns Rally (direkte data)](game-richard-burns-rally.md).

## Posisjoner og akser

| | |
|---|---|
| Posisjoner tatt opp | ja |
| Opp-akse | `y` |
| Enheter | meter |
| Speilet for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse legges i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s fotnote, slik at 3DHeat-vieweren selv vender og skalerer radene - se [Dataene](the-data.md).

## Flerspiller

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "tillatt (leser bare det spillet publiserer)".
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne spillet publiserer), så den tar opp også i nettspill, ikke bare frakoblet; flagget avgjør bare om minne noensinne får leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres

Statistikknøkler som adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

En nøkkel i klammer fullføres ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt, eller fra spillets egne statistikknavn, står ikke på denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slippes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt tatt vare på med navn; `used` markerer det som også ble rader), og `meta.json`s `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Leses**

- rader 10 ganger i sekundet fra fysikksiden: posisjon (gjennomsnitt av dekkenes kontaktpunkter), fart, gir, gass, brems, yaw/pitch/roll (rad), turtall, styring (slik siden har den); øktstart med bane og bil fra den statiske siden; runder, posisjon i løpet

**Tatt vare på rått**

- hver side hel - hele minneområdet, ikke bare bytene som dekodes - hver gang bytene endrer seg, ved watcherens lesing 10 ganger i sekundet: `acpmf_physics`, `acpmf_static`; en lesing som er byte for byte den forrige, telles i meta.jsons `unchanged_reads` og lagres ikke på nytt
- alt som dekodes bare for rundefiler (`decoders/kunos.py`: slip per hjul, last, trykk, temperaturer, camber, fjæring, kontaktpunkter, bremsetemperaturer, slipforhold og slipvinkel; verdens- og lokal hastighet, vinkelhastighet, hjelpemidler) ligger på disse sidene

**Ikke tilgjengelig**

- andre biler' posisjoner: sidene beskriver bare spillerens bil (ACCs grafikkside har bil-id-er og koordinater for andre i noen versjoner - tatt vare på i den rå siden, ikke dekodet)
- fysikk-tikk mellom watcherens lesinger: spillet skriver siden om med sin fysikkrate (opptil 333 Hz), og watcheren leser 10 ganger i sekundet
- en etappeklokke eller spillets etappetid: AC Rally publiserer ingen grafikkside; etapper slutter der bilen stopper

**Størrelse**: omtrent 150-300 MB i timen før komprimering (et 4 KB-område per side, opptil 10 endringer i sekundet); sidene er stort sett nuller, og zstd beholder en liten brøkdel

## Verifisert

dekodingen er rundeopptakerens i gamecapture (testet på syntetiske sider); adapteren testet på delt minne bygd i testen fra den dokumenterte layouten; ikke testet mot spillet; kjørbar-filnavnet er ikke bekreftet

## Kilde

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
