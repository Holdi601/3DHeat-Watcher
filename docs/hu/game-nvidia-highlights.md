---
title: "NVIDIA highlights (platform)"
nav_order: 34
lang: "hu"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (platform) {#nvidia-highlights-platform}

A watcher elmenti, amit az NVIDIA highlights a játékaidról megőriz, hogy később a játékaid történetét a 3DHeat-megjelenítőben térképen megnézhesd.

*Műszaki részletek: adapter `nvidia-highlights`, típus [`platform`](sources-and-rules.md); folyamatosan fut (nem vár arra, hogy játék induljon), és 10 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- minden új klip, highlight vagy képernyőkép: játék, fájl, típus, hossz és a pillanat (falióra szerinti ezredmásodperc)
- a highlight azonosítója és neve, ha a játék regisztrálta az NVIDIA-nál
- hol volt a játékos abban a pillanatban, ha egy másik adapter rögzítette ugyanazt a játékot akkor
- a GfeSDK-s játékok naplózott highlight-kérései, akkor is, ha nem marad meg klip

## Honnan származik {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;game>\config.json; a klipek a rögzítési mappában (%USERPROFILE%\Videos\NVIDIA\\&lt;Game>\\\*.mp4) és &lt;temp>\Highlights\\&lt;game> mappában; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Bekapcsolás {#how-to-switch-it-on}

NVIDIA App: az Azonnali visszajátszás vagy a Highlights bekapcsolva, a klipek billentyűvel vagy a játék által mentve

## Működés {#how-it-works}

Amit az indító és a grafikus illesztőprogram megőriz a játékról: a Steam statisztikái, eredményei, játékideje és idővonalai, valamint az NVIDIA highlight-jei és klipjei.

Egyik forrás sem igényli, hogy a játék együttműködjön vagy fusson, ezért a három itteni adapter mindig be van kapcsolva, és néhány fájlt néhány másodpercenként néz meg.

#### NVIDIA highlight-ok és klipek (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Amit az NVIDIA App / GeForce Experience megőriz, mindez itt van:
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay` alatt:
```text
UGCTracker.json      the gallery index: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, when the file was written), profileName, drsName
                     (the exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (where clips are saved),
                     settings.tempDirectory (highlights wait in
                     <temp>\Highlights\<game> until saved)
Highlights\<game>\config.json  the highlight kinds a game registered:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
és maguk a klipfájlok, `<rögzítési mappa>\<Game>\<Game> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (a képernyőképek: `<Game> Screenshot yyyy.mm.dd - ...png`), a fájlnév idejét a mentés helyi ideje adja. A GfeSDK-s játékok a highlight-hívásaikat is naplózzák a `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` fájlban.

Mit tud és mit nem tud ez: a GfeSDK-t támogató játék (NVIDIA Highlights) a highlight-típusait egyszer regisztrálja - egy azonosítót, mint "kill", egy jelentőséget, címkéket, egy megjelenítendő nevet -, később pedig csak ennyit mond: "highlight <id>, from <ms> before now to <ms> after". Nincsenek pozíciók, nincs mérkőzés vagy kör, nincs ellenfél, nincs egyéni adat: az SDK-ban nincs mező ezekre. Egy mentett klip egy fájlt, egy játéknevet, egy hosszt és egy időt ad hozzá. Tehát az, ami rögzítődik: "ilyen típusú pillanat, ebben a játékban, ebben az időben" - a hely pedig csak úgy kerül elő, hogy az időt megkeressük egy másik adapter ugyanazon játék felvételében (`position_at`), amit ez az adapter minden rögzített klipnél megtesz.
<https://developer.nvidia.com/highlights>

Minden adapter elmenti, amit már látott, a `<data>\state\<id>.json` fájlba, így az újraindítás nem rögzít semmit kétszer.

Minden munkamenet azt is egészben megőrzi, amiből a sorai születtek (a 3DHeat konvertáló szabálya szerint, a megjelenítő repójának docs/converters.md fájlja), a `heat.raw.parquet`-ban: a statisztikafájl és a sémája bájtjai és a játék localconfig blokkja (steam-stats; az a statisztikafájl, amelyet a dekóder nem tud olvasni, csak a bájtjait tartalmazó munkamenetet kap), az idővonal-fájl fejléce és minden bejegyzése JSON-ként (steam-timeline), minden klip galériaindex-bejegyzése, a játék highlight-definíciói és minden GfeSDK-naplósor, azok is, amelyek nem highlight-kérések (nvidia-highlights).

A ugyanez a modul szolgálja ki még: [Steam statisztikák (platform)](game-steam-stats.md), [Steam Timeline (platform)](game-steam-timeline.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | csak kölcsönvett: az a hely, amelyet egy másik felvétel ugyanarra a játékra abban a pillanatban tárol |
| Felfelé mutató tengely | `y` |
| Mértékegységek | méter |
| Tükrözés a megjelenítőhöz | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek minden munkamenet `meta.json` fájljának `axes` mezőjébe kerülnek, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat-megjelenítő magától forgatja és méretezi a sorokat - lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játékként jelölve (`multiplayer`): **nem**. A `games --markdown` ezt "egyjátékos" formában mutatja.
- `platform` típus: csak azt olvassa, amit a játék vagy a platform kiad (amit a Steam vagy a grafikus illesztőprogram megőriz), ezért online játékban is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` típusú adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van megjelölve - lásd [Forrásak és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Azok a statisztikakulcsok, amelyeket ez az adapter kódja név szerint állít be (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`clip_seconds`, `clips`, `placed`, `screenshots`

A kapcsos zárójeles kulcsot futásidőben töltik ki (a `score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevei közül vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertáló szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megőrzi, sosem dobja el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőriz a munkamenet `heat.raw.parquet` fájlja (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), és a `meta.json` `selfCheck.completeness` mezője minden `type` értéket megszámol - a `lost` értéke 0.

**Beolvasva**

- minden új klip és képernyőkép: játék, fájl, típus, médium, hossz (az index, különben az MP4 fejléce), a pillanat a fájlnévből, a highlight azonosítója és neve, ha a játék regisztrálta, és a játékos helye akkor egy másik adapter felvételéből
- GfeSDK highlight-kérések (minden `Posted Request HL...`, kivéve a konfigurációs hívásokat) az idejükkel

**Nyersen megőrizve**

- `UGC`: a klip teljes bejegyzése a UGCTracker.json galériaindexből, minden mezője, amelyet az NVIDIA ír
- `clip_file`: olyan klipnél, amelyet az index nem sorol fel, a fájl útvonala, mérete, ideje és mappája
- `highlights_config`: a játék `Highlights\<game>\config.json` fájlja úgy, ahogy van (jelentőség, címkék, nevek minden nyelven), munkamenetenként egyszer
- `gfesdk_log`: a GfeSDK-naplók minden sora, amelyeket az első futás után olvastak; a `used` igaz a highlight-kérésekre, hamis a többire (konfiguráció, videobeállítások, az SDK saját üzenetei)

**Nem elérhető**

- maguk a klipek és képernyőképek: a videó és a képek ott maradnak, ahol az NVIDIA mentette; a sorok a fájlt nevezik meg
- ami az adapter első futása előtt történt: látottnak tekintjük, így az évekig tartó klipek nem válnak egyszerre munkamenetekké (`baseline`; a False rögzíti őket)
- a UGCTracker.json `apps` és `info` mezői és a GallerySettings.json: az alkalmazás beállításai, nem a játék pillanatai; a benne nevezett rögzítési mappa használatos
- pozíciók, körök, ellenfelek: a GfeSDK-ban nincs ezekre mező

**Méret**: klipenként körülbelül 1 KB, játékindításonként néhány KB definíció és naplósor: jóval 1 MB alatt óránként

## Ellenőrzés {#verified}

valódi galériaindexen, beállításokon, highlight-definíciókon és klipeken tesztelve, helyi telepítésből; a GfeSDK highlight-kérés sorai és a klipekben lévő highlight-azonosítók nincsenek tesztelve

## Forrás {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
