---
title: "EA SPORTS WRC (live-data)"
nav_order: 17
lang: "da"
source: game-ea-wrc.md
source_hash: "c97300f65c43"
nav_exclude: true
search_exclude: true
---
# EA SPORTS WRC (live-data) {#ea-sports-wrc-live-data}

Mens du spiller EA SPORTS WRC, gemmer watcheren de data, som spillet selv sender ud, så du senere kan se dem på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `ea-wrc`, type [`telemetry`](sources-and-rules.md); den kører, mens `WRC.exe` kører, og leder efter nye data hver 0.1 s.*

## Hvad der registreres {#what-is-recorded}

- egen bils position (verdens XYZ, m) 10 gange i sekundet med hastighed, gear, gas, bremse, distance i etapen
- etapestart (etapeuret starter), slut med etapetiden, genstarter
- teleportering (en nulstilling til vejen): `teleport` der hvor bilen var, `spawn` der hvor den er nu
- etaper, bedste etapetid, distance, topfart

## Hvor data kommer fra {#where-it-comes-from}

UDP 127.0.0.1:20777, standardstrukturen `wrc`s session_update-pakke (Documents\My Games\WRC\telemetry\config.json); mens en anden app holder 20777, lader watcheren porten være til den

## Sådan slår du det til {#how-to-switch-it-on}

`python -m heat3d_watch setup ea-wrc --apply` slår session_update-pakken til i config.json (sikkerhedskopi tages først)

Skriv kommandoen i en terminal, der er åbnet i watcherens mappe (se [Før du går i gang](before-you-start.md)). Hvis den fejler, siger den sidste linje hvorfor; [Installation og kørsel](installing-and-running.md) dækker de almindelige årsager.

`python -m heat3d_watch setup ea-wrc` viser de filer, den ville ændre; `python -m heat3d_watch setup ea-wrc --apply` ændrer dem og gemmer originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `ea-wrc: changed: ...` for hver ændring, eller `ea-wrc: nothing to change`, når den allerede er slået til.

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

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: WRC's `Documents/My Games/WRC/telemetry/config.json` (strukturen `wrc`s
`session_update`-pakke), DiRTs `hardware_settings_config.xml`
(`<udp enabled="true" extradata="3" port="20777">`), RBRs NGP-plugin
(`udpTelemetry=1`, port 6776). Etaper efter spillets etapeur
(`rally.StageSplitter`). RBR dokumenterer ikke sine akser: op-aksen er
den, etapen varierer mindst langs, afgjort når sessionen lukkes.

#### Alt gemmes {#everything-kept}

Rækkerne er få pr. sekund; spillene sender langt flere. Hver UDP-pakke der
kommer ind - i menuerne, mellem runder, dem ingen afkoder læser - gemmes hel
i sessionens `heat.raw.parquet` under sit format (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), og hver side i delt hukommelse
(hele området, ikke kun de bytes der er afkodet) hver gang den ændrer sig, under
sit områdes navn (`acpmf_physics`, ...). `used` markerer det, der også blev
rækker; `meta.json`s `selfCheck.completeness` tæller hver type (3DHeats
konverterregel).

Modulet dækker også: [Assetto Corsa (live-data)](game-assetto-corsa.md), [Assetto Corsa Competizione (live-data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (live-data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (live-data)](game-assetto-corsa-rally.md), [BeamNG.drive (live-data)](game-beamng.md), [DiRT Rally 2.0 (live-data)](game-dirt-rally-2.md), [Forza Horizon 4 (live-data)](game-forza-horizon-4.md), [Forza Horizon 5 (live-data)](game-forza-horizon-5.md), [Forza Horizon 6 (live-data)](game-forza-horizon-6.md), [Forza Motorsport (live-data)](game-forza-motorsport.md), [Richard Burns Rally (live-data)](game-richard-burns-rally.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | ja |
| Op-akse | `y` |
| Enheder | meter |
| Spejlet for vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, ind i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "tilladt (læser kun det spillet udleverer)".
- Type `telemetry`: den læser kun det, spillet eller platformen udleverer (en UDP-port eller delt hukommelse spillet udgiver), så den optager også i onlinespil såvel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der registreres {#statistics-recorded}

Statistiknøgler, som denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text`, plus ethvert felt gemt under sit navn; `used` markerer det, der også blev rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- rækker 10 gange i sekundet: position, hastighed, gear, gas, bremse, etapedistance, yaw, omdrejninger, styring; etapestart, slut med etapetiden, genstarter

**Gemt råt**

- hver pakke der når porten, hel, i spillets takt, under sit format: `session_update` (standardstrukturen `wrc`, 237 bytes), `wrc <n>-byte` for enhver anden pakke konfigurationen sender
- i pakken ud over rækkerne: verdenshastighed og -acceleration, bilens akser, position pr. hjulnav og hastighed, kontaktfladens hastighed, bremsetemperatur, kobling, håndbremse, spillets ur; 22 bytes (forskydning 16-36 og 40), som ingen offentliggjort kanalliste navngiver

**Ikke tilgængeligt**

- andre biler: spillene sender kun spillerens bil
- de andre strukturer og pakker telemetri-konfigurationen kan definere (session_start, session_end, pause): kun `session_update` slås til af `setup`; enhver anden pakke der sendes til porten, gemmes

**Størrelse**: cirka 65 MB i timen ved 60 pakker i sekundet (237 bytes plus et 70-byte item-header; konfigurationens -1-takt sender én pr. billede, så der er flere ved højere billedfrekvens); zstd beholder en brøkdel

## Verificeret {#verified}

afkodningen er gamecapture's rundeoptagers (testet på pakker bygget ud fra de dokumenterede layouts); adapteren testet på pakker bygget i testen og sendt over UDP; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
