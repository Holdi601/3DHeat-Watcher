---
title: "Path of Exile (datoteke dnevnika)"
nav_order: 36
lang: "hr"
source: game-poe.md
source_hash: "9facfd5a1551"
nav_exclude: true
search_exclude: true
---
# Path of Exile (datoteke dnevnika) {#path-of-exile-log-files}

Dok igrate Path of Exile, watcher čita datoteke koje igra piše i sprema što se dogodilo, pa to kasnije možete pogledati kao statistiku i vremensku crtu.

*Tehnički detalji: adapter `poe`, vrsta [`log`](sources-and-rules.md); radi dok je pokrenut `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` ili `PathOfExile_x64_KG.exe` i traži nove podatke svakih 0,5 s.*

## Što se bilježi {#what-is-recorded}

- zone u koje se uđe, s razinom područja, ID-jem područja i njegovim sjemenom
- podizanja razine s klasom i razinom
- smrti („has been slain“)
- igrači koji ulaze i izlaze iz područja, šaptanja primljena i poslana, zahtjevi za trgovinu, prihvaćene trgovine
- svaki redak Client.txt-a ovog sjedenja cijel u heat.raw.parquet
- smrti, dobivene razine, najviša razina, ušle zone, različite zone, šaptanja, zahtjevi za trgovinu, trgovine

## Odakle dolazi {#where-it-comes-from}

&lt;install>\logs\Client.txt Path of Exile ili Path of Exile 2 (prati se; mapa instalacije je mapa pokrenute izvršne datoteke)

## Kako to uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Path of Exile i Path of Exile 2: dnevnik klijenta, `<install>\logs\Client.txt`.

Obje igre dopisuju u jedan Client.txt u svojoj mapi instalacije, dok god su instalirane (raste kroz pokretanja). Redci izgledaju ovako:

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- lokalno vrijeme, brojač u milisekundama, hash, razina i dretva, pa ono što prikazuje prozor za chat. Poruke su s engleskog klijenta; klijent na drugom jeziku ih piše prevedene, a ovdje se ne razumiju. Ništa ne daje poziciju. Format nije dokumentirao Grinding Gear Games; to je običan tekstualni dnevnik igre, kao što ga godinama čitaju zajednički alati (alati za trgovinu, vodiči za razine) - npr. <https://github.com/klayveR/poe-log-monitor> (MIT) za popis događaja.

Mapa instalacije je mapa pokrenute izvršne datoteke; bez nje se pretražuju Steam biblioteke i zadana mapa samostalnog klijenta.

Svaki redak ovog sjedenja čuva se cijel u sirovom pratećem dijelu sesije (pravilo pretvarača 3DHeat), bez obzira ima li za ovaj prikaz značenje: `type` je razina i logger u njegovim zagradama (`INFO Client`, `DEBUG Client`, `WARN Client`, ...), redak s vremenom bez zagrada je `untagged`, a redak bez vremena `untimed`.

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Bilježe se pozicije | nema |
| Os prema gore | `y` |
| Jedinice | nema pozicija |
| Zrcaljeno za preglednik | nema |
| Mjerilo jedinice (`scale`: preglednik ovim množi pozicije) | 1 |

Ovo ide u `meta.json` (`axes`) svake sesije i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `log`: čita samo ono što igra ili platforma daje (datoteke koje igra piše dok radi), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: adapter je **nikad** ne čita. Memoriju čitaju samo adapteri vrste `memory`, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` u `meta.json` svake sesije i tablica `stats` u `watcher.sqlite`):

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz imena statistike same igre nisu na ovom popisu; odjeljak „Što se bilježi“ ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeata: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json`-u broji svaki `type` - `lost` je 0.

**Čita se**

- `You have entered <zone>`, s razinom područja, ID-jem područja i sjemenom iz retka `Generating level` prije njega
- `<name> (<class>) is now level <n>`, `<name> has been slain`, igrači koji ulaze i izlaze iz područja, šaptanja primljena i poslana (s time je li riječ o zahtjevu za trgovinu), prihvaćene i otkazane trgovine

**Čuva se sirovo**

- svaki redak ovog sjedenja cijel, `type` = razina i logger u njegovim zagradama (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` gdje je postao retkom: globalni, trgovinski, party i guild chat, `Connecting to instance server`, obavijesti AFK i DND, odgovori na naredbe za chat kao `/played` i `/deaths`, redci učitavanja i motora klijenta - čuvaju se, još nisu pretvoreni u retke
- redak s vremenom bez zagrada (`***** LOG FILE OPENING *****`) kao `untagged`, a redak bez vremena kao `untimed`

**Nije dostupno**

- pozicije: ništa u dnevniku ih ne daje
- što piše klijent na drugom jeziku: redci se čuvaju, ali se u retke pretvaraju samo engleske poruke
- redci ranijih pokretanja: Client.txt raste kroz pokretanja; redci s vremenom prije ovog pokretanja igre ostaju (sačuvani su kad su odigrani)
- ubojstva, šteta, plijen i stablo talenata: igra ih ne bilježi

**Veličina**: Client.txt raste oko 0,3-3 MB po satu (najviše od DEBUG redaka pri učitavanju područja, više uz zauzet trgovinski chat); zstd u heat.raw.parquet ga smanjuje na otprilike desetinu

## Provjereno {#verified}

testirano na sintetičkim redcima Client.txt-a u formatu igre; neprovjereno u samoj igri

## Izvor {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
