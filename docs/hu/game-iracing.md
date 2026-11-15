---
title: "iRacing (élő adatok)"
nav_order: 28
lang: "hu"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (élő adatok) {#iracing-live-data}

Amíg az iRacinget játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék kiküld, így később statisztikaként és idővonalként is megnézheted őket.

*Műszaki részletek: adapter `iracing`, típus [`telemetry`](sources-and-rules.md); akkor fut, amikor az `iRacingSim64DX11.exe` vagy az `iRacingSim64.exe` fut, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a vezetés 5 Hz-cel, pozíció nélkül (az iRacing élőben nem ad pozíciót): sebesség, fokozat, gáz, fék, kör, a kör hányada, versenyhelyezés és osztályhelyezés, incidensek
- munkamenet kezdete, beszállás és kiszállás az autóba, boxutca be- és kilépés, körök a köridővel, incidensek a pontjaikkal, kockás zászló, célba érés
- a játékmenet alatt írt .ibt telemetria-fájlok (szélesség, hosszúság, magasság – a megjelenítő ezeket olvassa)
- körök, legjobb kör, incidensek, versenyhelyezés, boxkiállások, távolság, legnagyobb sebesség
- a teljes megosztott memória a heat.raw.parquet fájlban: fejléc, változófejlécek, munkamenet-információ, minden beolvasott telemetriasor

## Honnan származik {#where-it-comes-from}

megosztott memória Local\IRSDKMemMapFileName (az iRacing SDK); .ibt fájlok a %USERPROFILE%\Documents\iRacing\telemetry mappában

## Hogyan kapcsold be {#how-to-switch-it-on}

Az élő adatokhoz semmit sem kell tenni. Pozíciókhoz: rögzíts telemetriát az autóban (Alt+L), vagy állítsd az app.ini fájlban az irsdkLog=1 értéket

## Hogyan működik {#how-it-works}

iRacing, élőben: az iRacing SDK megosztott memóriája, natívan olvasva.

Az iRacing a telemetriáját az alkalmazásoknak egy elnevezett fájlleképezésben teszi közzé, `Local\IRSDKMemMapFileName` néven, amelyet a szimulátor futás közben hoz létre (és minden frissítésnél jelez a `Local\IRSDKDataValidEvent` eseménnyel, ami itt nincs szükségnek: a watcher másodpercenként tízszer néz rá). Az elrendezés az SDK `irsdk_defines.h` fájlja szerint van, amelyet a pyirsdk (MIT) is követ – ezeknek a tényeknek alapján újraírva:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

A szimulátor a `numBuf` sort körforgásosan írja; a legújabb az, amelyiknek a legnagyobb tickCount értéke, és egy sort újra olvasnak, ha a tickCount a másolás közben megváltozott.

Az élő adatokban nincs világpozíció – a szélesség, hosszúság és magasság csak azokban az `.ibt` fájlokban van, amelyeket az iRacing a `Documents\iRacing\telemetry` mappába ír (Alt+L az autóban, vagy `irsdkLog=1`), és amelyeket a 3DHeat megjelenítő maga olvas. Ezért a rögzítés a vezetést koordináták nélküli eseményekként írja le – sebesség, kör, a kör megtett hányada, versenyhelyezés, incidensek –, valamint köröket, incidenseket, boxkiállásokat és a kockás zászlót, a végén pedig a munkamenetben írt .ibt fájlokat `telemetry_file` eseményekként, hogy a megjelenítő megnyithassa őket.

A sorok mellett az egész memóriatérkép megmarad a munkamenet nyers mellékletében (`heat.raw.parquet`): a fejléc rögzített része (`header`, valahányszor változik), a változófejlécek (`var_headers`, egészben, és JSON-ként a `text` mezőben, valahányszor az elrendezés változik), a munkamenet-információ YAML-ja (`session_info`, a szövege, valahányszor a `sessionInfoUpdate` változik), és a legújabb telemetriasor (`telemetry`, minden változója, minden olvasásnál, amely új ütemet talál). A változófejlécek és egy sor elég ahhoz, hogy egy későbbi dekóder bármely változót olvasni tudjon.

Forrás: az iRacing SDK (irsdk_defines.h, "iRacing SDK" fórumdokumentáció); kutu/pyirsdk (MIT) a címek megerősítésére.

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | nem |
| Felfelé mutató tengely | `y` |
| Mértékegység | élőben nincs pozíció; az .ibt fájlok szélességet/hosszúságot/magasságot hordoznak |
| Tükrözés a megjelenítőnek | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json` fájljának `axes` mezőjébe, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe, így a 3DHeat megjelenítő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos mód {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így jeleníti meg: "engedélyezett (csak azt olvassa, amit a játék közzétesz)".
- Típus `telemetry`: csak azt olvassa, amit a játék vagy a platform kiad (egy UDP-port vagy megosztott memória, amelyet a játék közzétesz), ezért online játék közben is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van jelölve – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Ennek az adapternek a kódja névről név beállított statisztikakulcsai (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

A kapcsos zárójelben lévő kulcsot futásidőben töltik ki (`score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevéből vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertálási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megtartja, soha nem dobja el. A sorokon kívül minden csomagot, lapot, sort vagy választ, amelyet az adapter kap, egészben megtart a munkamenet `heat.raw.parquet` fájljában (oszlopai `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), a `meta.json` `selfCheck.completeness` adatai pedig minden `type`-ot számolnak – a `lost` értéke 0.

**Beolvasva**

- a legújabb telemetriasorból: a munkamenet ideje, száma, állapota és azonosítója, pályán, visszajátszás, kör, a megtett körök száma, a kör hányada és métere, utolsó és legjobb kör, sebesség, fokozat, gáz, fék, fordulatszám, boxutca, pályafelület, versenyhelyezés és osztályhelyezés, a saját incidensszám (a 5 Hz-es `driving` sorok és az események)
- most már a `driving` sorokon is: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (fok, a szimulátor radiánjaiból – csak akkor, ha a változófejléc a mértékegységet rad-ban adja meg), `fuel_l` (l), `lat_accel` és `lon_accel` (m/s^2)
- a munkamenet-információ YAML-jából: a játékos autójának indexe, pálya és konfiguráció, munkamenet-típusok, minden versenyző neve, autója, csapata és száma (session_start sorok, meta.json)
- a tesztekben egy az irsdk_defines.h alapján épített blokkon ellenőrizve; a szimulátoron még nem ellenőrizve

**Nyers formában megtartva**

- `telemetry`: a legújabb sor egészben, minden változója, amelyet a szimulátor közzétesz (minden autó CarIdx tömbjei, gumik, felfüggesztés, a nagy sebességű `_ST` tömbök, ahol a szimulátor ezeket adja ...), minden olvasásnál, amely új ütemet talál; a `tick` a szimulátor ütemszáma; a `used` hamis, amíg visszajátszás fut
- `var_headers`: a változófejlécek egészben (144 bájt mindegyik), és a `text` mezőben JSON-ként (név, típus, eltolás, darabszám, mértékegység, leírás), valahányszor az elrendezés változik – elég minden megtartott sor minden változójának olvasásához
- `session_info`: a YAML-szöveg egészben, valahányszor a frissítési számlálója változik (hétvége, munkamenetek és eredmények, versenyzők, autóbeállítás, rádió, kamera-listák), `update` a számláló
- `header`: a 112 bájtos irsdk-fejléc egészben, valahányszor változik (verzió, állapot, ütemezés, eltolások, a sorok ütemei)

**Nem elérhető**

- élő világpozíció: a megosztott memóriában nincs; a szélesség, hosszúság és magasság csak az .ibt fájlokban van (ha a naplózás be van kapcsolva), amelyeket a megjelenítő olvas – a watcher a munkamenet alatt írottakat nevezi meg
- a két olvasás közötti ütemek: a szimulátor másodpercenként 60 sort ír 3 vagy 4 rekeszbe, a watcher pedig másodpercenként tízszer olvas, így a legtöbb ütemet felülírják, mielőtt olvashatók lennének; a naplózás bekapcsolt állapotában az .ibt fájl minden ütemet tartalmaz

**Méret**: egy telemetriasor néhány KB (kb. 5–10 KB minden autó tömbjével), másodpercenként legfeljebb tízszer megtartva, plusz a fejléc (112 bájt) ugyanígy, és a munkamenet-információ YAML-ja (tíz KB-ok) változásonként: óránként körülbelül 0,2–0,4 GB pályán, tömörítés előtt; a zstd a töredékére hozza (még nem mérték valódi munkamenetben)

## Ellenőrizve {#verified}

egy a tesztben az irsdk-elrendezés alapján épített megosztott memória-blokkon tesztelve; a szimulátoron még nem tesztelve

## Forrás {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
