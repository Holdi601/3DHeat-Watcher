---
title: "EVE Online (log datoteke)"
nav_order: 20
lang: "bs"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (log datoteke) {#eve-online-log-files}

Dok igrate EVE Online, watcher čita datoteke koje igra piše i sprema šta se desilo, da to kasnije možete pogledati kao statistiku i vremensku liniju.

*Tehnički detalji: adapter `eve`, vrsta [`log`](sources-and-rules.md); radi dok je pokrenut `exefile.exe` i svakih 0,5 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- zadana i primljena šteta, s drugim brodom, pilotom, tickerom korporacije, oružjem i kvalitetom pogotka
- promašaji zadani i primljeni
- isplaćene nagrade (ubistva NPC-ova) s ISK
- skokovi između sistema
- svaka linija gamelog-a i chat loga cijela u heat.raw.parquet
- zadana i primljena šteta, pogoci, promašaji, ubistva s nagradom i ISK, skokovi

## Odakle dolazi {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt i Chatlogs\\\*.txt pored njih (svaka datoteka napisana otkako je klijent pokrenut)

## Kako ga uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

EVE Online: logovi igre klijenta, `Documents\EVE\logs\Gamelogs\*.txt`.

Klijent piše jednu datoteku po liku po prijavi,
`<yyyymmdd>_<hhmmss>[_<character id>].txt`; zapisivanje u datoteku je po zadanim postavkama uključeno. Više klijenata koji rade
uporedo piše svaki svoju, pa se prati svaka datoteka napisana otkako je igra
pokrenuta. Zaglavlje i linije (EVE vrijeme je UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(linija combat je u datoteci jedna linija). Oznake formatiranja se uklanjaju prije
poklapanja. Datoteka je tokom godina bila UTF-8 i UTF-16; čitaju se oba.
Format CCP nije dokumentirao; to je klijentov obični tekstualni log, koji se čita kao
što ga čitaju alati zajednice za combat log (npr. <https://docs.rs/crate/eve-log-parser>).
Nema položaja.

Pored njega, `Documents\EVE\logs\Chatlogs\<channel>_<yyyymmdd>_<hhmmss>[_<id>].txt`:
jedna datoteka po chat kanalu po prijavi (kad je chat logging uključen, što je
klijentova zadana postavka), UTF-16, zaglavlje s imenom kanala i slušaoca, zatim
`[ yyyy.mm.dd hh:mm:ss ] Sender > message`.

Svaka linija oba logova čuva se cijela u sirovom sidecaru sesije (3DHeat-ovo
pravilo konvertera): linija gamelog-a pod svojim kanalom u zagradama (`combat`,
`notify`, `bounty`, `None`, ...), chat linija kao `chat` s njenim kanalom, a
linije zaglavlja kao `gamelog header` / `chatlog header`.

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

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- pogoci `(combat)` iz gamelog-a zadani i primljeni (iznos, drugi pilot, ticker korporacije, brod, oružje, kvalitet pogotka) i promašaji u oba smjera
- isplate `(bounty)` iz gamelog-a s ISK, i linije `Jumping from A to B`
- Listener u zaglavlju gamelog-a: čiji je to log

**Čuva se sirovo**

- svaka linija gamelog-a cijela, `type` = njen kanal u zagradama (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), s `file` i `listener`; `used` gdje je postala red; linije zaglavlja kao `gamelog header`
- svaka linija chat loga cijela (Local, korporacija, flota, privatni kanali, obavijesti `EVE System` poput promjene Local kanala pri skoku), `type` `chat`, s `channel`, `listener` i `file`; linije zaglavlja kao `chatlog header`. Još se ne pretvaraju u redove
- oznake formatiranja (`<color>`, `<b>`, `<font>`) ostaju u sirovom tekstu; u redovima su uklonjene

**Nije dostupno**

- položaji: klijent ih ne piše u svoje logove
- borbe drugih pilota: gamelog je slušaočev vlastiti
- logovi ranijih prijava: svaka prijava piše nove datoteke; one starije od ovog pokretanja klijenta ne čitaju se ponovo
- chat kad je igrač isključio chat logging u postavkama klijenta
- klijentove vlastite cache datoteke i datoteke postavki: nisu logovi i nisu dokumentirane

**Veličina**: gamelog je 0,1-2 MB na sat (najviše u borbi); chat logovi zavise od otvorenih kanala - prometan Local ili kanal flote 0,5-3 MB na sat; zstd u heat.raw.parquet to smanjuje otprilike na desetinu

## Provjereno {#verified}

testirano na sintetičkim linijama gamelog-a u formatu koji objavljuju parseri zajednice; nije testirano na igri

## Izvor {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
