---
title: "Assetto Corsa (live-data)"
nav_order: 2
lang: "da"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (live-data) {#assetto-corsa-live-data}

Mens du spiller Assetto Corsa, gemmer watcheren de data, som spillet selv sender ud, så du senere kan se dem på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `assetto-corsa`, type [`telemetry`](sources-and-rules.md); den kører, mens `acs.exe` eller `acs_x86.exe` kører, og leder efter nye data hver 0.1 s.*

## Hvad der registreres {#what-is-recorded}

- egen bils position (verdens XYZ, m: gennemsnittet af dækkenes kontaktpunkter) 10 gange i sekundet med hastighed, gear, gas og bremse
- sessionens start og slut med banen og bilen, spillet angiver
- runder efter spillets rundetæller, med rundetiden
- teleportering (tilbage til pitten, en genstart): `teleport` der hvor bilen var, `spawn` der hvor den er nu
- runder, bedste runde, distance, topfart

## Hvor data kommer fra {#where-it-comes-from}

shared memory Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Sådan slår du det til {#how-to-switch-it-on}

Der er intet at slå til: watcheren læser kilden, som spillet eller platformen stiller den til rådighed.

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

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Delt hukommelse, som spillet skriver til apps: `Local\acpmf_physics`,
`Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`).
Åbnes kun læsning og først, når spillet har oprettet den (`simracing_shm`). Positionen er
gennemsnittet af de fire dækkes kontaktpunkter, verdens meter, Y op.
Runder efter spillets tæller (AC, ACC) eller ved at passere startpunktet igen
(AC EVO, AC Rally), som `kunos.py` gør for rundeoptageren.

#### Alt gemmes {#everything-kept}

Rækkerne er få pr. sekund; spillene sender langt flere. Hver UDP-pakke der
kommer ind - i menuerne, mellem runder, dem ingen afkoder læser - gemmes hel
i sessionens `heat.raw.parquet` under sit format (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), og hver side i delt hukommelse
(hele området, ikke kun de bytes der er afkodet) hver gang den ændrer sig, under
sit områdes navn (`acpmf_physics`, ...). `used` markerer det, der også blev
rækker; `meta.json`s `selfCheck.completeness` tæller hver type (3DHeats
konverterregel).

Modulet dækker også: [Assetto Corsa Competizione (live-data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (live-data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (live-data)](game-assetto-corsa-rally.md), [BeamNG.drive (live-data)](game-beamng.md), [DiRT Rally 2.0 (live-data)](game-dirt-rally-2.md), [EA SPORTS WRC (live-data)](game-ea-wrc.md), [Forza Horizon 4 (live-data)](game-forza-horizon-4.md), [Forza Horizon 5 (live-data)](game-forza-horizon-5.md), [Forza Horizon 6 (live-data)](game-forza-horizon-6.md), [Forza Motorsport (live-data)](game-forza-motorsport.md), [Richard Burns Rally (live-data)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text`, plus ethvert felt gemt under sit navn; `used` markerer det, der også blev rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- rækker 10 gange i sekundet fra fysiksiden: position (gennemsnit af dækkenes kontaktpunkter), hastighed, gear, gas, bremse, yaw/pitch/roll (rad), omdrejninger, styring (som siden har den); sessionens start med bane og bil fra statiksiden; runder, placering

**Gemt råt**

- hver side hel - hele hukommelsesområdet, ikke kun de afkodede bytes - hver gang dens bytes ændrer sig, ved watcherens læsning 10 gange i sekundet: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; en genlæsning der er byte for byte den sidste, tælles i meta.jsons `unchanged_reads` og gemmes ikke igen
- alt afkodet kun til rundefiler (`decoders/kunos.py`: slip, belastning, tryk, temperaturer, camber, ophæng, kontaktpunkter pr. hjul, bremsetemperaturer, slip-forhold og -vinkel; verdens- og lokal hastighed, vinkelhastighed, hjælpere) ligger på disse sider

**Ikke tilgængeligt**

- andre biers positioner: siderne beskriver kun spillerens bil (ACCs grafiksiden har bil-id'er og koordinater for andre i nogle versioner - gemt i den rå side, ikke afkodet)
- fysiktik mellem watcherens læsninger: spillet skriver siden om med sin fysiksats (op til 333 Hz), og watcheren læser 10 gange i sekundet

**Størrelse**: cirka 150-300 MB i timen før komprimering (et område på 4 KB pr. side, op til 10 ændringer i sekundet); siderne er for det meste nuller, og zstd beholder en lille brøkdel

## Verificeret {#verified}

afkodningen er gamecapture's rundeoptagers (testet på syntetiske sider); adapteren testet på delt hukommelse bygget i testen ud fra det dokumenterede layout; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
