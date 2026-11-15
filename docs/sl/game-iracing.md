---
title: "iRacing (živi podatki)"
nav_order: 28
lang: "sl"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (živi podatki) {#iracing-live-data}

Medtem ko igrate iRacing, watcher shrani podatke, ki jih igra sama pošilja, da jih lahko kasneje pogledate kot statistiko in časovnico.

*Tehnične podrobnosti: adapter `iracing`, vrsta [`telemetry`](sources-and-rules.md); teče, ko sta `iRacingSim64DX11.exe` ali `iRacingSim64.exe` zagnana, in išče nove podatke vsakih 0,1 s.*

## Kaj se zapiše {#what-is-recorded}

- vožnja 5-krat na sekundo brez položaja (iRacing ga v živo ne da): hitrost, prestava, plin, zavora, krog, delež kroga, položaj na dirki in v razredu, incidenti
- začetek seje, vstop in izstop iz avtomobila, vhod in izhod iz boksov, krogi s časom kroga, incidenti s točkami, karirana zastava, cilj
- datoteke telemetrije .ibt, zapisane med sedenjem (zemljepisna širina, dolžina, višina - pregledovalnik jih bere)
- krogi, najboljši krog, incidenti, položaj na dirki, postanki v boksih, razdalja, najvišja hitrost
- celotni skupni pomnilnik v `heat.raw.parquet`: glava, glave spremenljivk, podatki o seji, vsaka prebrana telemetrijska vrstica

## Od kod prihaja {#where-it-comes-from}

skupni pomnilnik Local\IRSDKMemMapFileName (iRacing SDK); datoteke .ibt v %USERPROFILE%\Documents\iRacing\telemetry

## Kako vklopiti {#how-to-switch-it-on}

Za žive podatke ničesar. Za položaje: snemajte telemetrijo v avtu (Alt+L) ali nastavite irsdkLog=1 v app.ini

## Kako deluje {#how-it-works}

iRacing, živo: iRacing SDK-jev skupni pomnilnik, bran nativno.

iRacing objavi svojo telemetrijo za aplikacije v poimenovani preslikavi datoteke, `Local\IRSDKMemMapFileName`, ki jo simulator ustvari med delovanjem (in ob vsaki posodobitvi signalizira `Local\IRSDKDataValidEvent`, kar tu ni potrebno: watcher bere desetkrat na sekundo). Postavitev je iz SDK-jeve `irsdk_defines.h`, prav tako jo uporablja pyirsdk (MIT) - tu je napisana znova iz teh dejstev:

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

Simulator piše `numBuf` vrstic krožno; najnovejša je tista z najvišjim tickCount, vrstica pa se vzame znova, če se je njen tickCount premaknil med kopiranjem.

Živi podatki nimajo svetovnega položaja - zemljepisna širina, dolžina in višina so samo v datotekah `.ibt`, ki jih iRacing beleži v `Documents\iRacing\telemetry` (Alt+L v avtu ali `irsdkLog=1`), in jih pregledovalnik bere sam. Zato to zapiše vožnjo kot dogodke brez koordinat - hitrost, krog, delež prevožene krožne poti, položaj na dirki, incidente - ter krogi, incidenti, postanki v boksih in karirana zastava, na koncu pa datoteke `.ibt`, zapisane med sedenjem, kot dogodke `telemetry_file`, da jih pregledovalnik lahko odpre.

Poleg vrstic se celotna preslikava pomnilnika shrani v surovem spremljevalnem zapisu seje (`heat.raw.parquet`): trajni del glave (`header`, vsakič, ko se spremeni), glave spremenljivk (`var_headers`, cele, in v `text` kot JSON, vsakič, ko se postavitev spremeni), YAML podatkov o seji (`session_info`, njegovo besedilo, vsakič, ko se `sessionInfoUpdate` premakne) in najnovejša telemetrijska vrstica (`telemetry`, vsaka spremenljivka v njej, ob vsakem branju, ki najde nov takt). Glave spremenljivk in ena vrstica sta vse, kar kasnejši dekoder potrebuje, da prebere katerokoli spremenljivko.

Vir: iRacing SDK (irsdk_defines.h, dokumentacija "iRacing SDK" na forumu); kutu/pyirsdk (MIT) za potrditev zamikov.

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zabeleženi | ne |
| Navpična os | `y` |
| Enote | ni položajev v živo; datoteke .ibt nosijo zemljepisno širino, dolžino in višino |
| Zrcaljeno za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

To gre v `meta.json` vsake seje (`axes`) in, kadar seja ima položaje, v nogo `heat.parquet`, zato pregledovalnik sam obrne in premeri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `telemetry`: bere samo to, kar igra ali platforma ponudi (vrata UDP ali skupni pomnilnik, ki ga igra objavi), zato zapisuje tudi pri igranju na spletu, ne samo brez njega; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: **nikoli** ga ta adapter ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igranje na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Statistične ključe, ki jih koda tega adapterja nastavi po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele igrinih polj ali iz igrinih lastnih imen statistike, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornika](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali shrani, nikoli se ne zavrže. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani cel v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in vsako polje, shranjeno po imenu; `used` označi, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- iz najnovejše telemetrijske vrstice: čas seje, številka, stanje in id, na progi, replay, krog, končani krogi, delež in metri kroga, zadnji in najboljši krog, hitrost, prestava, plin, zavora, vrtljaji, pit road, podlaga proge, položaj na dirki in v razredu, lastno število incidentov (vrstice `driving` pri 5 Hz in dogodki)
- zdaj tudi na vrsticah `driving`: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (stopinje, iz simulatorjevih radianov - samo kadar glava spremenljivke navaja enoto rad), `fuel_l` (enota l), `lat_accel` in `lon_accel` (enota m/s^2)
- iz YAML podatkov o seji: indeks igralčevega avtomobila, proga in konfiguracija, vrste seje, ime vsakega voznika, avto, ekipa in številka (vrstice session_start, meta.json)
- preverjeno z blokom, sestavljenim iz irsdk_defines.h v testih; še ne s simulatorjem

**Shranjeno surovo**

- `telemetry`: najnovejša vrstica cela, vsaka spremenljivka, ki jo simulator objavi (polja CarIdx za vsak avto, pnevmatike, vzmetenje, polja `_ST` z visoko hitrostjo, kjer jih simulator ima ...), ob vsakem branju, ki najde nov takt; `tick` je števec taktov simulatorja; `used` je napačno, medtem ko se predvaja replay
- `var_headers`: glave spremenljivk cele (144 bajtov vsaka) in v `text` kot JSON (ime, tip, zamik, število, enota, opis), vsakič, ko se postavitev spremeni - dovolj, da se prebere vsaka spremenljivka v vsaki shranjeni vrstici
- `session_info`: YAML besedilo v celoti vsakič, ko se njegov števec posodobitev premakne (vikend, seje in rezultati, vozniki, nastavitev avta, radio, seznami kamer), `update` je števec
- `header`: 112-bajtna glava irsdk cela vsakič, ko se spremeni (različica, stanje, hitrost taktov, zamiki, takti vrstic)

**Ni na voljo**

- položaj v živo: skupni pomnilnik ga nima; zemljepisna širina, dolžina in višina so samo v datotekah .ibt (ob vklopljenem snemanju), ki jih pregledovalnik bere - watcher imenuje tiste, zapisane med sedenjem
- takti med dvema branjema: simulator piše 60 vrstic na sekundo v 3 ali 4 reže, watcher pa bere desetkrat na sekundo, zato je večina taktov prepisanih, preden jih je mogoče prebrati; datoteka .ibt ima vsak takt, kadar je snemanje vklopljeno

**Velikost**: približno 0,2 do 0,4 GB na uro na progi pred stiskanjem: telemetrijska vrstica je nekaj KB (okoli 5 do 10 KB z vsemi polji avtomobilov), zapisana do desetkrat na sekundo, plus glava (112 bajtov) prav tako pogosto in YAML podatkov o seji (deset KB) ob spremembi; zstd jo stisne na delček (še ni izmerjeno na pravi seji)

## Preverjeno {#verified}

preizkušeno na bloku pomnilnika, sestavljenem v testu po postavitvi irsdk; še nepreizkušeno s simulatorjem

## Vir {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
