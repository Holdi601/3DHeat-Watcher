---
title: "DiRT Rally 2.0 (live-data)"
nav_order: 11
lang: "no"
source: game-dirt-rally-2.md
source_hash: "367131ff990b"
nav_exclude: true
search_exclude: true
---
# DiRT Rally 2.0 (live-data) {#dirt-rally-20-live-data}

Mens du spiller DiRT Rally 2.0, lagrer watcheren de dataene spillet selv sender ut, slik at du kan se på dem senere på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `dirt-rally-2`, type [`telemetry`](sources-and-rules.md); den kjører mens `dirtrally2.exe` kjører, og ser etter nye data hvert 0,1 s.*

## Hva som lagres {#what-is-recorded}

- egen bils posisjon (verdens XYZ, m) 10 ganger i sekundet, med fart, gir, gass, brems og distanse i etappen
- etappestart (når etappeklokken starter), målgang med etappetiden, omstarter
- teleporteringer (en tilbakestilling til veien): `teleport` der bilen var, `spawn` der den er nå
- etapper, beste etappetid, distanse, toppfart

## Hvor dataene kommer fra {#where-it-comes-from}

UDP 127.0.0.1:20777, extradata=3 (Documents\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config.xml); mens en annen app holder 20777, lar watcheren porten være til den

## Slik slår du det på {#how-to-switch-it-on}

`python -m heat3d_watch setup dirt-rally-2 --apply` setter &lt;udp enabled="true" extradata="3"> (sikkerhetskopi tas først)

Skriv kommandoen i en terminal som er åpnet i watcherens mappe (se [Før du starter](before-you-start.md)). Hvis den feiler, sier siste linje hvorfor; [Installere og kjøre](installing-and-running.md) dekker de vanligste årsakene.

`python -m heat3d_watch setup dirt-rally-2` viser filene den ville endret; `python -m heat3d_watch setup dirt-rally-2 --apply` endrer dem og beholder originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `dirt-rally-2: changed: ...` for hver endring, eller `dirt-rally-2: nothing to change` når den allerede er på.

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

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: WRC sin `Documents/My Games/WRC/telemetry/config.json` (`wrc`-strukturens
`session_update`-pakke), DiRT sin `hardware_settings_config.xml`
(`<udp enabled="true" extradata="3" port="20777">`), RBR sin NGP-plugin
(`udpTelemetry=1`, port 6776). Etapper etter spillets etappeklokke
(`rally.StageSplitter`). RBR dokumenterer ikke sine akser: opp-aksen er den
som etappen varierer minst langs, avgjort når økten avsluttes.

#### Alt som lagres {#everything-kept}

Radene er noen få i sekundet; spillene sender langt flere. Hver UDP-pakke som kommer inn - i menyene, mellom runder, og de som ingen dekoder leser - lagres uendret
i øktens `heat.raw.parquet` under sitt format (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), og hver side i delt minne (hele
området, ikke bare de bytene som dekodes) hver gang den endrer seg, under
navnet på området (`acpmf_physics`, ...). `used` markerer det som også ble til
rader; `selfCheck.completeness` i `meta.json` teller hver type (3DHeat sin
regel for konvertering).

Den samme modulen dekker også: [Assetto Corsa (live-data)](game-assetto-corsa.md), [Assetto Corsa Competizione (live-data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (live-data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (live-data)](game-assetto-corsa-rally.md), [BeamNG.drive (live-data)](game-beamng.md), [EA SPORTS WRC (live-data)](game-ea-wrc.md), [Forza Horizon 4 (live-data)](game-forza-horizon-4.md), [Forza Horizon 5 (live-data)](game-forza-horizon-5.md), [Forza Horizon 6 (live-data)](game-forza-horizon-6.md), [Forza Motorsport (live-data)](game-forza-motorsport.md), [Richard Burns Rally (live-data)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

En nøkkel i klammeparenteser blir fullført under kjøring (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell med spillets felter eller fra spillets egne statistikknavn, står ikke på listen; «Hva som lagres» over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeat sin [regel for konvertering](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller lagres, og slettes aldri. I tillegg til radene blir hver pakke, side, linje eller respons adapteren mottar, lagret uendret i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt som beholdes med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- rader 10 ganger i sekundet: posisjon, fart, gir, gass, brems, distanse i etappen, giring, turtall, styring; etappestart, målgang med etappetiden, omstarter

**Lagres uendret**

- hver pakke som når porten, hel, i spillets takt, under sitt format: `extradata3` (66 flyttall, 264 byte), `extradata3-64` (DiRT Rallys 64), `<n>-byte` ellers
- i pakken, utover radene: alle 66 flyttallene - hastighet i verden, sidevektor og fremoverrettet vektor, fjæringsposisjon og fart per hjul, fart i kontaktflaten og bremsetemperatur, g-krefter, runder, etapplengde; flyttallene uten fastsatt navn ligger i rundefiler som `float<i>`

**Ikke tilgjengelig**

- andre biler: spillene sender bare spillerens bil
- en kanal for håndbrems: pakken har ingen

**Størrelse**: omtrent 70 MB per time ved 60 pakker i sekundet (264 byte pluss 70 byte med overskrift per post); zstd beholder en brøkdel

## Verifisert {#verified}

dekodingen er rundeopptakerens i gamecapture (testet med pakker bygd etter de dokumenterte oppsettene); adapteren testet med pakker bygd i testen og sendt over UDP; ikke testet mot spillet

## Kilde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
