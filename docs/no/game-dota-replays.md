---
title: "Dota 2 (repriser)"
nav_order: 12
lang: "no"
source: game-dota-replays.md
source_hash: "88539ee6dc65"
nav_exclude: true
search_exclude: true
---
# Dota 2 (repriser) {#dota-2-replays}

Etter en kamp i Dota 2 gjør watcheren om repriser spillet har lagret, til filer du kan se på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `dota-replays`, type [`replay`](sources-and-rules.md); den kjører hele tiden (den venter ikke på at et spill starter) og ser etter nye data hvert 5. s.*

## Hva som tas opp {#what-is-recorded}

- hver helts posisjon, høyde, helse og nivå, 7,5 ganger i sekundet mens helten lever
- drap og dødsfall der de skjedde; tårn, kaserner, Roshan og Tormentors der de falt; wards der de ble plantet
- hver spillers kartmarkeringer, kart-tegninger og ordrer (flytt, angrip, bruk evne, kjøp, ...) der de pekte
- poengsummen og hver spillers linje; den innloggede spillerens som statistikk
- alt annet reprisen inneholder, tatt vare på helt ved siden av tabellen: hver ramme og nettverksmelding, hver endring av entitetsegenskaper, hver oppføring i strengtabellen

## Hvor det kommer fra {#where-it-comes-from}

repriser Dota 2 lagrer: &lt;Dota>/game/dota/replays/&lt;match id>.dem (lastet ned i klienten, eller med `dota-replay <match id>`)

## Slik slår du det på {#how-to-switch-it-on}

last ned en kamps reprise i Dota 2, eller hent en offentlig: `python -m heat3d_watch dota-replay <match id>`; installer leseren: github.com/Holdi601/3DHeat-Ext-DotaReplay (`heat3d-dota-replay`, tar med gem-dota)

Skriv kommandoen i en terminal som er åpnet i watcher-mappen (se [Før du starter](before-you-start.md)). Hvis den feiler, sier siste linje hvorfor. [Installere og kjøre](installing-and-running.md) dekker de vanlige årsakene.

Innstillinger fra miljøvariabler:

- `HEAT3D_DOTA_REPLAY`: leserens mappe (en klone eller utpakket utgivelse), når den ikke er installert eller ligger ved siden av watcheren

## Slik fungerer det {#how-it-works}

Repriser og demoer: det et spill lagrer av en kamp, konvertert når kampen er ferdig.

En reprise inneholder alt et live-grensesnitt holder tilbake i flerspillerspill - hver spillers posisjon, hvert drap der det skjedde - og det er en fil spillet skriver for sine spillere, så å lese den rører ingenting i spillet. Watcheren ser på mappene spill lagrer dem i, venter til en ny fil slutter å vokse (spillet skriver fortsatt til den ellers), og konverterer den i en arbeidstråd, slik at en lang konvertering aldri stopper resten av watcheren.

Første gang en mappe ses, bare noteres repriser som allerede ligger der, de konverteres ikke: en spiller med år med demoer ville ellers fått watcheren opptatt i et døgn. `python -m heat3d_watch replays <adapter> [folder]` konverterer de eksisterende på forespørsel.

#### Dota 2 {#dota-2}

Dota 2 lagrer repriser en spiller laster ned (en kamps detaljer, eller Watch > Replays) i `<Dota>/game/dota/replays/<match id>.dem`; Valve beholder hver offentlig kamps reprise på sine servere i noen uker, og `python -m heat3d_watch dota-replay <match id>` henter en etter id via OpenDota. Watcheren leser dem ikke selv: en ekstern leser gjør det (3DHeat Dota Replay, github.com/Holdi601/3DHeat-Ext-DotaReplay, `exporters/ext/dota-replay`, kommandoen `heat3d-dota-replay`, som leser gjennom gem-dota, MIT), et eget prosjekt, og kjøres i en egen prosess for hver ny reprise når den står på PATH, er installert eller ligger ved siden av watcheren; mangler den, sier watcheren én gang hvordan den installeres. Den skriver hver helts posisjon, høyde, helse, nivå, retning, mana, erfaring, egenskaper og gjenstander 7,5 ganger i sekundet mens helten lever, drap og dødsfall der de skjedde, tårn, kaserner, Roshan og Tormentors der de falt, hver ward der den ble plantet og der den forsvant, kamploggens oppføringer om heltene (skade, helbredelse, evner, gjenstander, kjøp, runer, gull, erfaring, modifikatorer), og hver spillers kartmarkeringer, kart-tegninger og ordrer - inn i `dota/<match>.parquet`; hver annen enhet (kryp, påkalte, illusjoner, kurerer, bygninger) én gang i sekundet inn i `<match>.units.parquet`; hele kamploggen inn i `<match>.combatlog.parquet`; og kampen, chatten, draften, alt annet leseren henter ut og spillets egen postkamp-oppføring inn i `<match>.match.json`, i øktmappen. Alt annet reprisen inneholder tas vare på helt ved siden av dem (konverteringsregelen til 3DHeat): hver ramme og nettverksmelding i `<match>.packets.parquet`, hver endring av entitetsegenskaper i `<match>.entities.parquet`, hver oppføring i strengtabellen i `<match>.strings.parquet`, talt i kampdokumentets `selfCheck.completeness`. Posisjoner er Dotas verdensenheter, de samme som spillets game-state integration melder. Den innloggede spillerens linje på resultattavlen blir øktens statistikk: drap, dødsfall, assists, last hits, denies, nettoverdi, GPM, XPM, heltedskade, wards og om kampen ble vunnet. En ny Dota-patch kan endre entitetene i reprisen før gem følger med; en reprise gem ikke kan lese til slutten, konverteres så langt den rekker og merkes `incomplete` i sammendraget.

Samme modul brukes også av: [Counter-Strike 2 (repriser)](game-cs2-demos.md), [Squad (repriser)](game-squad-demos.md), [War Thunder (repriser)](game-warthunder-replays.md), [World of Tanks (repriser)](game-wot-replays.md), [World of Warships (repriser)](game-wows-replays.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner registreres | ja |
| Opp-akse | `z` |
| Enheter | Dota-verdensenheter (Hammer-enheter; kartet er omtrent 16400 på tvers) |
| Speilet for visningen | `y` |
| Enhetsskala (`scale`: visningen ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s footer, slik at 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "allowed (reads only what the game publishes)".
- Type `replay`: den leser bare det spillet eller plattformen gir ut (repriser og demoer spillet lagrer), så den tar opp også i nettspill, både på nett og offline; flagget avgjør bare om minnet noen gang kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill som er merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

En nøkkel i klammer fylles ut ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt eller fra spillets egne statistikknavn står ikke i denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Konverteringsverktøyet følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det reprisen inneholder, leses eller tas vare på, og slettes aldri. I tillegg til tabellen tas alt annet reprisen inneholder vare på helt i sidefiler ved siden av den, i øktens `dota/`-mappe - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (kolonnene `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, etter hvert som de gjelder) - og kampdokumentets (`<match>.match.json`) `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Leses**

- tabellen (`dota/<match>.parquet`): hver helts posisjon, høyde, helse, nivå, retning, mana, erfaring, egenskaper, armering, fart, skade, gjenstander og spillerens markør 7,5 ganger i sekundet; drap, dødsfall, mål, wards, kamploggens oppføringer om heltene; kartmarkeringer (`ping`, DOTA_UM_LocationPing), kart-tegninger (`map_line`, DOTA_UM_MapLine) og hver enhetsordre (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` ordretypen, `value` evne- eller gjenstands-id-en, `text` målets klasse; på punktet det ble gitt, ellers ved helten)
- `<match>.units.parquet`: hver annen enhet én gang i sekundet; `<match>.combatlog.parquet`: hele kamploggen slik gem leser den, hvert felt
- kampdokumentet: alt gem henter ut, og reprisens egne poster helt - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: spillelengde, hver spillers navn, helt, Steam-id, lag), `matchDetails` (DOTA_UM_MatchDetails: spillkoordinatorens postkamp-resultattavle, hver spillers tall, gjenstander, skade etter type, valg og forbud) og `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: drap, dødsfall, assists, nivå, last hits og denies slik de leses fra strømmen, mot `matchDetails`, per spiller

**Tatt vare på rått**

- `<match>.packets.parquet`: hver ramme som ikke er en pakke (`type` `frame <n>`) og hver nettverksmelding (`message <n>`, `name` Valves), hel i `payload`, i filrekkefølge (`seq`, `frame`), med `decoded` protobuf-en som JSON (et bytefelt gitt som sin lengde), hver meldingstype dekodet: svc_PacketEntities (entitetsstrømmen), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, kamploggmeldingene, GE_SosStartSoundEvent, DOTA_UM_TE_\* (prosjektiler, animasjoner, blod), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; sendetabellene, klasselisten og serverinfoen en senere entitetsdekoder trenger er blant dem
- `<match>.entities.parquet`: hver entitets hver egenskap hver gang den endret seg (`type` egenskapen, `name` klassen, `entity` dens indeks; `value`, `vector` eller `decoded`), dens hele tilstand når den ble laget, og hver opprettelse, innkomst, utgang og sletting - millioner av rader for en hel kamp
- `<match>.strings.parquet`: hver oppføring i strengtabellen fra hver oppdatering og hvert fullt øyeblikksbilde, verdien hel; `userinfo`, `ActiveModifiers` og `EconItems` dekodet fra sine protobufer
- `selfCheck.completeness` i kampdokumentet teller rammer og meldinger etter Valves navn, kamploggoppføringer (`combatlog <type>`), spillhendelser (`gameevent <name>`), oppføringer i strengtabellen (`stringtable <name>`) og entitetsoppdateringer (`entity <class>`); noen få tas bare vare på rått (hele entitetsøyeblikksbilder gem hopper over fordi den bygger fra endringene, og oppføringer i tabeller ingen leser verdiene i), tapt 0

**Ikke tilgjengelig**

- stemme: reprisen har stemmeoppsettet, men ingen stemmedata
- navn bak hasher og id-er: lyder og partikler er navngitt med hasher av spillets filer, evner med id-er; reprisen bærer ikke navnene (gjenstander navngis gjennom gems katalog der den har dem)
- alt bare spillernes egne klienter kjente (kameraet deres, skjermen deres) utover det serveren kringkastet; markøren og hver ordre er med

**Størrelse**: sidefilene til sammen er litt større enn selve reprisen, pakkene og entitetene størst; en hel kamp tar ett til to minutter i én prosess

## Verifisert {#verified}

kontrollert på en offentlig kamps reprise: drap, dødsfall, assists, nivå, last hits og denies stemmer med spillets egen postkamp-oppføring for alle ti spillerne; hver melding i pakkesidefilen serialiseres på nytt byte for byte; tabellen og statistikken ved tester på syntetiske data

## Kilde {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
