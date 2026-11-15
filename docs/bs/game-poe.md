---
title: "Path of Exile (log datoteke)"
nav_order: 36
lang: "bs"
source: game-poe.md
source_hash: "9facfd5a1551"
nav_exclude: true
search_exclude: true
---
# Path of Exile (log datoteke) {#path-of-exile-log-files}

Dok igrate Path of Exile, watcher čita datoteke koje igra piše i sprema šta se desilo, da to kasnije možete pogledati kao statistiku i vremensku liniju.

*Tehnički detalji: adapter `poe`, vrsta [`log`](sources-and-rules.md); radi dok je pokrenut `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` ili `PathOfExile_x64_KG.exe` i svakih 0,5 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- zone u koje se ulazi s nivoom područja, id-om područja i njegovim seedom
- podizanja nivoa s klasom i nivoom
- smrti ("has been slain")
- igrači koji ulaze u područje i izlaze iz njega, šapati primljeni i poslani, zahtjevi za trgovinu, prihvaćene trgovine
- svaka linija Client.txt iz ove sjednice cijela u heat.raw.parquet
- smrti, dobijeni nivoi, najviši nivo, zone u koje se ušlo, različite zone, šapati, zahtjevi za trgovinu, trgovine

## Odakle dolazi {#where-it-comes-from}

&lt;install>\logs\Client.txt igre Path of Exile ili Path of Exile 2 (prati se; instalacijski folder je folder pokrenute izvršne datoteke)

## Kako ga uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Path of Exile i Path of Exile 2: log klijenta, `<install>\logs\Client.txt`.

Obje igre dopisuju u jedan Client.txt u svom instalacijskom folderu sve dok
su instalirane (raste kroz pokretanja). Linije izgledaju ovako

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- lokalno vrijeme, brojač milisekundi, hash, nivo i nit, pa ono što prozor
  chata prikazuje. Poruke su one engleskog klijenta; klijent drugog jezika
  piše ih prevedene i ovdje se ne razumije. Ništa ne daje
  položaj. Format Grinding Gear Games nije dokumentirao; to je
  obični tekstualni log igre, kako ga alati zajednice (pomoćnici za trgovinu, vodiči za nivoe) čitaju
  godinama - npr. <https://github.com/klayveR/poe-log-monitor> (MIT) za
  popis događaja.

Instalacijski folder je folder pokrenute izvršne datoteke; bez nje se traže
Steam biblioteke i zadani folder samostalnog klijenta.

Svaka linija ove sjednice čuva se cijela u sirovom sidecaru sesije (3DHeat-ovo
pravilo konvertera), znači li ovdje nešto ili ne: `type` je nivo i
logger u njegovim zagradama (`INFO Client`, `DEBUG Client`, `WARN Client`, ...), linija
s vremenskom oznakom bez zagrada je `untagged`, linija bez vremenske oznake
`untimed`.

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | ne |
| Osa gore | `y` |
| Jedinice | položaji se ne bilježe |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `log`: čita samo ono što igra ili platforma daje (datoteke koje igra piše dok radi), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- `You have entered <zone>`, s nivoom područja, id-om područja i seedom iz linije `Generating level` prije nje
- `<name> (<class>) is now level <n>`, `<name> has been slain`, igrači koji ulaze u područje i izlaze iz njega, šapati primljeni i poslani (s tim jesu li zahtjev za trgovinu), prihvaćene i otkazane trgovine

**Čuva se sirovo**

- svaka linija ove sjednice cijela, `type` = nivo i logger u njegovim zagradama (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` gdje je postala red: globalni, trade, party i guild chat, `Connecting to instance server`, AFK i DND obavijesti, odgovori na chat komande poput `/played` i `/deaths`, klijentove linije učitavanja i engine-a - čuvaju se, još ne pretvaraju u redove
- linija s vremenskom oznakom bez zagrada (`***** LOG FILE OPENING *****`) kao `untagged`, linija bez vremenske oznake kao `untimed`

**Nije dostupno**

- položaji: ništa u logu ne daje položaj
- ono što piše klijent drugog jezika: linije se čuvaju, ali se samo engleske poruke pretvaraju u redove
- linije ranijih pokretanja: Client.txt raste kroz pokretanja; linije s vremenskom oznakom prije ovog pokretanja igre se preskaču (čuvane su kad su odigrane)
- ubistva, šteta, plijen i stablo vještina: igra ih ne bilježi

**Veličina**: Client.txt raste oko 0,3-3 MB na sat (najviše od DEBUG linija pri učitavanju područja, više uz prometan trade chat); zstd u heat.raw.parquet to smanjuje otprilike na desetinu

## Provjereno {#verified}

testirano na sintetičkim linijama Client.txt u formatu igre; nije testirano na igri

## Izvor {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
