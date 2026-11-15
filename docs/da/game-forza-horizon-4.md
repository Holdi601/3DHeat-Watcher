---
title: "Forza Horizon 4 (live-data)"
nav_order: 21
lang: "da"
source: game-forza-horizon-4.md
source_hash: "ac1890f4d62c"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 4 (live-data) {#forza-horizon-4-live-data}

Mens du spiller Forza Horizon 4, gemmer watcheren de data, som spillet selv sender ud, så du senere kan se dem på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `forza-horizon-4`, type [`telemetry`](sources-and-rules.md); den kører, mens `ForzaHorizon4.exe` kører, og leder efter nye data hver 0.1 s.*

## Hvad der registreres {#what-is-recorded}

- egen bils position (verdens XYZ, m) 10 gange i sekundet med hastighed, gear, gas, bremse, runde
- kørslens start og slut (session_start/session_end), runder med spillets rundetid
- løbets start og slut med løbsplaceringen
- teleportering (spoling tilbage, hurtigrejse): `teleport` der hvor bilen var, `spawn` der hvor den er nu
- runder, bedste runde, distance, topfart, løb

## Hvor data kommer fra {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); hver pakke videresendt uændret til 127.0.0.1:5301

## Sådan slår du det til {#how-to-switch-it-on}

I spillet: Settings > HUD and Gameplay > Data Out On, IP 127.0.0.1, port 5300 (Motorsport: format Dash). FH Companion eller en anden Data Out-app: sæt dens port til 5301 - watcheren videresender hver pakke; mens en anden app lytter på 5300, lader watcheren porten være til den og optager ingenting

## Sådan virker det {#how-it-works}

Racingspillenes egen telemetri: Forza, Assetto Corsa-spillene, rallyspillene
og BeamNG, gemt som ruter, runder og etaper.

Alle spil her udgiver deres telemetri med vilje, til dashboards og bevægelsesrigge;
intet bliver indsprøjtet, og intet læses, som spillet ikke selv udleverer. Afkodningen
er ikke skrevet to gange: det er gamecapture's rundeoptagere i
3DHeat GameCapture's `heat3d_capture/telemetry`, kopieret til `heat3d_watch/decoders` (testet der mod pakker bygget ud fra
de offentliggjorte layouts), og dette modul omsætter deres billeder til watcherens
rækker - bilens position et par gange i sekundet med hastighed, gear og pedaler,
en hændelse pr. runde eller etape, og de tal en fører holder styr på: runder, bedste runde,
distance, topfart.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, slået til i spillets HUD- og Gameplay-indstillinger, til
127.0.0.1 port 5300, format Dash. Én pakke pr. simuleringstik; blokken
med dashdata får sin forskydning fundet ud fra pakkerne (`forza.detect_layout`). Verdens
meter, Y op; verdenen er venstrehåndet og tegnes som sendt, ligesom rundeoptageren
gør (Forza Motorsports og Forza Horizons "Data Out"-dokumentation).
Spillet sender til én port, og FH Companion og andre Data Out-apps lytter
på den samme. To programmer kan ikke dele den: på Windows får socketen bundet
til 127.0.0.1 pakkerne, og en bundet til alle adresser på samme
port får ingen, uanset hvem der var først. Derfor venter watcheren lidt, efter
spillet er startet, før den tager porten, tager den aldrig fra en app, der
holder den, og slipper den, så snart en anden app begynder at lytte der.
Mens den holder porten, videresender den hver pakke uændret til
127.0.0.1:5301 - sæt FH Companions portfelt (fanen telemetri) til 5301, så
optager begge.

#### Alt gemmes {#everything-kept}

Rækkerne er få pr. sekund; spillene sender langt flere. Hver UDP-pakke der
kommer ind - i menuerne, mellem runder, dem ingen afkoder læser - gemmes hel
i sessionens `heat.raw.parquet` under sit format (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), og hver side i delt hukommelse
(hele området, ikke kun de bytes der er afkodet) hver gang den ændrer sig, under
sit områdes navn (`acpmf_physics`, ...). `used` markerer det, der også blev
rækker; `meta.json`s `selfCheck.completeness` tæller hver type (3DHeats
konverterregel).

Modulet dækker også: [Assetto Corsa (live-data)](game-assetto-corsa.md), [Assetto Corsa Competizione (live-data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (live-data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (live-data)](game-assetto-corsa-rally.md), [BeamNG.drive (live-data)](game-beamng.md), [DiRT Rally 2.0 (live-data)](game-dirt-rally-2.md), [EA SPORTS WRC (live-data)](game-ea-wrc.md), [Forza Horizon 5 (live-data)](game-forza-horizon-5.md), [Forza Horizon 6 (live-data)](game-forza-horizon-6.md), [Forza Motorsport (live-data)](game-forza-motorsport.md), [Richard Burns Rally (live-data)](game-richard-burns-rally.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | ja |
| Op-akse | `y` |
| Enheder | meter; Forzas verden er venstrehåndet, tegnes som sendt, ligesom rundeoptageren gør |
| Spejlet for vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, ind i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "tilladt (læser kun det spillet udleverer)".
- Type `telemetry`: den læser kun det, spillet eller platformen udleverer (en UDP-port eller delt hukommelse spillet udgiver), så den optager også i onlinespil såvel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der registreres {#statistics-recorded}

Statistiknøgler, som denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text`, plus ethvert felt gemt under sit navn; `used` markerer det, der også blev rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- rækker 10 gange i sekundet: position, hastighed, gear, gas, bremse, runde, yaw/pitch/roll (rad), omdrejninger, styring (-1..1); session_start med bilens ordinal, klasse, PI og drivlinje; runder med spillets rundetid; løbsplacering

**Gemt råt**

- hver pakke der når porten, hel, i spillets takt (én pr. simuleringstik), under sit format: `dash-horizon` (324 bytes, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: dækslid og bane-id), `sled` (232, ingen position), `<n>-byte` for alt andet - herunder menupakker (isRaceOn 0), pakkerne der holdes, indtil dashlayoutet er bevist, og de ~13 bytes i Horizon-pakken som intet offentliggjort layout navngiver
- Sled-blokkens hver hjulkanal (slip-forhold, slip-vinkel, kombineret slip, ophæng, hjulhastighed, rumble, puddle), accelerationer, vinkelhastighed, effekt, moment, boost, brændstof, dæktemperaturer, kobling, håndbremse, kørelinje, AI-bremseforskel: alt i pakkerne, afkodet af `decoders/fulllap.decode_full` ud fra dem

**Ikke tilgængeligt**

- andre biler: Data Out beskriver kun spillerens bil
- bane- eller rutenavnet: Forza Horizon sender det aldrig; Motorsport 2023 sender kun et banenummer
- pakker mens en anden app (FH Companion) holder UDP 5300: watcheren lader porten være til den

**Størrelse**: cirka 85 MB i timen før komprimering (60 pakker i sekundet á 324 bytes plus et 70-byte item-header); på hinanden følgende pakker adskiller sig lidt, så zstd beholder en brøkdel af det

## Verificeret {#verified}

afkodningen er gamecapture's rundeoptagers (testet på pakker bygget ud fra Data Out-layoutet); adapteren testet på syntetiske pakker og på optagne rundebaner afspillet som pakker; ikke testet mod selve spillet

## Kilde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
