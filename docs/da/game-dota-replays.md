---
title: "Dota 2 (replays)"
nav_order: 12
lang: "da"
source: game-dota-replays.md
source_hash: "88539ee6dc65"
nav_exclude: true
search_exclude: true
---
# Dota 2 (replays) {#dota-2-replays}

Efter en kamp i Dota 2 laver watcheren de replay, spillet har gemt, om til filer, du kan se på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `dota-replays`, slags [`replay`](sources-and-rules.md); den kører hele tiden (den venter ikke på at et spil starter) og kigger efter nye data hvert 5. s.*

## Hvad der optages {#what-is-recorded}

- hver helts position, højde, liv og level, 7,5 gange i sekundet mens de er i live
- drab og dødsfald der hvor de skete; tårne, barakker, Roshan og Tormentors der hvor de faldt; wards der hvor de blev plantet
- hver spillers kort-pings, kort-tegninger og ordrer (flyt, angreb, cast, køb, ...) der hvor de pegede
- scoren og hver spillers linje; den loggede ind spillers som statistik
- alt andet replayet indeholder, gemt helt ved siden af tabellen: hver frame og netværksbesked, hver ændring af entitetsegenskaber, hver post i strengtabellen

## Hvor det kommer fra {#where-it-comes-from}

replays Dota 2 gemmer: &lt;Dota>/game/dota/replays/&lt;match id>.dem (hentet i klienten, eller med `dota-replay <match id>`)

## Sådan slår du det til {#how-to-switch-it-on}

hent en kamps replay i Dota 2, eller hent et offentligt: `python -m heat3d_watch dota-replay <match id>`; installer læseren: github.com/Holdi601/3DHeat-Ext-DotaReplay (`heat3d-dota-replay`, medbringer gem-dota)

Skriv kommandoen i en terminal, der er åbnet i watcherens mappe (se [Før du går i gang](before-you-start.md)). Hvis det fejler, siger den sidste linje hvorfor; [Installation og kørsel](installing-and-running.md) dækker de almindelige årsager.

Indstillinger fra miljøvariabler:

- `HEAT3D_DOTA_REPLAY`: læserens mappe (en klon eller udpakket udgivelse), når den ikke er installeret eller ligger ved siden af watcheren

## Sådan virker det {#how-it-works}

Replays og demoer: hvad et spil gemmer af en kamp, konverteret én gang, når kampen er slut.

Et replay indeholder alt, en live-grænseflade holder tilbage i multiplayer-spil -
hver spillers position, hvert drab der hvor det skete - og det er en fil, spillet
skriver til sine spillere, så at læse den rører ikke ved spillet. Watcheren kigger i
de mapper, spil gemmer dem i, venter, til en ny fil er holdt op med at vokse (ellers
skriver spillet stadig på den), og konverterer den i en arbejdstråd, så en lang
konvertering aldrig holder resten af watcheren op.

Første gang en mappe ses, bliver replayene, der allerede ligger i den, kun noteret,
ikke konverteret: en spiller med års demoer ville ellers opleve, at watcheren var
optaget i et døgn. `python -m heat3d_watch replays <adapter> [folder]` konverterer de
eksisterende på forespørgsel.

#### Dota 2 {#dota-2}

Dota 2 gemmer de replays, en spiller henter (en kamps detaljer, eller Watch >
Replays) i `<Dota>/game/dota/replays/<match id>.dem`; Valve gemmer hver offentlig
kamps replay på sine servere i nogle uger, og `python -m heat3d_watch
dota-replay <match id>` henter et replay ud fra dets id via OpenDota. Watcheren læser
dem ikke selv: en ekstern læser gør det (3DHeat Dota Replay,
github.com/Holdi601/3DHeat-Ext-DotaReplay, `exporters/ext/dota-replay`, kommando
`heat3d-dota-replay`, der læser via gem-dota, MIT), et projekt for sig,
kørt i en proces for sig selv på hvert nyt replay, når den
er på PATH, installeret eller ved siden af watcheren; mangler den, siger watcheren én
gang, hvordan den installeres. Den skriver hver helts position, højde, liv, level,
retning, mana, erfaring, attributter og genstande 7,5 gange i sekundet, mens de er i
live, drab og dødsfald der hvor de skete, tårne, barakker, Roshan og Tormentors der
hvor de faldt, hver ward hvor den blev plantet og hvor den endte, kamploggens poster
om heltene (skade, heling, evner, genstande, køb, runer, guld, erfaring, modifikatorer),
og hver spillers kort-pings, kort-tegninger og ordrer - i `dota/<match>.parquet`; hver
anden enhed (creeps, summons, illusioner, kurerer, bygninger) én gang i sekundet i
`<match>.units.parquet`; hele kamploggen i `<match>.combatlog.parquet`; og kampen, chatten,
draften, alt andet udtrækket fra parseren og spillets egen slutningsoversigt i
`<match>.match.json`, i sessionsmappen. Alt andet replayet indeholder, gemmes helt ved
siden af dem (3DHeats konverterregel): hver frame og netværksbesked i
`<match>.packets.parquet`, hver ændring af en entitets egenskab i
`<match>.entities.parquet`, hver post i strengtabellen i `<match>.strings.parquet`,
talt i dokumentets `selfCheck.completeness`. Positionerne er Dotas verdensenheder,
de samme som game-state-integrationen melder. Den loggede ind spillers linje på
scoreboardet bliver sessionens statistik: drab, dødsfald, assists, last hits, denies,
nettoværdi, GPM, XPM, heltens skade, wards, og om kampen blev vundet. En ny Dota-patch
kan ændre replayets entiteter, før gem følger med; et replay gem ikke kan læse til
ende, konverteres så langt det kan, og markeres `incomplete` i sin opsummering.

Det samme modul betjener også: [Counter-Strike 2 (replays)](game-cs2-demos.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner optaget | ja |
| Opadakse | `z` |
| Enheder | Dota-verdensenheder (Hammer-enheder; kortet er cirka 16400 på tværs) |
| Spejlet for viewer | `y` |
| Enhedsskala (`scale`: viewer ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, i `heat.parquet`s footer, så 3DHeat-viewer selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Multiplayer {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "allowed (reads only what the game publishes)".
- Slags `replay`: den læser kun det, spillet eller platformen udleverer (replays og demoer, spillet gemmer), så den optager også i online-spil, ligesom offline; flaget afgør kun, om hukommelsen nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der optages {#statistics-recorded}

Statistiknøglerne, som denne adapters kode sætter med navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der optages" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Konverteren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det replayet indeholder bliver læst eller gemt, aldrig smidt væk. Ud over tabellen gemmes alt andet replayet indeholder helt i sidecars ved siden af den, i sessionens `dota/`-mappe - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (kolonnerne `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, efter hvad der gælder) - og kampdokumentets (`<match>.match.json`) `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- tabellen (`dota/<match>.parquet`): hver helts position, højde, liv, level, retning, mana, erfaring, attributter, rustning, hastighed, skade, genstande og spillerens markør 7,5 gange i sekundet; drab, dødsfald, mål, wards, kamploggens poster om helte; kort-pings (`ping`, DOTA_UM_LocationPing), kort-tegninger (`map_line`, DOTA_UM_MapLine) og hver enheds-ordre (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` ordretypen, `value` evnens eller genstandens id, `text` målets klasse; ved det bestilte punkt, ellers ved helten)
- `<match>.units.parquet`: hver anden enhed én gang i sekundet; `<match>.combatlog.parquet`: hele kamploggen, som gem læser den, hvert felt
- kampdokumentet: alt gem udtrækker, og replayets egne poster helt - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: afspilningens længde, hver spillers navn, helt, Steam-id, hold), `matchDetails` (DOTA_UM_MatchDetails: spilkoordinatorens slutoversigt, hver spillers tal, genstande, skade efter type, valg og forbud) og `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: drab, dødsfald, assists, level, last hits og denies som læst fra strømmen mod `matchDetails`, pr. spiller

**Gemt rå**

- `<match>.packets.parquet`: hver frame, der ikke er en pakke (`type` `frame <n>`), og hver netværksbesked (`message <n>`, `name` Valves), helt i `payload`, i filens rækkefølge (`seq`, `frame`), med `decoded` protobuf'en som JSON (et bytes-felt givet ved sin længde), hver beskedtype afkodet: svc_PacketEntities (entitetsstrømmen), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, kamploggens beskeder, GE_SosStartSoundEvent, DOTA_UM_TE_\* (projektiler, animationer, blod), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; send-tabellerne, klasselisten og serverinfo, som en senere entitetsafkoder har brug for, er blandt dem
- `<match>.entities.parquet`: hver entitets hver egenskab, hver gang den ændrede sig (`type` egenskaben, `name` klassen, `entity` dens indeks; `value`, `vector` eller `decoded`), dens hele tilstand når den oprettes, og hver oprettelse, indtræden, udtrædelse og sletning - millioner af rækker for en hel kamp
- `<match>.strings.parquet`: hver post i strengtabellen fra hver opdatering og hver fuld snapshot, værdien helt; `userinfo`, `ActiveModifiers` og `EconItems` afkodet fra deres protobufs
- `selfCheck.completeness` i kampdokumentet tæller frames og beskeder efter Valves navn, kamploggens poster (`combatlog <type>`), spilhændelser (`gameevent <name>`), poster i strengtabellen (`stringtable <name>`) og entitetsopdateringer (`entity <class>`); nogle få gemmes kun rå (fulde entitets-snapshots, som gem springer over, fordi den bygger op af deltaerne, og poster i tabeller, som ingen værdi læser), lost 0

**Ikke tilgængeligt**

- stemme: replayet har stemmeopsætningen, men ingen stemmedata
- navne bag hashes og id'er: lyde og partikler er navngivet med hashes af spillets filer, evner med id'er; replayet bærer ikke navnene (genstande navngives gennem gems katalog, hvor det har dem)
- alt, kun spillernes egne klienter kendte (deres kamera, deres skærm) ud over det serveren udsendte; markøren og hver ordre er med

**Størrelse**: sidecars tilsammen er lidt større end selve replayet, pakkerne og entiteterne de største; en hel kamp tager et minut eller to i én proces

## Verificeret {#verified}

kontrolleret på et offentligt kamps replay: drab, dødsfald, assists, level, last hits og denies stemmer med spillets egen slutoversigt for alle ti spillere; hver besked i pakke-sidecar'en serialiseres igen byte for byte; tabellen og statistikken ved tests på syntetiske data

## Kilde {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
