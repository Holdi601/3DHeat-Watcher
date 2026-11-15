---
title: "BeamNG.drive (live-data)"
nav_order: 7
lang: "da"
source: game-beamng.md
source_hash: "1c23a869a62f"
nav_exclude: true
search_exclude: true
---
# BeamNG.drive (live-data) {#beamngdrive-live-data}

Mens du spiller BeamNG.drive, gemmer watcheren de data, som spillet selv sender ud, så du senere kan se dem på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `beamng`, type [`telemetry`](sources-and-rules.md); den kører, mens `BeamNG.drive.x64.exe` eller `BeamNG.drive.exe` kører, og leder efter nye data hver 0.1 s.*

## Hvad der registreres {#what-is-recorded}

- egen bils position (i verden, m, drejet til Y op) 10 gange i sekundet med hastighed, gear, gas, bremse
- kørslens start, nulstillinger (genopstå), runder efter det sted hvor kørslen begyndte
- runder, bedste runde, distance, topfart

## Hvor data kommer fra {#where-it-comes-from}

UDP 127.0.0.1:4460 fra heat3d-protokolmodden (mods/beamng/heat3d i dette repository)

## Sådan slår du det til {#how-to-switch-it-on}

`python -m heat3d_watch setup beamng --apply` installerer modden; derefter Options > Other > Protocols > "others"

Skriv kommandoen i en terminal, der er åbnet i watcherens mappe (se [Før du starter](before-you-start.md)). Hvis den fejler, siger den sidste linje hvorfor; [Installation og kørsel](installing-and-running.md) dækker de almindelige årsager.

`python -m heat3d_watch setup beamng` viser, hvilke filer den ville ændre; `python -m heat3d_watch setup beamng --apply` ændrer dem og gemmer originalen som `<fil>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `beamng: changed: ...` for hver ændring, eller `beamng: nothing to change`, når den allerede er slået til.

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

#### BeamNG.drive {#beamngdrive}

Protokolmodden `heat3d`, som gamecapture leverer (UDP 4460, Options > Other >
Protocols > "others"); BeamNG's verden med Z op drejet til Y op, som `beamng.py` gør.

#### Alt det øvrige gemmes {#everything-kept}

Rækkerne er et par stykker i sekundet; spillene sender langt flere. Hver UDP-pakke,
der kommer ind - i menuerne, mellem runder, og dem ingen afkoder læser - gemmes hel
i kørslens `heat.raw.parquet` under sit format (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), og hver side med delt hukommelse
(hele mappingen, ikke kun de bytes der afkodes) hver gang den ændrer sig, under
sit mappings navn (`acpmf_physics`, ...). `used` markerer det, der også blev til
rækker; `selfCheck.completeness` i `meta.json` tæller hver type (3DHeats
konverterregel).

Det samme modul bruges også af: [Assetto Corsa (live-data)](game-assetto-corsa.md), [Assetto Corsa Competizione (live-data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (live-data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (live-data)](game-assetto-corsa-rally.md), [DiRT Rally 2.0 (live-data)](game-dirt-rally-2.md), [EA SPORTS WRC (live-data)](game-ea-wrc.md), [Forza Horizon 4 (live-data)](game-forza-horizon-4.md), [Forza Horizon 5 (live-data)](game-forza-horizon-5.md), [Forza Horizon 6 (live-data)](game-forza-horizon-6.md), [Forza Motorsport (live-data)](game-forza-motorsport.md), [Richard Burns Rally (live-data)](game-richard-burns-rally.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | ja |
| Op-akse | `y` |
| Enheder | meter (BeamNG's verden med Z op, drejet om X, som rundeoptageren gør) |
| Spejlet til vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver kørsels `meta.json` (`axes`) og, når kørslen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **nej**. `games --markdown` viser det som "kun enkeltspiller".
- Type `telemetry`: den læser kun det spillet eller platformen udleverer (en UDP-port eller delt hukommelse spillet udgiver), så den optager også i onlinespil og offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: læses **aldrig** af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Registrerede statistikker {#statistics-recorded}

Statistiknøgler, som adapterens kode sætter ved navn (hver kørsels `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `top_speed_kmh`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, og aldrig smides væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i kørslens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter, der gemmes under deres navn; `used` markerer, hvad der også blev til rækker), og `selfCheck.completeness` i `meta.json` tæller hver `type` - `lost` er 0.

**Læst**

- rækker 10 gange i sekundet: position, hastighed, gear, gas, bremse, gir, rpm, styring; kørslens start, nulstillinger, runder

**Gemt råt**

- hver pakke, der når porten, hel, med modens 100 Hz, under `H3D1` (modens 160-byte-struktur: ur, position, hastighed, bilens akser, drejningshastighed, ni input, pr. hjul overfladehastighed, rotation, belastning og underlagsmateriale) og `<n>-byte` for alt andet

**Ikke tilgængeligt**

- det modden ikke sender: BeamNG har ingen fast telemetripakke, så kanalerne er dem, heat3d-modden har valgt (andre køretøjer, skader og kortets navn er ikke med)

**Størrelse**: cirka 80 MB i timen før komprimering (100 pakker i sekundet á 160 byte plus en 70-byte pakkehovedet)

## Verificeret {#verified}

afkodningen er rundeoptagerens fra gamecapture (testet på pakker bygget ud fra modens struktur); adapteren testet på sådanne pakker; modden er ikke testet i spillet

## Kilde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Genereret fra adapteren af tools/gen_game_pages.py; ret adapteren og kør den igen i stedet for at redigere denne side. -->
