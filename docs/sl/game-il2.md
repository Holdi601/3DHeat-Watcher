---
title: "IL-2 Sturmovik: Great Battles (živi podatki)"
nav_order: 26
lang: "sl"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (živi podatki) {#il-2-sturmovik-great-battles-live-data}

Medtem ko igrate IL-2 Sturmovik: Great Battles, watcher shrani podatke, ki jih igra sama pošilja, da jih lahko kasneje pogledate kot statistiko in časovnico.

*Tehnične podrobnosti: adapter `il2`, vrsta [`telemetry`](sources-and-rules.md); teče, ko sta `Il-2.exe` ali `IL2Series.exe` zagnana, in išče nove podatke vsakih 0,1 s.*

## Kaj se zapiše {#what-is-recorded}

- izleti (sorties): letalo, ki ga prevzameš (spawn), in kdaj izhod preneha (session_end) - brez svetovnega položaja, ker ga igra ne pošlje
- izpuščene bombe in rakete (masa), zadetki in prejete poškodbe, eksplozije, rafali strelov - položaji lokalni glede na letalo
- ekvivalentna zračna hitrost, AGL, navpična hitrost, g, vrtljaji motorja enkrat na sekundo, z vsakim drugim kazalnikom, ki ga paket nosi (tlak v sesalniku, tresljaji motorja, stanje in tlak podvozja, AoA, zdrs, pospešek x/y/z, tresljaji kabine, zakrilca, zračne zavore)
- izleti, izstreljeni streli, bombe, rakete, prejeti zadetki, najvišja hitrost, najvišji g, čas letenja; naslov strežnika in ime pilota na spletu
- vsak telemetrijski paket cel v heat.raw.parquet

## Od kod prihaja {#where-it-comes-from}

telemetrijski UDP izhod igre na 127.0.0.1:41995 ([KEY = telemetrydevice] v &lt;igra&gt;\data\startup.cfg)

## Kako vklopiti {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (doda addrN = "127.0.0.1:41995", enable = true), nato znova zaženite IL-2

Ukaz vtipkajte v terminalu, odprtem v mapi watcherja (glej [Preden začneš](before-you-start.md)). Če ne uspe, zadnja vrstica pove, zakaj; [Namestitev in zagon](installing-and-running.md) pokriva običajne vzroke.

`python -m heat3d_watch setup il2` našteje datoteke, ki bi se spremenile; `python -m heat3d_watch setup il2 --apply` jih spremeni, original pa ohrani kot `<file>.heat3d-backup` (glej [Ukazi](commands.md#setup)). Izpiše `il2: changed: ...` za vsako spremembo ali `il2: nothing to change`, če je že vklopljeno.

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

Istemu modulu pripada tudi: [IL-2 Sturmovik: Great Battles (posnetki)](game-il2-tacview.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zabeleženi | ne |
| Navpična os | `y` |
| Enote | ni enot: telemetrija nima svetovnih položajev |
| Zrcaljeno za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

To gre v `meta.json` vsake seje (`axes`) in, kadar seja ima položaje, v nogo `heat.parquet`, zato pregledovalnik sam obrne in premeri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `telemetry`: bere samo to, kar igra ali platforma ponudi (vrata UDP ali skupni pomnilnik, ki ga igra objavi), zato zapisuje tudi pri igranju na spletu, ne samo brez njega; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: **nikoli** ga ta adapter ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igranje na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Statistične ključe, ki jih koda tega adapterja nastavi po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele igrinih polj ali iz igrinih lastnih imen statistike, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornika](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali shrani, nikoli se ne zavrže. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani cel v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in vsako polje, shranjeno po imenu; `used` označi, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- SET_FOCUS (prevzeto letalo: izlet), DROP_BOMB in ROCKET_LAUNCH (masa, lokalni položaj), HIT in DAMAGE (lokalni položaj, sila), EXPLOSION (lokalni položaj, polmer), GUN_FIRE (streli na vzorec) kot vrstice
- SETUP_ENG (zaporedna številka, id, lokalni položaj, največji vrtljaji), SETUP_GUN (zaporedna številka, lokalni položaj, masa izstrelka, začetna hitrost) in SETUP_LGEAR (zaporedna številka, id, lokalni položaj) kot vrstice: motorji, topovi in nosilci podvozja letala ob začetku izleta
- SRV_TITLE, SRV_ADDR, SRS_ADDR in CLIENT_DAT (ime pilota) v meta.json; CTRL_DAT-jeva koalicija kot ekipa izleta
- vseh petnajst kazalnikov specifikacije na vrstici `state` enkrat na sekundo (ena vrednost kot število, za vsak motor, nosilec podvozja ali os kot seznam); najvišja hitrost, g in AGL iz vsakega paketa

**Shranjeno surovo**

- vsak datagram cel kot `payload`, pod svojim Packet_ID: `0x54000101` za telemetrijo (uporabljeno, ko je ustvarilo vrstico ali vpis v meta.json), vsak drug id kot sam, datagram, prekratek za enega, kot `short`
- kar hrani samo surovi spremljevalni zapis: kazalniki med vrsticami na sekundo (igra jih pošilja s 50 Hz / decimation), dogodek SETUP, krajši od postavitve specifikacije, id-ji dogodkov, ki jih specifikacija ne našteva

**Ni na voljo**

- svetovni položaj: telemetrijski izhod ga nima (položaji dogodkov so lokalni glede na letalo); adapter il2-tacview bere položaje iz igrinih lastnih Tacview posnetkov
- drugi letalniki in igralci: izhod opiše samo letalo lastnega igralca

**Velikost**: približno 8 MB na uro pri 10 Hz (decimation 5; paket je okoli 160 bajtov plus njegov okvir), 40 MB pri polni igrini 50 Hz, pred zstd; zstd ponavljajoče se floate stisne na delček

## Preverjeno {#verified}

preizkušeno na paketih, sestavljenih po igrini specifikaciji Il2_TeleOutput (rev 1.2); urejanje startup.cfg preizkušeno na kopiji datoteke; še nepreizkušeno z delujočo igro

## Vir {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
