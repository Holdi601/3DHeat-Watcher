---
title: "osu! (visszajátszások)"
nav_order: 35
lang: "hu"
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (visszajátszások) {#osu-replays}

Egy osu!-mérkőzés után a watcher a játék által mentett visszajátszást olyan fájlokká alakítja, amelyeket térképen megnézhetsz a 3DHeat-megjelenítőben.

*Műszaki részletek: adapter `osu-replays`, típus [`replay`](sources-and-rules.md); folyamatosan fut (nem vár arra, hogy játék induljon), és 5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a kurzor útvonala a játéktéren (x 0..512, y 0..384) és a lenyomva tartott billentyűk, minden képkockánál
- pontszám, kombó, 300-as/100-as/50-es találatok, gekik, katuk, hibák, pontosság, módosítók, teljes kombó
- az életsáv a játék felett, a beatmap és a visszajátszás hasheink, a véletlen mag, az online pontszám-azonosító

## Honnan származik {#where-it-comes-from}

az osu! (stabil) által mentett visszajátszások: %LOCALAPPDATA%/osu!/Data/r/\*.osr (minden játék) és osu!/Replays/\*.osr (exportált)

## Bekapcsolás {#how-to-switch-it-on}

Semmit sem kell bekapcsolni: a watcher úgy olvassa a forrást, ahogy a játék vagy a platform biztosítja.

## Működés {#how-it-works}

Visszajátszások és demók: amit a játék egy mérkőzésről ment, a mérkőzés befejezése után alakítva.

A visszajátszás mindent tartalmaz, amit az élő felület a többjátékos játékokban visszatart - minden játékos pozícióját, minden ölést ott, ahol történt -, és ez egy fájl, amelyet a játék a játékosainak ír, ezért az olvasása nem érint semmit a játékban. A watcher figyeli azokat a mappákat, ahová a játékok mentik őket, megvárja, amíg egy új fájl már nem nő (különben a játék még írja), és egy munkaszálban alakítja át, hogy egy hosszú átalakítás ne tartsa fel a watcher többi részét.

Amikor egy mappát először látnak, a benne lévő visszajátszásokat csak megjegyzik, nem alakítják át: egy több évnyi demót tartó játékos különben egy napig foglalt watchert találna. A `python -m heat3d_watch replays <adapter> [mappa]` kérésre átalakítja a meglévőket.

#### osu! {#osu}

Az osu! (stabil) minden játékot a `osu!/Data/r/*.osr` fájlba ment, az exportáltakat pedig az `osu!/Replays/` mappába. A watcher maga olvassa őket, az osu! wiki által közzétett formátum szerint: a kurzor útvonalát és billentyűit minden képkockánál, a pontszámsort, az életsávot, a magot és a pontszám-azonosítót; a fájl egészben, részenként, mellette megmarad a munkamenet `heat.raw.parquet` fájljában.

A ugyanez a modul szolgálja ki még: [Counter-Strike 2 (visszajátszások)](game-cs2-demos.md), [Dota 2 (visszajátszások)](game-dota-replays.md), [Squad (visszajátszások)](game-squad-demos.md), [War Thunder (visszajátszások)](game-warthunder-replays.md), [World of Tanks (visszajátszások)](game-wot-replays.md), [World of Warships (visszajátszások)](game-wows-replays.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `y` |
| Mértékegységek | osu! pixel (játéktér 512 x 384) |
| Tükrözés a megjelenítőhöz | `z` |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek minden munkamenet `meta.json` fájljának `axes` mezőjébe kerülnek, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat-megjelenítő magától forgatja és méretezi a sorokat - lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt "engedélyezett (csak azt olvassa, amit a játék közzétesz)" formában mutatja.
- `replay` típus: csak azt olvassa, amit a játék vagy a platform kiad (a játék által mentett visszajátszások és demók), ezért online játékban is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` típusú adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van megjelölve - lásd [Forrásak és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Azok a statisztikakulcsok, amelyeket ez az adapter kódja név szerint állít be (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`accuracy`, `full_combo`

A kapcsos zárójeles kulcsot futásidőben töltik ki (a `score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevei közül vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertáló szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megőrzi, sosem dobja el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőriz a munkamenet `heat.raw.parquet` fájlja (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), és a `meta.json` `selfCheck.completeness` mezője minden `type` értéket megszámol - a `lost` értéke 0.

**Beolvasva**

- minden képkocka: egy sor az idejénél (az ezredmásodpercek összeadva), x és y a játéktéren, a `keys` a billentyűbitek (egér 1 és 2, billentyű 1 és 2, füst); a mania módban az x a lenyomott billentyűket tartalmazza hely helyett
- a fejléc, minden mezővel: mód, verzió, a beatmap MD5-je (a fájl a beatmapet csak ezzel nevezi meg), a játékos, a visszajátszás MD5-je, 300-as, 100-as, 50-es, gekik, katuk, hibák, pontszám, maximális kombó, teljes kombó, módosítók (névvel a meta.json `osu.modNames` mezőjében), a játék ideje - statisztikaként és a meta.json `osu` mezőjében
- az életsáv-grafikon: egy `life` sor pontonként (idő, élet 0..1)
- a `-12345` képkocka: a véletlen mag (`osu.seed`); az online pontszám-azonosító (`osu.scoreId`); célgyakorlásnál annak pontossága (`osu.targetPracticeAccuracy`)

**Nyersen megőrizve**

- a fájl egészben, részenként, a heat.raw.parquet fájlban (az `offset` mutatja, hol kezdődik minden rész, így a részek adják ki a fájlt): `header`, `replay_data` (az LZMA-tömörített képkockák, ahogy tárolódnak), `score_id`, `mod_info`, és `trailing` mindenre, ami a formátum által leírt részek után következik (az osu!lazer exportjai ide írnak adatot) - megőrizve, nem olvasva

**Nem elérhető**

- maga a beatmap (találati objektumok, időzítés): nincs a visszajátszásban; csak az MD5-je nevezi meg
- az osu!lazer saját visszajátszásai: az adatbázisában tárolódnak, nem fájlként

**Méret**: a nyers mellékfájl nagyjából a visszajátszás mérete (tíz-száz kilobájt)

## Ellenőrzés {#verified}

a közzétett .osr formátum szerint épített visszajátszásokon tesztelve; az osu!lazer a saját tárolójában tartja a visszajátszásait, ezeket nem olvassuk

## Forrás {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
