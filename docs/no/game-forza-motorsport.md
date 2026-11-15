---
title: "Forza Motorsport (live-data)"
nav_order: 24
lang: "no"
source: game-forza-motorsport.md
source_hash: "d411fbb6ebea"
nav_exclude: true
search_exclude: true
---
# Forza Motorsport (live-data) {#forza-motorsport-live-data}

Mens du spiller Forza Motorsport, lagrer watcheren de dataene spillet selv sender ut, slik at du kan se på dem senere på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `forza-motorsport`, type [`telemetry`](sources-and-rules.md); den kjører mens `forza_steamworks_release_final.exe`, `forza_gaming.desktop.x64_release_final.exe` eller `ForzaMotorsport7.exe` kjører, og ser etter nye data hvert 0,1 s.*

## Hva som lagres {#what-is-recorded}

- egen bils posisjon (verdens XYZ, m) 10 ganger i sekundet, med fart, gir, gass, brems og runde
- kjøreøktens start og slutt (session_start/session_end), runder med spillets rundetid
- løpsstart og målgang med posisjonen i løpet
- teleporteringer (spoling tilbake, hurtigreise): `teleport` der bilen var, `spawn` der den er nå
- runder, beste runde, distanse, toppfart, løp

## Hvor dataene kommer fra {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); hver pakke videresendes uendret til 127.0.0.1:5301

## Slik slår du det på {#how-to-switch-it-on}

I spillet: Settings > HUD and Gameplay > Data Out On, IP 127.0.0.1, port 5300 (Motorsport: format Dash). FH Companion eller en annen Data Out-app: sett porten til 5301 - watcheren sender videre hver pakke; mens en annen app lytter på 5300, lar watcheren porten være til den og tar ikke opp noe

## Slik fungerer det {#how-it-works}

Racingspillenes egen telemetri: Forza, Assetto Corsa-spillene, rallyspillene
og BeamNG, lagret som ruter, runder og etapper.

Alle spillene her sender ut telemetrien sin med vilje, til dashbord og bevegelsesrigger;
ingenting blir injisert, og ingenting spillet ikke gir ut, leses. Dekodingen er
ikke skrevet to ganger: det er rundeopptakerne i gamecapture, i 3DHeat GameCapture sin `heat3d_capture/telemetry`, kopiert over til `heat3d_watch/decoders` (testet der mot pakker bygd etter de publiserte oppsettene),
og denne modulen gjør rammene deres om til watcherens rader - bilens posisjon noen
ganger i sekundet med fart, gir og pedaler, en hendelse per runde eller etappe,
og tallene en sjåfør holder styr på: runder, beste runde, distanse, toppfart.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

«Data Out» over UDP, slått på i spillets HUD- og spillinnstillinger, til
127.0.0.1 port 5300, format Dash. Én pakke per simuleringstikk; oppsettet
for dash-blokken finnes ut fra pakkene (`forza.detect_layout`). Verdens meter, Y opp; verdenen er venstrehåndet og tegnes slik den sendes, slik rundeopptakeren gjør
(Forza Motorsport og Forza Horizon sin dokumentasjon for «Data Out»).
Spillet sender til én port, og FH Companion og andre Data Out-apper lytter på
samme. To programmer kan ikke dele den: på Windows får socketen bundet til
127.0.0.1 pakkene, og en som er bundet til alle adresser på samme
port får ingen, uansett hvem som kom først. Derfor venter watcheren litt etter at
spillet har startet før den tar porten, tar den aldri fra en app som holder den,
og gir den fra seg så snart en annen app begynner å lytte der.
Mens den holder porten, sender den hver pakke videre uendret til
127.0.0.1:5301 - sett FH Companion sin portboks (fanen for telemetri) til 5301, så tar begge opp.

#### Alt som lagres {#everything-kept}

Radene er noen få i sekundet; spillene sender langt flere. Hver UDP-pakke som kommer inn - i menyene, mellom runder, og de som ingen dekoder leser - lagres uendret
i øktens `heat.raw.parquet` under sitt format (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), og hver side i delt minne (hele
området, ikke bare de bytene som dekodes) hver gang den endrer seg, under
navnet på området (`acpmf_physics`, ...). `used` markerer det som også ble til
rader; `selfCheck.completeness` i `meta.json` teller hver type (3DHeat sin
regel for konvertering).

Den samme modulen dekker også: [Assetto Corsa (live-data)](game-assetto-corsa.md), [Assetto Corsa Competizione (live-data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (live-data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (live-data)](game-assetto-corsa-rally.md), [BeamNG.drive (live-data)](game-beamng.md), [DiRT Rally 2.0 (live-data)](game-dirt-rally-2.md), [EA SPORTS WRC (live-data)](game-ea-wrc.md), [Forza Horizon 4 (live-data)](game-forza-horizon-4.md), [Forza Horizon 5 (live-data)](game-forza-horizon-5.md), [Forza Horizon 6 (live-data)](game-forza-horizon-6.md), [Richard Burns Rally (live-data)](game-richard-burns-rally.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner lagres | ja |
| Opp-akse | `y` |
| Enheter | meter; Forzas verden er venstrehåndet, og tegnes slik den sendes, slik rundeopptakeren gjør |
| Speilvendt for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet` sin footer, så 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som «tillatt (leser bare det spillet publiserer)».
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne spillet publiserer), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som lagres {#statistics-recorded}

Statistikknøklene denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

En nøkkel i klammeparenteser blir fullført under kjøring (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell med spillets felter eller fra spillets egne statistikknavn, står ikke på listen; «Hva som lagres» over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeat sin [regel for konvertering](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller lagres, og slettes aldri. I tillegg til radene blir hver pakke, side, linje eller respons adapteren mottar, lagret uendret i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt som beholdes med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- rader 10 ganger i sekundet: posisjon, fart, gir, gass, brems, runde, giring, turtall, styring (-1..1); session_start med bilens ordinal, klasse, PI og drivlinje; runder med spillets rundetid; posisjon i løpet

**Lagres uendret**

- hver pakke som når porten, hel, i spillets takt (én per simuleringstikk), under sitt format: `dash-horizon` (324 byte, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: slitasje på dekk og bane-id), `sled` (232, ingen posisjon), `<n>-byte` for alt annet - også menypakker (isRaceOn 0), pakkene som holdes til oppsettet for dash-blokken er bevist, og de ~13 bytene i Horizon-pakken som ingen publisert oppsett nevner
- Sled-blokkens alle kanaler per hjul (slip ratio, slip angle, combined slip, fjæring, hjulfart, rumble, puddle), akselerasjoner, vinkelhastighet, effekt, dreiemoment, boost, drivstoff, dekktemperaturer, kobling, håndbrems, kjørelinje, AI-bremseforskjell: alt i pakkene, dekodet fra dem av `decoders/fulllap.decode_full`

**Ikke tilgjengelig**

- andre biler: Data Out beskriver bare spillerens bil
- navnet på banen eller ruten: Forza Horizon sender aldri ett; Motorsport 2023 sender bare et banenummer
- pakker mens en annen app (FH Companion) holder UDP 5300: watcheren lar porten være til den

**Størrelse**: omtrent 85 MB per time før komprimering (60 pakker i sekundet på 324 byte pluss 70 byte med overskrift per post); påfølgende pakker er lite forskjellige, så zstd beholder en brøkdel av det

## Verifisert {#verified}

dekodingen er rundeopptakerens i gamecapture (testet med pakker bygd etter Data Out-oppsettet); adapteren testet med syntetiske pakker og med innspilte rundebaner avspilt som pakker; ikke testet mot selve spillet

## Kilde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
