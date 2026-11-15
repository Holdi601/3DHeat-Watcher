---
title: "Assetto Corsa Competizione (live-data)"
nav_order: 3
lang: "da"
source: game-assetto-corsa-competizione.md
source_hash: "08033208b212"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa Competizione (live-data) {#assetto-corsa-competizione-live-data}

Mens du spiller Assetto Corsa Competizione, gemmer watcheren de data, som spillet selv sender ud, så du senere kan se dem på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `assetto-corsa-competizione`, type [`telemetry`](sources-and-rules.md); den kører, mens `AC2-Win64-Shipping.exe` kører, og leder efter nye data hver 0.1 s.*

## Hvad der registreres {#what-is-recorded}

- egen bils position (verdens XYZ, m: gennemsnittet af dækkenes kontaktpunkter) 10 gange i sekundet med hastighed, gear, gas, bremse
- kørslens start og slut med banen og bilen, spillet angiver
- runder efter spillets rundetæller, med spillets rundetid; løbsplacering
- teleportering (tilbage til depotet, en genstart): `teleport` der hvor bilen var, `spawn` der hvor den er nu
- runder, bedste runde, distance, topfart

## Hvor data kommer fra {#where-it-comes-from}

delt hukommelse Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Sådan slår du det til {#how-to-switch-it-on}

Der skal ikke slås noget til: watcheren læser kilden, som spillet eller platformen udleverer den.

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

#### Alt det øvrige gemmes {#everything-kept}

Rækkerne er et par stykker i sekundet; spillene sender langt flere. Hver UDP-pakke,
der kommer ind - i menuerne, mellem runder, og dem ingen afkoder læser - gemmes hel
i kørslens `heat.raw.parquet` under sit format (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), og hver side med delt hukommelse
(hele mappingen, ikke kun de bytes der afkodes) hver gang den ændrer sig, under
sit mappings navn (`acpmf_physics`, ...). `used` markerer det, der også blev til
rækker; `selfCheck.completeness` i `meta.json` tæller hver type (3DHeats
konverterregel).

Det samme modul bruges også af: [Assetto Corsa (live-data)](game-assetto-corsa.md), [Assetto Corsa EVO (live-data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (live-data)](game-assetto-corsa-rally.md), [BeamNG.drive (live-data)](game-beamng.md), [DiRT Rally 2.0 (live-data)](game-dirt-rally-2.md), [EA SPORTS WRC (live-data)](game-ea-wrc.md), [Forza Horizon 4 (live-data)](game-forza-horizon-4.md), [Forza Horizon 5 (live-data)](game-forza-horizon-5.md), [Forza Horizon 6 (live-data)](game-forza-horizon-6.md), [Forza Motorsport (live-data)](game-forza-motorsport.md), [Richard Burns Rally (live-data)](game-richard-burns-rally.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | ja |
| Op-akse | `y` |
| Enheder | meter |
| Spejlet til vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver kørsels `meta.json` (`axes`) og, når kørslen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser det som "tilladt (læser kun det spillet udgiver)".
- Type `telemetry`: den læser kun det spillet eller platformen udleverer (en UDP-port eller delt hukommelse spillet udgiver), så den optager også i onlinespil og offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: læses **aldrig** af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Registrerede statistikker {#statistics-recorded}

Statistiknøgler, som adapterens kode sætter ved navn (hver kørsels `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, og aldrig smides væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i kørslens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter, der gemmes under deres navn; `used` markerer, hvad der også blev til rækker), og `selfCheck.completeness` i `meta.json` tæller hver `type` - `lost` er 0.

**Læst**

- rækker 10 gange i sekundet fra fysiksiden: position (gennemsnit af dækkenes kontaktpunkter), hastighed, gear, gas, bremse, gir/hældning/rulning (rad), rpm, styring (som siden har den); kørslens start med bane og bil fra statiksiden; runder, løbsplacering

**Gemt råt**

- hver side hel - hele mappingområdet, ikke kun de bytes der afkodes - hver gang dens bytes ændrer sig, med watcherens 10 læsninger i sekundet: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; en genlæsning der er byte for byte den sidste, tælles i meta.json's `unchanged_reads` og gemmes ikke igen
- alt det, der kun afkodes for rundefiler (`decoders/kunos.py`: slip, belastning, tryk, temperaturer, camber, ophæng, kontaktpunkter, bremsetemperaturer, slip-forhold og -vinkel pr. hjul; verdens- og lokal hastighed, vinkelhastighed, hjælpesystemer) ligger i siderne

**Ikke tilgængeligt**

- andre biler' positioner: siderne beskriver kun spillerens bil (ACC's grafikside har i nogle versioner bil-id'er og koordinater for andre biler - de gemmes i den rå side, men afkodes ikke)
- fysiktik mellem watcherens læsninger: spillet skriver siden om med sin fysikhastighed (op til 333 Hz), og watcheren læser 10 gange i sekundet

**Størrelse**: cirka 150-300 MB i timen før komprimering (en 4 KB-region pr. side ved op til 10 ændringer i sekundet); siderne er for det meste nuller, og zstd gemmer en lille del

## Verificeret {#verified}

afkodningen er rundeoptagerens fra gamecapture (testet på syntetiske sider); adapteren testet på delt hukommelse bygget i testen ud fra det dokumenterede layout; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Genereret fra adapteren af tools/gen_game_pages.py; ret adapteren og kør den igen i stedet for at redigere denne side. -->
