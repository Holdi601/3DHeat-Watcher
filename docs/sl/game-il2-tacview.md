---
title: "IL-2 Sturmovik: Great Battles (posnetki)"
nav_order: 27
lang: "sl"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (posnetki) {#il-2-sturmovik-great-battles-replays}

Po tekmi IL-2 Sturmovik: Great Battles watcher spremeni posnetek, ki ga je shranila igra, v datoteke, ki jih lahko pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `il2-tacview`, vrsta [`replay`](sources-and-rules.md); teče ves čas (ne čaka, da se igra zažene) in išče nove podatke vsakih 5 s.*

## Kaj se zapiše {#what-is-recorded}

- vsako letalo, vozilo in ladjo v posnetku: položaji enkrat na sekundo (metri vzhodno/gor/severno od referenčne točke posnetka; lat/lon/alt kot stolpci)
- pojavitve, uničenja (death) in odhodi (left), vzleti in pristanki, kadar so posneti
- objekti, uničeni, vzleti, pristanki in dolžina na posnetek
- vsaka vrstica posnetka cela v heat.raw.parquet, na uri vrstic

## Od kod prihaja {#where-it-comes-from}

igrini lastni Tacview posnetki &lt;igra&gt;\data\Tracks\\\*.acmi (ACMI 2.x besedilo, navadno ali zipano)

## Kako vklopiti {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 v [KEY = track_record])

Ukaz vtipkajte v terminalu, odprtem v mapi watcherja (glej [Preden začneš](before-you-start.md)). Če ne uspe, zadnja vrstica pove, zakaj; [Namestitev in zagon](installing-and-running.md) pokriva običajne vzroke.

`python -m heat3d_watch setup il2-tacview` našteje datoteke, ki bi se spremenile; `python -m heat3d_watch setup il2-tacview --apply` jih spremeni, original pa ohrani kot `<file>.heat3d-backup` (glej [Ukazi](commands.md#setup)). Izpiše `il2-tacview: changed: ...` za vsako spremembo ali `il2-tacview: nothing to change`, če je že vklopljeno.

## Kako deluje {#how-it-works}

IL-2 Sturmovik: Great Battles - telemetrijski UDP izhod igre in njeni lastni Tacview posnetki.

1. Telemetrija ("Telemetry output of IL2 v4.003", revizija 1.2, priložena kot `<igra>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Vklopljena v `<igra>\data\startup.cfg`, razdelek `[KEY = telemetrydevice]`: `addr`, `addr1`, ... = "IP[:port]" (več ciljev hkrati), `decimation` (50 Hz / n), `enable`, `port`. `setup` doda en cilj, 127.0.0.1:41995 (JoyPro uporablja 41994, privzeta vrata igre so 4322), in vklopi izhod. Paketi, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Kazalniki: 0 ENG_RPM, 1 ENG_MP, 2/3 engine shake, 4 LGEARS_STATE, 5 LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz z gravitacijo), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14 VERTICAL_SPEED (m/s). Dogodki (2-bajtno pakirani): 0 SET_FOCUS (STRING: dolžinski bajt + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float pos[3]}, 4 DROP_BOMB in 5 ROCKET_LAUNCH {float pos[3], float mass, WORD flags}, 6 HIT in 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. Položaji dogodkov so lokalni glede na letalo igralca; tok nima nikakršnega svetovnega položaja - zato so to dogodki in števila, ne pot.

2. Tacview posnetek: `tacviewrecord = 1` v `[KEY = track_record]` naredi, da igra zapiše `<igra>\data\Tracks\*.acmi` (v več igralcih odloči strežnik). Končan posnetek se pretvori: vsako letalo, vozilo in ladja s svojimi položaji, pojavitvijo in odstranitvijo (uničen ali odšel), vzleti in pristanki, kadar jih posnetek ima. ACMI 2.x besedilo, navadno ali zipano, po <https://www.tacview.net/documentation/acmi/en/> - vrstice "#t" premaknejo uro, vrstice "id,Key=Value,..." nastavijo lastnosti (šestnajstiški id-ji, vejice pobegnjene kot "\\,", zadnji "\\" nadaljuje vrstico), "-id" odstrani objekt, objekt 0 nosi globalne vrednosti (ReferenceLongitude/Latitude, RecordingTime, ...) in dogodke ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] ali Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], zemljepisna dolžina in širina glede na referenco, prazna polja ostanejo nespremenjena. Položaji gredo v ravni zemljevid okoli referenčne točke: x vzhod, y višina, z sever, metri. Referenčna točka je `geo` seje, shranjena v meta.json in nogi tabele, zato lahko pregledovalnik pravi svet postavi pod proge.

Istemu modulu pripada tudi: [IL-2 Sturmovik: Great Battles (živi podatki)](game-il2.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zabeleženi | da |
| Navpična os | `y` |
| Enote | metri (vzhod, višina, sever od prvega zajema) |
| Zrcaljeno za pregledovalnik | `z` |
| Merilo enote (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

To gre v `meta.json` vsake seje (`axes`) in, kadar seja ima položaje, v nogo `heat.parquet`, zato pregledovalnik sam obrne in premeri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `replay`: bere samo to, kar igra ali platforma ponudi (ponovitve in demo posnetki, ki jih igra shrani), zato zapisuje tudi pri igranju na spletu, ne samo brez njega; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: **nikoli** ga ta adapter ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igranje na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Statistične ključe, ki jih koda tega adapterja nastavi po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele igrinih polj ali iz igrinih lastnih imen statistike, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornika](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali shrani, nikoli se ne zavrže. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani cel v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in vsako polje, shranjeno po imenu; `used` označi, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- vsak T objekta (zemljepisna dolžina, širina, višina, zvitje, nagib, zasuk, U, V, kurz) kot položaj enkrat na sekundo na objekt, z Name, Type, Pilot, Coalition/Color, Country, Group in Parent
- pojavitve, odstranitve (smrt, če je prej prišel dogodek Destroyed, sicer odhod), dogodki TakenOff in Landed, dogodki Message in Bookmark kot vrstice
- globalne vrednosti ReferenceLongitude/Latitude (izhodišče karte), RecordingTime/ReferenceTime (kdaj), DataSource, DataRecorder in Title v meta.json

**Shranjeno surovo**

- vsaka neprazna logična vrstica cela kot `text` (vrstica, nadaljevana z zadnjim "\", je združena, kot jo bere ACMI), pod svojo vrsto: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` in `event` (objekt 0), `object` (id,Key=Value,...)
- kar hrani samo surovi spremljevalni zapis: položaji med vrsticami na sekundo, orožje, izstrelki, bakle, plevel in drugi objekti, ki niso narisani kot poti, vsaka druga lastnost (telemetrija, kot IAS, AOA, plin, gorivo, kjer jo posnetek ima), drugi globali (Comments, Briefing, Author, Category), dogodki, razen prebranih (Timeout, LeftArea ...)

**Ni na voljo**

- nič, kar posnetek ne vsebuje; česar igra ne zapiše v svoje posnetke, ni v njih

**Velikost**: približno besedilo samega posnetka plus nekaj 70 bajtov na vrstico, pred zstd: 100 MB posnetek naredi približno 150-250 MB surovih podatkov, ki jih zstd stisne skoraj na velikost zipanega posnetka

## Preverjeno {#verified}

preizkušeno na sintetičnih datotekah ACMI 2.2 (besedilo in zip); še nepreizkušeno na posnetku iz igre

## Vir {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
