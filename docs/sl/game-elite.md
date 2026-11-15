---
title: "Elite Dangerous (dnevniške datoteke)"
nav_order: 18
lang: "sl"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (dnevniške datoteke) {#elite-dangerous-log-files}

Medtem ko igrate Elite Dangerous, watcher bere datoteke, ki jih igra zapisuje, in shrani, kaj se je zgodilo, da to lahko pozneje pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `elite`, vrsta [`log`](sources-and-rules.md); teče, medtem ko se izvaja `EliteDangerous64.exe`, in novih podatkov išče vsakih 0,25 s.*

## Kaj se zapiše {#what-is-recorded}

- vsak dogodek dnevnika poti pod njegovim imenom dnevnika, z navadnimi polji
- galaktični položaj (StarPos, svetlobna leta) ob skokih, lokacijah, oživitvah, smrtih, priklopih in pristankih
- oživitev ob LoadGame/Resurrect, smrt ob Died, priklop/odklop, dotik tal/vzlet, skok, session_end
- pot po površini planeta iz Status.json: zemljepisna širina, zemljepisna dolžina, višina, smer in metri v tangentni ravnini za vsako telo (seja = ime telesa), z drugimi navadnimi polji iz Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- vsaka vrstica dnevnika poti in vsaka spremljevalna datoteka v celoti v heat.raw.parquet
- skoki, preskočena razdalja, smrti, pobitja, zasluženi krediti, opravljene misije, pregledana telesa, obiskani sistemi, priklopi, pristanki

## Od kod prihajajo {#where-it-comes-from}

Dnevnik igralca %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (najnovejša datoteka, sledi se, medtem ko se piše), Status.json in druge spremljevalne datoteke \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) v isti mapi

## Kako vklopiti {#how-to-switch-it-on}

Ničesar ni treba vklapljati: watcher bere vir tako, kot ga da igra ali platforma.

## Kako deluje {#how-it-works}

Elite Dangerous: dnevnik igralca in Status.json, ki jih igra zapisuje med delovanjem.

Kje: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - en objekt JSON na vrstico, ena datoteka na vsak zagon (dolga seja se nadaljuje v delu .02, .03 ...). Vsaka vrstica ima `timestamp` (UTC, ISO 8601) in `event`. Galaktični položaji so `StarPos` [x, y, z] sistema, v svetlobnih letih od Sonca, pri `FSDJump`, `Location` in `CarrierJump`. Galaktični okvir Elite ima y navzgor (proti galaktičnemu severu), z proti galaktičnemu jedru in x proti galaktični dolžini 270 - levosučni okvir, zato pregledovalnik z zrcali z, da ga nariše prav.
* `Status.json` - vsakič znova zapisan v celoti, ko se stanje ladje spremeni: `Flags`, in blizu planeta `Latitude`, `Longitude` (stopinje), `Altitude` (metri), `Heading`, `BodyName` in `PlanetRadius` (metri).
* Druge spremljevalne datoteke, vsaka zapisana v celoti, ko igra zapiše ustrezen dogodek dnevnika: `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`. Vsaka datoteka `*.json` v mapi, ki jo igra v tej seji zapiše, se ob vsaki spremembi shrani v celoti pod svojim imenom (pravilo pretvornikov 3DHeat: kar vir vsebuje, se prebere ali ohrani).

Vsaka vrstica dnevnika se v surovem spremljevalnem zapisu seje ohrani v celoti pod svojim `event`, vsaka spremljevalna datoteka pod svojim imenom; vrstica, ki ni JSON, pa pod `unparsed`.

Položaji na površini se postavijo v lokalno tangentno ravnino za vsako telo, v metrih: prva točka na telesu je njegovo izhodišče, x vzhodno, z severno, y navzgor (višina), enako usmerjenost kot galaktični okvir; vrstice nosijo ime telesa kot svoj `session`, tako da se vožnja ali hoja po planetu nariše kot lastna pot. Vrstice galaksije imajo sejo "galaxy". Obe merili sta v eni tabeli; sejo izberete v pregledovalniku.

Oblika: priročnik Frontierjevega "Elite Dangerous Player Journal" (objavljen ob vsaki posodobitvi na uradnem forumu, <https://forums.frontier.co.uk/> - "Journal Manual", v4.x), dogodki in polja, kot so tam opisani; zastavice Status.json po poglavju "Status File" istega priročnika.

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Zabeleženi položaji | da |
| Os navzgor | `y` |
| Enote | svetlobna leta (vrstice galaksije, seja 'galaxy'); metri vzhodno/navzgor/severno od prve točke na telesu (vrstice površine, seja = ime telesa) |
| Za pregledovalnik zrcaljeno | `z` |
| Merilo enot (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

To se zapiše v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, zato pregledovalnik 3DHeat vrstice sam obrne in skalira - glejte [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igrano na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `log`: bere samo, kar igra ali platforma izda (datoteke, ki jih igra zapisuje med delovanjem), zato beleži tudi v spletni igri, ne samo brez povezave; zastavica odloča samo, ali sme pomnilnik sploh kdaj brati.
- Pomnilnik: tega adapterja **nikoli** ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igrano na spletu - glejte [Viri in pravila](sources-and-rules.md).

## Zabeležene statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavi po imenu (`stats` vsake seje v `meta.json` in tabela `stats` v `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz imen statistik igre, na tem seznamu niso; "Kaj se zapiše" zgoraj jih našteje.

## Popolnost {#completeness}

Watcher upošteva [pravilo pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali ohrani, nikoli ne izpusti. Poleg vrstic vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, ostane v celoti v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text`, nato vsako polje, ohranjeno po imenu; `used` označuje, kar je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- vsaka vrstica dnevnika kot vrstica pod svojim `event`, z navadnimi polji (lokalizirano besedilo, kjer ga igra da; besedila, daljša od 300 znakov, so v vrstici skrajšana)
- vrstice galaksije (StarPos) ob FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; vrstice površine iz Status.json in Touchdown/Liftoff
- navadna polja Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) pri vrsticah površine
- statistike: skoki, razdalja, smrti, pobitja, zasluženi krediti, misije, pregledana telesa, obiskani sistemi, priklopi, pristanki

**Ohranjeno surovo**

- vsaka vrstica dnevnika v celoti, `type` = njen `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` true: seznami in predmeti, ki jih vrstice izpustijo (StarPos, Factions, Rewards, Killers, Materials, Modules, ...), so samo tukaj
- vrstica dnevnika, ki ni JSON, `type` `unparsed`
- vsaka spremljevalna datoteka v celoti ob vsakem njenem ponovnem zapisu, `type` = njeno ime: `Status.json` (`used`, ko je ustvarila vrstico površine), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json` in vsaka druga `*.json`, ki jo igra tam zapiše

**Ni na voljo**

- položaj med skoki (znotraj sistema, v supercruise ali v normalnem prostoru): igra zapiše samo StarPos sistema in, blizu planeta, zemljepisno širino, dolžino in višino
- položaji drugih ladij in igralcev: dnevnik je lastni zapis poveljnika
- hitrost, plin in druga telemetrija letenja: igra tega ne zapiše
- dnevniki in spremljevalne datoteke prejšnjih sej: ohranjene, ko so bile igrane (sledilnik začne na koncu datoteke, starejše od tega zagona igre)
- Frontierjev spletni vmesnik cAPI spremljevalcev: potrebuje prijavo igralca pri Frontierju; ni datoteka, ki bi jo igra zapisala

**Velikost**: približno 1-5 MB surovega besedila na uro: dnevnik 0,2-2 MB, Status.json (pod 1 KB, prepisan do vsake sekunde) 1-2 MB, komplet market/outfitting/shipyard 20-150 KB na obiskano postajo; zstd v heat.raw.parquet ga zmanjša približno na desetino

## Preverjeno {#verified}

razčlenjevalnik je ponovljen nad pravimi datotekami dnevnika iz lokalne namestitve (številke dogodkov se ujemajo s statistikami); popravki površine iz Status.json so preizkušeni samo na izmišljenih posnetkih

## Vir {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
