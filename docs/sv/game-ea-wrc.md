---
title: "EA SPORTS WRC (livedata)"
nav_order: 17
lang: "sv"
source: game-ea-wrc.md
source_hash: "c97300f65c43"
nav_exclude: true
search_exclude: true
---
# EA SPORTS WRC (livedata) {#ea-sports-wrc-live-data}

När du kör EA SPORTS WRC sparar watchern den data som spelet själv skickar ut, så att du senare kan titta på den på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `ea-wrc`, slag [`telemetry`](sources-and-rules.md); den körs medan `WRC.exe` är igång och letar efter ny data var 0,1 s.*

## Vad som spelas in {#what-is-recorded}

- egen bils position (världens XYZ, m) 10 gånger per sekund, med hastighet, växel, gas, broms och sträcka i etappen
- etappstart (när etappklockan startar), målgång med etappens tid, omstarter
- teleporteringar (en återställning till vägen): `teleport` där bilen var, `spawn` där den är nu
- etapper, bästa etapptid, sträcka, högsta hastighet

## Var datan kommer ifrån {#where-it-comes-from}

UDP 127.0.0.1:20777, standardstrukturen `wrc`:s session_update-paket (Dokument\My Games\WRC\telemetry\config.json); medan en annan app håller 20777 lämnar watchern porten åt den

## Så slår du på det {#how-to-switch-it-on}

`python -m heat3d_watch setup ea-wrc --apply` slår på session_update-paketet i config.json (säkerhetskopia tas först)

Skriv kommandot i en terminal som öppnats i watcherns mapp (se [Innan du börjar](before-you-start.md)). Om det misslyckas säger sista raden varför; [Installera och köra](installing-and-running.md) går igenom de vanliga orsakerna.

`python -m heat3d_watch setup ea-wrc` listar vilka filer den skulle ändra; `python -m heat3d_watch setup ea-wrc --apply` ändrar dem och sparar originalet som `<fil>.heat3d-backup` (se [Kommandon](commands.md#setup)). Den skriver `ea-wrc: changed: ...` för varje ändring, eller `ea-wrc: nothing to change` när den redan är påslagen.

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

#### DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: WRC:s `Dokument/My Games/WRC/telemetry/config.json` (`wrc`-strukturens
`session_update`-paket), DiRT:s `hardware_settings_config.xml`
(`<udp enabled="true" extradata="3" port="20777">`), RBR:s NGP-plugin
(`udpTelemetry=1`, port 6776). Etapper enligt spelets etappklocka
(`rally.StageSplitter`). RBR dokumenterar inte sina axlar: upp-axeln är
den som etappen varierar minst längs, avgjort när sessionen stängs.

#### Allt sparas {#everything-kept}

Raderna är några per sekund; spelen skickar mycket mer. Varje UDP-paket som
kommer fram - i menyerna, mellan varven, de som ingen avkodare läser - sparas helt
i sessionens `heat.raw.parquet` under sitt format (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), och varje sida i delat minne
(hela mappningen, inte bara de byte som avkodats) varje gång den ändras, under
mappningens namn (`acpmf_physics`, ...). `used` markerar det som också blev
rader; `meta.json`:s `selfCheck.completeness` räknar varje slag (3DHeats
konverterarregel).

Samma modul används också av: [Assetto Corsa (livedata)](game-assetto-corsa.md), [Assetto Corsa Competizione (livedata)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (livedata)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (livedata)](game-assetto-corsa-rally.md), [BeamNG.drive (livedata)](game-beamng.md), [DiRT Rally 2.0 (livedata)](game-dirt-rally-2.md), [Forza Horizon 4 (livedata)](game-forza-horizon-4.md), [Forza Horizon 5 (livedata)](game-forza-horizon-5.md), [Forza Horizon 6 (livedata)](game-forza-horizon-6.md), [Forza Motorsport (livedata)](game-forza-motorsport.md), [Richard Burns Rally (livedata)](game-richard-burns-rally.md).

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

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåtet (läser bara det spelet publicerar)".
- Slag `telemetry`: den läser bara det spelet eller plattformen lämnar ut (en UDP-port eller delat minne som spelet publicerar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- rader 10 gånger per sekund: position, hastighet, växel, gas, broms, sträcka i etappen, yaw, varvtal, styrning; etappstart, målgång med etappens tid, omstarter

**Sparas råa**

- varje paket som når porten, helt, i spelets takt, under sitt format: `session_update` (standardstrukturen `wrc`, 237 byte), `wrc <n>-byte` för varje annat paket konfigurationen skickar
- i paketet utöver raderna: världshastighet och acceleration, bilens axlar, position och hastighet per hjulnav, kontaktytans hastighet, bromstemperatur, koppling, handbroms, spelets klocka; 22 byte (offset 16-36 och 40) som ingen publicerad kanallista namnger

**Finns inte**

- andra bilar: spelen skickar bara spelarens bil
- de övriga strukturerna och paketen som telemetrikonfigurationen kan definiera (session_start, session_end, paus): bara `session_update` slås på av `setup`; annat paket som skickas till porten sparas

**Storlek**: ungefär 65 MB per timme vid 60 paket per sekund (237 byte plus 70 byte paketrubrik; konfigurationens -1-takt skickar ett per bildruta, så mer vid högre bildfrekvens); zstd behåller en bråkdel

## Verifierat {#verified}

avkodningen är gamecapture-varvinspelarens (testad på paket byggda från de dokumenterade layouterna); adaptern testad på paket byggda i testet, skickade över UDP; ännu inte testad mot spelet

## Källa {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
