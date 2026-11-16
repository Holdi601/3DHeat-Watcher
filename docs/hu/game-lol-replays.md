---
title: "League of Legends (visszajátszások)"
nav_order: 30
lang: "hu"
source: game-lol-replays.md
source_hash: "216b88922360"
nav_exclude: true
search_exclude: true
---
# League of Legends (visszajátszások) {#league-of-legends-replays}

Egy League of Legends-meccs után a watcher a játék által mentett visszajátszást olyan fájlokká alakítja, amelyeket térképen megnézhetsz a 3DHeat megjelenítőben.

*Műszaki részletek: adapter `lol-replays`, típus [`replay`](sources-and-rules.md); mindig fut (nem vár a játék indulására), és 5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- minden játékos bajnoka, szerepe, csapata, ölései, halálai, asszisztjai, aranya, a bajnokoknak okozott sebzése és eredménye, valamint a meccs végi összesítő táblázat minden más száma
- a saját sorod statisztikaként, és a soraid a sajátodként megnevezve (meta.json `player`), a beállításokban megadott Riot ID-dal
- a saját Riot API-kulccsal: minden játékos pozíciója percenként a perc statisztikáival együtt, és az idővonal minden eseménye (ölések ott, ahol történtek, épületek, szörnyek, őrszemek, tárgyak, képességek), a falióra szerinti időben, ahogyan az idővonal adja
- a visszajátszásfájl minden része egészben a heat.raw.parquet fájlban; nincs dekódolva: a pillanatról pillanatra zajló játék, amely titkosított és a csalás ellen megzavarozott

## Honnan származik {#where-it-comes-from}

a League kliens által mentett visszajátszások: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (csak a sima meccs végi metaadatok); a saját Riot API-kulcsoddal a meccs hivatalos idővonala a Riot Match-V5 API-járól

## Hogyan kapcsold be {#how-to-switch-it-on}

Mentsd el a visszajátszást a League kliensben (meccselőzmények > letöltés); a pozíciókhoz állítsd be a riot_api_key és riot_platform értékeket a `config --set` paranccsal

## Hogyan működik {#how-it-works}

League of Legends és VALORANT visszajátszások: amit belőlük nyíltan lehet olvasni.

Mindkét játék a játékos lemezére menti a visszajátszásokat, és mindkettő védi a tartalmát: a pillanatról pillanatra zajló játékadatok megzavarozottak, és minden javítással másképp, hogy ne lehessen csalásra használni. Ezt a részt a 3DHeat sehol sem dekódolja. Amit minden fájl nyíltan hordoz, azt beolvassuk, a többit érintetlenül megtartjuk: a fájl minden része egészben, a munkamenet `heat.raw.parquet` fájljában (a 3DHeat konvertálási szabálya, a megjelenítő tárolójában a docs/converters.md), és a meta.json `selfCheck.completeness` adatai számolják.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Mindkét konténer-változat nyíltan, sima JSON-ként hordozza a meccs végi összesítő táblázatot (`statsJson`): tíz játékosonként a bajnokot, öléseket, halálokat, asszisztokat, aranyat, a bajnokoknak okozott sebzést, tárgyakat, csapatot, szerepet, győzelmet, Riot ID-jüket és minden más számot, amelyet a játék összesít (játékosonként több mint száz); ezek mind a játékos `player_result` sorává válnak. A ROFL1 (14.9-es javításig és azzal bezárólag) egy rögzített fejléc után hordozza (`RIOT\0\0`, egy 256 bájtos aláírás, majd a hosszúságok); a ROFL2 (14.11-től, `RIOT\2\0`) a fájl végén, a hosszát az utolsó négy bájt tartalmazza (egy Riot-mérnök mondja, ReplayBook 299-es hiba). A ROFL1 payload-fejléce (a játék azonosítója, hossza, a darabok és kulcskockák száma, a darabkulcs hossza) és a darabok táblázata (azonosító, típus, hossz, következő darab, eltolás) nyíltan vannak, és ezek olvashatók; maguk a darabok titkosítottak, érintetlenül, olvasatlanul megtartva. Az elrendezések a roflxd.cs (MIT) alapján készültek.

A pozíciók nem a fájlból jönnek. A játékos saját Riot fejlesztői kulcsával (`riot_api_key` a beállításokban; a személyes kulcs pontosan erre való: "a (saját) játékos-statisztikák megjelenítésére") a meccs hivatalos idővonalát a Riot Match-V5 API-járól kérjük le: minden játékos pozíciója percenként, mindazzal, amit a perc képkockája róluk mond (arany, tapasztalat, szint, minionok, bajnok- és sebzésstatisztikák), és az idővonal minden eseménye – ölések, épületek, elit szörnyek, őrszemek, tárgyak, képességek, szintek –, mindegyik egy sor, ahol van helye, ott a helyszínével. Kulcs nélkül semmi sem kérődik le, és semmi sem küldődik el.

Ugyanez a modul szolgálja ki még: [VALORANT (visszajátszások)](game-valorant-replays.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | a Summoner's Rift térkép egységei (kb. 15000 átmérő) |
| Tükrözés a megjelenítőnek | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json` fájljának `axes` mezőjébe, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe, így a 3DHeat megjelenítő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos mód {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így jeleníti meg: "engedélyezett (csak azt olvassa, amit a játék közzétesz)".
- Típus `replay`: csak azt olvassa, amit a játék vagy a platform kiad (a játék által mentett visszajátszásokat és demókat), ezért online játék közben is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van jelölve – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Ennek az adapternek a kódja névről név beállított statisztikakulcsai (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`champion`, `game_seconds`, `won`

A kapcsos zárójelben lévő kulcsot futásidőben töltik ki (`score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevéből vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertálási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megtartja, soha nem dobja el. A sorokon kívül minden csomagot, lapot, sort vagy választ, amelyet az adapter kap, egészben megtart a munkamenet `heat.raw.parquet` fájljában (oszlopai `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), a `meta.json` `selfCheck.completeness` adatai pedig minden `type`-ot számolnak – a `lost` értéke 0.

**Beolvasva**

- a metaadat-JSON: a játék hossza, a verzió, az utolsó darab és kulcskocka azonosítói, és a `statsJson` – minden játékos összesítő-táblázatának minden mezője a `player_result` során (a szövegként adott számok számként olvasva)
- ROFL1: a hosszúságok blokkja, a payload-fejléc (a játék azonosítója, a játék hossza, a kulcskocka- és darabszám, az indulási és játékkezdési darab-azonosítók, a kulcskockák közötti idő, a darabkulcs ahogy tárolva van) és a darabok táblázata (azonosító, típus, hossz, következő darab, eltolás) – a meta.json `rofl` mezőjében és a nyers sorok `text` mezőjében
- ROFL2: a verziószöveg
- a Match-V5 idővonal (csak a saját API-kulccsal): minden résztvevő-képkocka egy `position` soron (vagy `participant_frame` hely nélkül), minden mezőjével laposítva (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); minden esemény sorként a típusáról elnevezve, ahol van `position`, ott azon a helyen, a CHAMPION_KILL egy ölésként és egy halálként
 
**Nyers formában megtartva**

- a .rofl minden része egészben, a fájl sorrendjében (`offset`), így a részek kiadják a fájlt: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); bármely olyan szakasz, amelyet egy rész sem fed le, `unknown`-ként
- az idővonal egészben: `timeline <type>` minden eseményre, `timeline participantFrame` minden játékos képkockájára (`participant` a játékos azonosítója), `timeline` a többire

**Nem elérhető**

- maga a játék (pozíciók, képességek, minden egység, pillanatról pillanatra): a ROFL1 darabjai és a ROFL2 törzse titkosított, a bennük lévő csomagok pedig minden javítással megzavarozottak. Egészben megtartva, nincs olvasva
- pozíciók a saját Riot API-kulcs nélkül: a fájl nyíltan nem tartalmaz ilyet

**Méret**: a nyers melléklet nagyjából a visszajátszás saját mérete: a titkosított darabok nem tömörülnek

## Ellenőrizve {#verified}

a metaadat-olvasó a roflxd.cs (MIT) elrendezései szerint épített fájlokon tesztelve; az idővonal a Match-V5 dokumentált JSON-ján; valódi visszajátszás nem állt rendelkezésre az összevetéshez

## Forrás {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
