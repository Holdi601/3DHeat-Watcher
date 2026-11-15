---
title: "Assetto Corsa EVO (livedata)"
nav_order: 4
lang: "sv"
source: game-assetto-corsa-evo.md
source_hash: "b14d46c10e85"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa EVO (livedata) {#assetto-corsa-evo-live-data}

När du kör Assetto Corsa EVO sparar watchern den data som spelet själv skickar ut, så att du senare kan titta på den på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `assetto-corsa-evo`, slag [`telemetry`](sources-and-rules.md); den körs medan `AssettoCorsaEVO.exe` är igång och letar efter ny data var 0,1 s.*

## Vad som spelas in {#what-is-recorded}

- egen bils position (världens XYZ, m: medelvärdet av däckens kontaktpunkter) 10 gånger per sekund, med hastighet, växel, gas och broms
- sessionens start och slut, med banan och bilen som spelet anger
- varv när bilen passerar där körningen började, i samma riktning
- teleporteringar (tillbaka till depån, en omstart): `teleport` där bilen var, `spawn` där den är nu
- varv, bästa varv, sträcka, högsta hastighet

## Var datan kommer ifrån {#where-it-comes-from}

delat minne Local\acevo_pmf_physics, Local\acevo_pmf_static

## Så slår du på det {#how-to-switch-it-on}

Inget behöver slås på: watchern läser källan så som spelet eller plattformen tillhandahåller den.

## Så fungerar det {#how-it-works}

Racingspelens egen telemetri: Forza, Assetto Corsa-spelen, rallyspelen och BeamNG, sparad som rutter, varv och etapper.

Varje spel här publicerar sin telemetri med avsikt, för instrumentpaneler och rörelseplattformar; ingenting injiceras och inget som spelet inte lämnar ut läses. Avkodningen skrivs inte två gånger: det är gamecapture-varvinspelarna i 3DHeat GameCapture:s `heat3d_capture/telemetry`, kopierade till `heat3d_watch/decoders` (testade där mot paket byggda från de publicerade layouterna), och den här modulen gör deras bildrutor till watcherns rader - bilens position några gånger per sekund med hastighet, växel och pedaler, en händelse per varv eller etapp, och de siffror en förare behåller: varv, bästa varv, sträcka, högsta hastighet.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" över UDP, påslaget i spelets HUD- och Gameplay-inställningar, till 127.0.0.1 port 5300, format Dash. Ett paket per simuleringstick; blockets offset för instrumentpanelen hittas ur paketen (`forza.detect_layout`). Världen i meter, Y uppåt; världen är vänsterhänt och ritas så som den skickas, precis som varvinspelaren gör (Forza Motorsports och Forza Horizons dokumentation för "Data Out"). Spelet skickar till en port, och FH Companion och andra Data Out-appar lyssnar på samma. Två program kan inte dela den: på Windows får uttaget bundet till 127.0.0.1 paketen och ett bundet till alla adresser på samma port får inga, oavsett vilket som startade först. Därför väntar watchern en stund efter att spelet startat innan den tar porten, tar aldrig den från en app som håller den, och släpper den så fort en annan app börjar lyssna där. Medan den håller porten skickar den varje paket oförändrat vidare till 127.0.0.1:5301 - ställ FH Companions portruta (dess telemetriflik) på 5301 så spelar båda in.

#### Allt sparas {#everything-kept}

Raderna är några per sekund; spelen skickar mycket mer. Varje UDP-paket som kommer fram - i menyerna, mellan varven, de som ingen avkodare läser - sparas helt i sessionens `heat.raw.parquet` under sitt format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), och varje sida i delat minne (hela mappningen, inte bara de byte som avkodats) varje gång den ändras, under mappningens namn (`acpmf_physics`, ...). `used` markerar det som också blev rader; `meta.json`:s `selfCheck.completeness` räknar varje slag (3DHeats konverterarregel).

Samma modul används också av: [Assetto Corsa (livedata)](game-assetto-corsa.md), [Assetto Corsa Competizione (livedata)](game-assetto-corsa-competizione.md), [Assetto Corsa Rally (livedata)](game-assetto-corsa-rally.md), [BeamNG.drive (livedata)](game-beamng.md), [DiRT Rally 2.0 (livedata)](game-dirt-rally-2.md), [EA SPORTS WRC (livedata)](game-ea-wrc.md), [Forza Horizon 4 (livedata)](game-forza-horizon-4.md), [Forza Horizon 5 (livedata)](game-forza-horizon-5.md), [Forza Horizon 6 (livedata)](game-forza-horizon-6.md), [Forza Motorsport (livedata)](game-forza-motorsport.md), [Richard Burns Rally (livedata)](game-richard-burns-rally.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Upp-axel | `y` |
| Enheter | meter |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "allowed (reads only what the game publishes)".
- Slag `telemetry`: den läser bara det spelet eller plattformen lämnar ut (en UDP-port eller delat minne som spelet publicerar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- rader 10 gånger per sekund från fysiksidan: position (medelvärdet av däckens kontaktpunkter), hastighet, växel, gas, broms, yaw/pitch/roll (radianer), varvtal, styrning (så som sidan har den); sessionens start med banan och bilen från den statiska sidan; varv, placering

**Sparas råa**

- varje sida helt - hela mappningsområdet, inte bara de byte som avkodats - varje gång dess byte ändras, vid watchens läsning 10 gånger per sekund: `acevo_pmf_physics`, `acevo_pmf_static`; en omläsning som är byte för byte den förra räknas i meta.json:s `unchanged_reads`, och lagras inte igen
- allt som avkodats bara för varvfiler (`decoders/kunos.py`: slip, last, tryck, temperaturer, camber, fjädring, kontaktpunkter, bromstemperaturer, slip ratio och vinkel per hjul; värld- och lokal hastighet, vinkelhastighet, hjälpmedel) finns i de sidorna

**Finns inte**

- andra bilars positioner: sidorna beskriver bara spelarens bil (ACC:s grafiksida har bil-id och koordinater för andra i vissa versioner - sparas i den råa sidan, avkodas inte)
- fysiktick mellan watchens läsningar: spelet skriver om sidan i sin fysikfrekvens (upp till 333 Hz) och watchen läser 10 gånger per sekund
- en varvräknare eller spelets varvtid: AC EVO:s sidor som de läses har ingen grafiksida; varv delas efter position

**Storlek**: ungefär 150-300 MB per timme före komprimering (en 4 KB-region per sida, upp till 10 ändringar per sekund); sidorna är mestadels nollor och zstd behåller en liten bråkdel

## Verifierat {#verified}

avkodningen är gamecapture-varvinspelarens (testad på syntetiska sidor); adaptern testad på delat minne byggt i testet från den dokumenterade layouten; ännu inte testad mot spelet; körbara filens namn är från spelares rapporter

## Källa {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
