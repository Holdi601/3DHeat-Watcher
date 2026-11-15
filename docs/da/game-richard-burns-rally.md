---
title: "Richard Burns Rally (live-data)"
nav_order: 38
lang: "da"
source: game-richard-burns-rally.md
source_hash: "4f2a2e46f8c8"
nav_exclude: true
search_exclude: true
---
# Richard Burns Rally (live-data) {#richard-burns-rally-live-data}

Mens du spiller Richard Burns Rally, gemmer watcheren de data, som spillet selv sender ud, så du senere kan se dem på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `richard-burns-rally`, type [`telemetry`](sources-and-rules.md); den kører, mens `RichardBurnsRally_SSE.exe` eller `RichardBurnsRally.exe` kører, og leder efter nye data hver 0.1 s.*

## Hvad der registreres {#what-is-recorded}

- egen bils position (verdens XYZ, m) 10 gange i sekundet med hastighed, gear, gas, bremse, distance i etapen
- etapestart (etapeuret starter), slut med etapetiden, genstarter
- teleportering (en nulstilling til vejen): `teleport` der hvor bilen var, `spawn` der hvor den er nu
- etaper, bedste etapetid, distance, topfart

## Hvor data kommer fra {#where-it-comes-from}

NGP-pluginets UDP-telemetri, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1)

## Sådan slår du det til {#how-to-switch-it-on}

RSF/NGP: i RichardBurnsRally.ini, afsnittet [NGP], sæt udpTelemetry=1 og endpointet til 127.0.0.1:6776

## Sådan virker det {#how-it-works}

Racingspillenes egen telemetri: Forza, Assetto Corsa-spillene, rallyspillene
og BeamNG, gemt som ruter, runder og etaper.

Alle spil her udgiver deres telemetri med vilje, til dashboards og bevægelsesrigge;
intet bliver indsprøjtet, og intet læses, som spillet ikke selv udleverer. Afkodningen
er ikke skrevet to gange: det er gamecapture's rundeoptagere i
3DHeat GameCapture's `heat3d_capture/telemetry`, kopieret til `heat3d_watch/decoders` (testet der mod pakker bygget ud fra
de udgivne layouts), og dette modul omsætter deres billeder til watcherens
rækker - bilens position et par gange i sekundet med hastighed, gear og pedaler,
en hændelse pr. runde eller etape, og de tal en fører holder styr på: runder, bedste runde,
distance, topfart.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, slået til i spillets HUD- og Gameplay-indstillinger, til
127.0.0.1 port 5300, format Dash. Én pakke pr. simuleringstik; dash-blokkens
forskydning findes ud fra pakkerne (`forza.detect_layout`). Verdenen i meter,
Y op; verdenen er venstrehåndet og tegnes som sendt, ligesom rundeoptageren
gør (Forza Motorsports og Forza Horizons dokumentation for "Data Out").
Spillet sender til én port, og FH Companion og andre Data Out-apps lytter
på den samme. To programmer kan ikke dele den: på Windows får socketen bundet
til 127.0.0.1 pakkerne, og en socket bundet til alle adresser på samme
port får ingen, uanset hvem der kom først. Derfor venter watcheren lidt, efter
spillet er startet, før den tager porten, tager den aldrig fra en app der
holder den, og giver den fra sig, så snart en anden app begynder at lytte der.
Mens watcheren holder porten, videresender den hver pakke uændret til
127.0.0.1:5301 - sæt FH Companions portfelt (fanen telemetri) til 5301, så
optager begge.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: WRC's `Documents/My Games/WRC/telemetry/config.json` (`wrc`-strukturens
`session_update`-pakke), DiRT's `hardware_settings_config.xml`
(`<udp enabled="true" extradata="3" port="20777">`), RBR's NGP-plugin
(`udpTelemetry=1`, port 6776). Etaper efter spillets etapeur (`rally.StageSplitter`).
RBR dokumenterer ikke sine akser: op-aksen er den, etapen varierer mindst langs,
afgjort når sessionen lukkes.

#### Alt det øvrige gemmes {#everything-kept}

Rækkerne er et par stykker i sekundet; spillene sender langt flere. Hver UDP-pakke,
der kommer ind - i menuerne, mellem runder, og dem ingen afkoder læser - gemmes hel
i kørslens `heat.raw.parquet` under sit format (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), og hver side med delt hukommelse
(hele mappingen, ikke kun de bytes der afkodes) hver gang den ændrer sig, under
sit mappings navn (`acpmf_physics`, ...). `used` markerer det, der også blev til
rækker; `selfCheck.completeness` i `meta.json` tæller hver type (3DHeats
konverterregel).

Det samme modul bruges også af: [Assetto Corsa (live-data)](game-assetto-corsa.md), [Assetto Corsa Competizione (live-data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (live-data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (live-data)](game-assetto-corsa-rally.md), [BeamNG.drive (live-data)](game-beamng.md), [DiRT Rally 2.0 (live-data)](game-dirt-rally-2.md), [EA SPORTS WRC (live-data)](game-ea-wrc.md), [Forza Horizon 4 (live-data)](game-forza-horizon-4.md), [Forza Horizon 5 (live-data)](game-forza-horizon-5.md), [Forza Horizon 6 (live-data)](game-forza-horizon-6.md), [Forza Motorsport (live-data)](game-forza-motorsport.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | ja |
| Op-akse | `y` |
| Enheder | meter; op-aksen afgjort ud fra kørslen (RBR dokumenterer ikke sine akser) |
| Spejlet til vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver kørsels `meta.json` (`axes`) og, når kørslen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **nej**. `games --markdown` viser det som "kun enkeltspiller".
- Type `telemetry`: den læser kun det spillet eller platformen udleverer (en UDP-port eller delt hukommelse spillet udgiver), så den optager også i onlinespil og offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: læses **aldrig** af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Registrerede statistikker {#statistics-recorded}

Statistiknøgler, som adapterens kode sætter ved navn (hver kørsels `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, og aldrig smides væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i kørslens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter, der gemmes under deres navn; `used` markerer, hvad der også blev til rækker), og `selfCheck.completeness` i `meta.json` tæller hver `type` - `lost` er 0.

**Læst**

- rækker 10 gange i sekundet: position, hastighed, gear, gas, bremse, distance i etapen, giering, rpm, styring; etapestart, slut med etapetiden, genstarter

**Gemt råt**

- hver pakke, der når porten, hel, med spillets hastighed, under sit format: `telemetry` (NGP's 664-byte TelemetryData), ellers `rbr <n>-byte`
- i pakken ud over rækkerne: holdning, bilens egne hastigheder og accelerationer, pr. hjul fjederudslag og kraft, etapens fremskridt og afstand til målet; resten af de 664 byte (motor, dæk- og bremseblokke pr. hjul) afkodes endnu ingen steder

**Ikke tilgængeligt**

- andre biler: spillene sender kun spillerens bil
- dens hastighedsenhed og akser: ikke dokumenteret - hastigheden tages fra positionerne, op fra kørslen

**Størrelse**: cirka 160 MB i timen ved 60 pakker i sekundet (664 byte plus en 70-byte pakkehovedet); zstd gør en brøkdel af det

## Verificeret {#verified}

afkodningen er rundeoptagerens fra gamecapture (testet på pakker bygget ud fra de dokumenterede layouts); adapteren testet på pakker bygget i testen, sendt over UDP; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Genereret fra adapteren af tools/gen_game_pages.py; ret adapteren og kør den igen i stedet for at redigere denne side. -->
