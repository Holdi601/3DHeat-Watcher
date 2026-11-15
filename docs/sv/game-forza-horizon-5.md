---
title: "Forza Horizon 5 (livedata)"
nav_order: 22
lang: "sv"
source: game-forza-horizon-5.md
source_hash: "0083724478e7"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 5 (livedata) {#forza-horizon-5-live-data}

När du spelar Forza Horizon 5 sparar watchern den data som spelet själv skickar ut, så att du senare kan titta på den på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `forza-horizon-5`, slag [`telemetry`](sources-and-rules.md); den körs medan `ForzaHorizon5.exe` är igång och letar efter ny data var 0,1 s.*

## Vad som spelas in {#what-is-recorded}

- egen bils position (världens XYZ, m) 10 gånger per sekund, med hastighet, växel, gas, broms och varv
- körningens start och slut (session_start/session_end), varv med spelets varvtid
- race-start och målgång med placeringen
- teleporteringar (spola tillbaka, snabbresa): `teleport` där bilen var, `spawn` där den är nu
- varv, bästa varv, sträcka, högsta hastighet, lopp

## Var datan kommer ifrån {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); varje paket skickas oförändrat vidare till 127.0.0.1:5301

## Så slår du på det {#how-to-switch-it-on}

I spelet: Inställningar > HUD och spelmoment > Data Out På, IP 127.0.0.1, port 5300 (Motorsport: format Dash). FH Companion eller en annan Data Out-app: sätt dess port till 5301 - watchern skickar vidare varje paket; medan en annan app lyssnar på 5300 lämnar watchern porten åt den och spelar inte in något

## Så fungerar det {#how-it-works}

Racingspelens egen telemetri: Forza, Assetto Corsa-spelen, rallyspelen
och BeamNG, sparad som rutter, varv och etapper.

Varje spel här publicerar sin telemetri med avsikt, för instrumentpaneler och
rörelseplattformar; ingenting injiceras och inget som spelet inte lämnar ut läses. Avkodningen
skrivs inte två gånger: det är gamecapture-varvinspelarna i 3DHeat GameCapture:s `heat3d_capture/telemetry`,
kopierade till `heat3d_watch/decoders` (testade där mot paket byggda från
de publicerade layouterna), och den här modulen gör deras bildrutor till watcherns
rader - bilens position några gånger per sekund med hastighet, växel och pedaler,
en händelse per varv eller etapp, och de siffror en förare för kolla: varv, bästa varv,
sträcka, högsta hastighet.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" över UDP, påslaget i spelets HUD- och Gameplay-inställningar, till
127.0.0.1 port 5300, format Dash. Ett paket per simuleringstick; blockets offset för
instrumentpanelen hittas ur paketen (`forza.detect_layout`). Världen i meter, Y uppåt; världen är
vänsterhänt och ritas så som den skickas, precis som varvinspelaren gör (Forza Motorsports och Forza
Horizons dokumentation för "Data Out"). Spelet skickar till en port, och FH Companion och andra
Data Out-appar lyssnar på samma. Två program kan inte dela den: på Windows får uttaget
bundet till 127.0.0.1 paketen och ett bundet till alla adresser på samma port får inga, oavsett
vilket som startade först. Därför väntar watchern en stund efter att spelet startat innan den tar
porten, tar aldrig den från en app som håller den, och släpper den så fort en annan app
börjar lyssna där. Medan den håller porten skickar den varje paket oförändrat vidare till
127.0.0.1:5301 - ställ FH Companions portruta (dess telemetrifliken) på 5301 så spelar båda in.

#### Allt sparas {#everything-kept}

Raderna är några per sekund; spelen skickar mycket mer. Varje UDP-paket som
kommer fram - i menyerna, mellan varven, de som ingen avkodare läser - sparas helt
i sessionens `heat.raw.parquet` under sitt format (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), och varje sida i delat minne
(hela mappningen, inte bara de byte som avkodats) varje gång den ändras, under
mappningens namn (`acpmf_physics`, ...). `used` markerar det som också blev
rader; `meta.json`:s `selfCheck.completeness` räknar varje slag (3DHeats
konverterarregel).

Samma modul används också av: [Assetto Corsa (livedata)](game-assetto-corsa.md), [Assetto Corsa Competizione (livedata)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (livedata)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (livedata)](game-assetto-corsa-rally.md), [BeamNG.drive (livedata)](game-beamng.md), [DiRT Rally 2.0 (livedata)](game-dirt-rally-2.md), [EA SPORTS WRC (livedata)](game-ea-wrc.md), [Forza Horizon 4 (livedata)](game-forza-horizon-4.md), [Forza Horizon 6 (livedata)](game-forza-horizon-6.md), [Forza Motorsport (livedata)](game-forza-motorsport.md), [Richard Burns Rally (livedata)](game-richard-burns-rally.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Upp-axel | `y` |
| Enheter | meter; Forzas värld är vänsterhänt, ritas så som den skickas, precis som varvinspelaren gör |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåtet (läser bara det spelet publicerar)".
- Slag `telemetry`: den läser bara det spelet eller plattformen lämnar ut (en UDP-port eller delat minne som spelet publicerar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- rader 10 gånger per sekund: position, hastighet, växel, gas, broms, varv, yaw/pitch/roll (rad), varvtal, styrning (-1..1); session_start med bilens ordningsnummer, klass, PI och drivlina; varv med spelets varvtid; placering i loppet

**Sparas råa**

- varje paket som når porten, helt, i spelets takt (ett per simuleringstick), under sitt format: `dash-horizon` (324 byte, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: däckslitage och bana-id), `sled` (232, ingen position), `<n>-byte` för allt annat - även menypaket (isRaceOn 0), paketen som hålls tills instrumentpanelens layout är bevisad, och de ~13 byte i Horizon-paketet som ingen publicerad layout namnger
- Sled-blockets alla hjulkanaler (slip ratio, slip-vinkel, kombinerad slip, fjädring, hjulhastighet, rumble, puddle), accelerationer, vinkelhastighet, effekt, vridmoment, boost, bränsle, däcktemperaturer, koppling, handbroms, körlinje, AI:s bromsdifferens: allt finns i paketen, avkodat av `decoders/fulllap.decode_full` ur dem

**Finns inte**

- andra bilar: Data Out beskriver bara spelarens bil
- bane- eller ruttnamnet: Forza Horizon skickar aldrig något; Motorsport 2023 skickar bara ett banenummer
- paket medan en annan app (FH Companion) håller UDP 5300: watchern lämnar porten åt den

**Storlek**: ungefär 85 MB per timme före komprimering (60 paket per sekund à 324 byte plus 70 byte paketrubrik); på varandra följande paket skiljer sig lite, så zstd behåller en bråkdel

## Verifierat {#verified}

avkodningen är gamecapture-varvinspelarens (testad på paket byggda från Data Out-layouten); adaptern testad på syntetiska paket och på inspelade varvbanor spelade upp som paket; ännu inte testad mot spelet självt

## Källa {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
