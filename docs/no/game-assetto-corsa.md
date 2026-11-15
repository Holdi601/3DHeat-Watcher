---
title: "Assetto Corsa (live-data)"
nav_order: 2
lang: "no"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (live-data) {#assetto-corsa-live-data}

Mens du spiller Assetto Corsa, lagrer watcheren de dataene spillet selv sender ut, slik at du kan se på dem senere på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `assetto-corsa`, type [`telemetry`](sources-and-rules.md); den kjører mens `acs.exe` eller `acs_x86.exe` kjører, og ser etter nye data hvert 0,1 s.*

## Hva som lagres {#what-is-recorded}

- egen bils posisjon (verdens XYZ, m: gjennomsnittet av dekkenes kontaktpunkter) 10 ganger i sekundet, med fart, gir, gass og brems
- øktstart og øktslutt, med banen og bilen spillet oppgir
- runder etter spillets rundeteller, med rundetiden
- teleporteringer (tilbake til depotet, en omstart): `teleport` der bilen var, `spawn` der den er nå
- runder, beste runde, distanse, toppfart

## Hvor dataene kommer fra {#where-it-comes-from}

delt minne Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Slik slår du det på {#how-to-switch-it-on}

Du må ikke slå noe på: watcheren leser kilden slik spillet eller plattformen leverer den.

## Slik fungerer det {#how-it-works}

Racingspillenes egen telemetri: Forza, Assetto Corsa-spillene, rallyspillene
og BeamNG, lagret som ruter, runder og etapper.

Alle spillene her sender ut telemetrien sin med vilje, til dashbord og bevegelsesrigger;
ingenting blir injisert, og ingenting spillet ikke gir ut, leses. Dekodingen er
ikke skrevet to ganger: det er rundeopptakerne i gamecapture, i 3DHeat GameCapture sin `heat3d_capture/telemetry`, kopiert over til `heat3d_watch/decoders` (testet der mot pakker bygd etter de publiserte oppsettene),
og denne modulen gjør rammene deres om til watcherens rader - bilens posisjon noen
ganger i sekundet med fart, gir og pedaler, en hendelse per runde eller etappe,
og tallene en sjåfør holder styr på: runder, beste runde, distanse, toppfart.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

«Data Out» over UDP, slått på i spillets HUD- og spillinnstillinger, til
127.0.0.1 port 5300, format Dash. Én pakke per simuleringstikk; oppsettet
for dash-blokken finnes ut fra pakkene (`forza.detect_layout`). Verdens meter, Y opp; verdenen er venstrehåndet og tegnes slik den sendes, slik rundeopptakeren gjør
(Forza Motorsport og Forza Horizon sin dokumentasjon for «Data Out»).
Spillet sender til én port, og FH Companion og andre Data Out-apper lytter på
samme. To programmer kan ikke dele den: på Windows får socketen bundet til
127.0.0.1 pakkene, og en som er bundet til alle adresser på samme
port får ingen, uansett hvem som kom først. Derfor venter watcheren litt etter at
spillet har startet før den tar porten, tar den aldri fra en app som holder den,
og gir den fra seg så snart en annen app begynner å lytte der.
Mens den holder porten, sender den hver pakke videre uendret til
127.0.0.1:5301 - sett FH Companion sin portboks (fanen for telemetri) til 5301, så tar begge opp.

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Delt minne som spillet skriver til apper: `Local\acpmf_physics`,
`Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`).
Åpnes skrivebeskyttet og først når spillet har laget det (`simracing_shm`). Posisjonen er gjennomsnittet av de fire dekkenes kontaktpunkter, verdens meter, Y opp.
Runder etter spillets teller (AC, ACC) eller ved at bilen passerer startpunktet igjen
(AC EVO, AC Rally), slik `kunos.py` gjør for rundeopptakeren.

#### Alt som lagres {#everything-kept}

Radene er noen få i sekundet; spillene sender langt flere. Hver UDP-pakke som kommer inn - i menyene, mellom runder, og de som ingen dekoder leser - lagres uendret
i øktens `heat.raw.parquet` under sitt format (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), og hver side i delt minne (hele
området, ikke bare de bytene som dekodes) hver gang den endrer seg, under
navnet på området (`acpmf_physics`, ...). `used` markerer det som også ble til
rader; `selfCheck.completeness` i `meta.json` teller hver type (3DHeat sin
regel for konvertering).

Den samme modulen dekker også: [Assetto Corsa Competizione (live-data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (live-data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (live-data)](game-assetto-corsa-rally.md), [BeamNG.drive (live-data)](game-beamng.md), [DiRT Rally 2.0 (live-data)](game-dirt-rally-2.md), [EA SPORTS WRC (live-data)](game-ea-wrc.md), [Forza Horizon 4 (live-data)](game-forza-horizon-4.md), [Forza Horizon 5 (live-data)](game-forza-horizon-5.md), [Forza Horizon 6 (live-data)](game-forza-horizon-6.md), [Forza Motorsport (live-data)](game-forza-motorsport.md), [Richard Burns Rally (live-data)](game-richard-burns-rally.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner lagres | ja |
| Opp-akse | `y` |
| Enheter | meter |
| Speilvendt for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet` sin footer, så 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som «tillatt (leser bare det spillet publiserer)».
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne spillet publiserer), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som lagres {#statistics-recorded}

Statistikknøklene denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

En nøkkel i klammeparenteser blir fullført under kjøring (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell med spillets felter eller fra spillets egne statistikknavn, står ikke på listen; «Hva som lagres» over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeat sin [regel for konvertering](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller lagres, og slettes aldri. I tillegg til radene blir hver pakke, side, linje eller respons adapteren mottar, lagret uendret i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt som beholdes med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- rader 10 ganger i sekundet fra fysikksiden: posisjon (gjennomsnittet av dekkenes kontaktpunkter), fart, gir, gass, brems, giring/stigning/rulling (rad), turtall, styring (slik siden har den); øktstart med bane og bil fra statisk side; runder, posisjon i løpet

**Lagres uendret**

- hver side hel - hele minneområdet, ikke bare bytene som dekodes - hver gang bytene endrer seg, med watcherens lesing 10 ganger i sekundet: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; en ny lesing som er byte for byte lik den forrige, telles i `unchanged_reads` i meta.json og lagres ikke på nytt
- alt som bare dekodes for rundefiler (`decoders/kunos.py`: slip, last, trykk, temperaturer, camber, fjæring, kontaktpunkter, bremsetemperaturer, slip ratio og vinkel per hjul; hastighet i verden og i bilens eget system, vinkelhastighet, hjelpemidler) ligger i disse sidene

**Ikke tilgjengelig**

- andre biler sine posisjoner: sidene beskriver bare spillerens bil (ACC sin grafikkside har bil-id-er og koordinater for andre i noen versjoner - de lagres i den rå siden, men dekodes ikke)
- fysikktikk mellom watcherens lesinger: spillet skriver om siden i sin fysikkrate (opptil 333 Hz), og watcheren leser 10 ganger i sekundet

**Størrelse**: omtrent 150-300 MB per time før komprimering (et 4 KB-område per side, opptil 10 endringer i sekundet); sidene er for det meste nuller, og zstd beholder en liten brøkdel

## Verifisert {#verified}

dekodingen er rundeopptakerens i gamecapture (testet med syntetiske sider); adapteren testet mot delt minne bygd i testen fra det dokumenterte oppsettet; ikke testet mot spillet

## Kilde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
