---
title: "BeamNG.drive (livedata)"
nav_order: 7
lang: "sv"
source: game-beamng.md
source_hash: "1c23a869a62f"
nav_exclude: true
search_exclude: true
---
# BeamNG.drive (livedata) {#beamngdrive-live-data}

När du kör BeamNG.drive sparar watchern den data som spelet själv skickar ut, så att du senare kan titta på den på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `beamng`, slag [`telemetry`](sources-and-rules.md); den körs medan `BeamNG.drive.x64.exe` eller `BeamNG.drive.exe` är igång och letar efter ny data var 0,1 s.*

## Vad som spelas in {#what-is-recorded}

- egen bils position (världen, m, vriden till Y upp) 10 gånger per sekund med hastighet, växel, gas, broms
- körningens start, återställningar (respawn), varv förbi där körningen började
- varv, bästa varv, sträcka, högsta hastighet

## Var datan kommer ifrån {#where-it-comes-from}

UDP 127.0.0.1:4460 från heat3d-protokollmodden (mods/beamng/heat3d i det här förrådet)

## Så slår du på det {#how-to-switch-it-on}

`python -m heat3d_watch setup beamng --apply` installerar modden; sedan Options > Other > Protocols > "others"

Skriv kommandot i en terminal som öppnats i watcherns mapp (se [Innan du börjar](before-you-start.md)). Om det misslyckas säger den sista raden varför; [Installation och körning](installing-and-running.md) går igenom de vanliga orsakerna.

`python -m heat3d_watch setup beamng` listar filerna det skulle ändra; `python -m heat3d_watch setup beamng --apply` ändrar dem och sparar originalet som `<file>.heat3d-backup` (se [Kommandon](commands.md#setup)). Den skriver `beamng: changed: ...` för varje ändring, eller `beamng: nothing to change` när den redan är påslagen.

## Så fungerar det {#how-it-works}

Racingspelens egen telemetri: Forza, Assetto Corsa-spelen, rallyspelen och BeamNG, sparad som rutter, varv och etapper.

Varje spel här publicerar sin telemetri med avsikt, för instrumentpaneler och rörelseplattformar; ingenting injiceras och inget som spelet inte lämnar ut läses. Avkodningen skrivs inte två gånger: det är gamecapture-varvinspelarna i 3DHeat GameCapture:s `heat3d_capture/telemetry`, kopierade till `heat3d_watch/decoders` (testade där mot paket byggda från de publicerade layouterna), och den här modulen gör deras bildrutor till watcherns rader - bilens position några gånger per sekund med hastighet, växel och pedaler, en händelse per varv eller etapp, och de siffror en förare behåller: varv, bästa varv, sträcka, högsta hastighet.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" över UDP, påslaget i spelets HUD- och Gameplay-inställningar, till 127.0.0.1 port 5300, format Dash. Ett paket per simuleringstick; blockets offset för instrumentpanelen hittas ur paketen (`forza.detect_layout`). Världen i meter, Y uppåt; världen är vänsterhänt och ritas så som den skickas, precis som varvinspelaren gör (Forza Motorsports och Forza Horizons dokumentation för "Data Out"). Spelet skickar till en port, och FH Companion och andra Data Out-appar lyssnar på samma. Två program kan inte dela den: på Windows får uttaget bundet till 127.0.0.1 paketen och ett bundet till alla adresser på samma port får inga, oavsett vilket som startade först. Därför väntar watchern en stund efter att spelet startat innan den tar porten, tar aldrig den från en app som håller den, och släpper den så fort en annan app börjar lyssna där. Medan den håller porten skickar den varje paket oförändrat vidare till 127.0.0.1:5301 - ställ FH Companions portruta (dess telemetriflik) på 5301 så spelar båda in.

#### BeamNG.drive {#beamngdrive}

Protokollmodden `heat3d` som gamecapture levererar (UDP 4460, Options > Other > Protocols > "others"); BeamNG:s Z-upp-värld vrids till Y upp så som `beamng.py` gör.

#### Allt sparas {#everything-kept}

Raderna är några per sekund; spelen skickar mycket mer. Varje UDP-paket som kommer fram - i menyerna, mellan varven, de som ingen avkodare läser - sparas helt i sessionens `heat.raw.parquet` under sitt format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), och varje sida i delat minne (hela mappningen, inte bara de byte som avkodats) varje gång den ändras, under mappningens namn (`acpmf_physics`, ...). `used` markerar det som också blev rader; `meta.json`:s `selfCheck.completeness` räknar varje slag (3DHeats konverterarregel).

Samma modul används också av: [Assetto Corsa (livedata)](game-assetto-corsa.md), [Assetto Corsa Competizione (livedata)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (livedata)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (livedata)](game-assetto-corsa-rally.md), [DiRT Rally 2.0 (livedata)](game-dirt-rally-2.md), [EA SPORTS WRC (livedata)](game-ea-wrc.md), [Forza Horizon 4 (livedata)](game-forza-horizon-4.md), [Forza Horizon 5 (livedata)](game-forza-horizon-5.md), [Forza Horizon 6 (livedata)](game-forza-horizon-6.md), [Forza Motorsport (livedata)](game-forza-motorsport.md), [Richard Burns Rally (livedata)](game-richard-burns-rally.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Upp-axel | `y` |
| Enheter | meter (BeamNG:s Z-upp-värld vriden kring X, precis som varvinspelaren gör) |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **nej**. `games --markdown` visar detta som "single-player".
- Slag `telemetry`: den läser bara det spelet eller plattformen lämnar ut (en UDP-port eller delat minne som spelet publicerar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `top_speed_kmh`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- rader 10 gånger per sekund: position, hastighet, växel, gas, broms, yaw, varvtal, styrning; körningens start, återställningar, varv

**Sparas råa**

- varje paket som når porten, helt, i modden 100 Hz: `H3D1` (modens 160-byte-struktur: klocka, position, hastighet, bilens axlar, yaw-hastighet, nio reglage, ytans hastighet per hjul, rotation, last och underlagsmaterial), `<n>-byte` för allt annat

**Finns inte**

- det modden inte skickar: BeamNG har inget fast telemetripaket, så kanalerna är de som heat3d-modden valt (andra fordon, skador, kartans namn ingår inte)

**Storlek**: ungefär 80 MB per timme före komprimering (100 paket per sekund på 160 byte plus ett 70-byte objektshuvud)

## Verifierat {#verified}

avkodningen är gamecapture-varvinspelarens (testad på paket byggda från modens struktur); adaptern testad på sådana paket; modden är ännu inte testad i spelet

## Källa {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
