---
title: "EVE Online (datoteke dnevnika)"
nav_order: 20
lang: "hr"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (datoteke dnevnika) {#eve-online-log-files}

Dok igrate EVE Online, watcher čita datoteke koje igra piše i sprema što se dogodilo, pa to kasnije možete pogledati kao statistiku i vremensku crtu.

*Tehnički detalji: adapter `eve`, vrsta [`log`](sources-and-rules.md); radi dok je `exefile.exe` pokrenut i traži nove podatke svakih 0,5 s.*

## Što se bilježi {#what-is-recorded}

- nanesena i primljena šteta od drugog broda, pilota, oznake korporacije, oružja i kvalitete pogotka
- promašaji naneseni i primljeni
- isplaćene nagrade (ubojstva NPC-ova) s ISK-om
- skokovi između sustava
- svaki redak gamelog-a i chat dnevnika cijel u heat.raw.parquet
- nanesena i primljena šteta, pogoci, ubojstva za nagrade i ISK, skokovi

## Odakle dolazi {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt i Chatlogs\\\*.txt pored njih (svaka datoteka napisana otkako je klijent pokrenut)

## Kako to uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

EVE Online: tekstualni dnevnici klijenta igre, `Documents\EVE\logs\Gamelogs\*.txt`.

Klijent piše jednu datoteku po liku po prijavi, `<yyyymmdd>_<hhmmss>[_<character id>].txt`; zapisivanje u datoteku uključeno je prema zadanim postavkama. Ako radi više klijenata istovremeno, svaki piše svoju datoteku, pa se prati svaka datoteka napisana otkako je igra pokrenuta. Zaglavlje i redci (vrijeme u EVE-u je UTC):

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

(redak combat u datoteci je jedan redak). Oznake oblikovanja uklanjaju se prije uspoređivanja. Datoteka je kroz godine bila i UTF-8 i UTF-16; čitaju se obje. Format CCP ne dokumentira; to je običan tekstualni dnevnik klijenta, čitan kao što ga čitaju zajednički alati za borbeni dnevnik (npr. <https://docs.rs/crate/eve-log-parser>). Nema pozicija.

Pored toga, `Documents\EVE\logs\Chatlogs\<channel>_<yyyymmdd>_<hhmmss>[_<id>].txt`: jedna datoteka po chat kanalu po prijavi (kad je bilježenje chata uključeno, što je zadano u klijentu), UTF-16, zaglavlje s imenom kanala i slušatelja, zatim `[ yyyy.mm.dd hh:mm:ss ] Sender > message`.

Svaki redak oba tipa čuva se cijel u sirovom pratećem dijelu sesije (pravilo pretvarača 3DHeat): redak gamelog-a pod svojim kanalom u zagradama (`combat`, `notify`, `bounty`, `None`, ...), chat redak kao `chat` s kanalom, a redci zaglavlja kao `gamelog header` / `chatlog header`.

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

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz imena statistike same igre nisu na ovom popisu; odjeljak „Što se bilježi“ ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeata: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json`-u broji svaki `type` - `lost` je 0.

**Čita se**

- gamelog `(combat)` pogoci naneseni i primljeni (iznos, drugi pilot, oznaka korporacije, brod, oružje, kvaliteta pogotka) i promašaji u oba smjera
- gamelog `(bounty)` isplate s ISK-om i redci `Jumping from A to B`
- Listener iz zaglavlja gamelog-a: čiji je to dnevnik

**Čuva se sirovo**

- svaki redak gamelog-a cijel, `type` = njegov kanal u zagradama (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), uz `file` i `listener`; `used` gdje je postao retkom; redci zaglavlja kao `gamelog header`
- svaki chat redak cijel (Local, korporacija, flota, privatni kanali, obavijesti `EVE System` kao promjena Local kanala pri skoku), `type` `chat`, uz `channel`, `listener` i `file`; redci zaglavlja kao `chatlog header`. Još se ne pretvaraju u retke

**Nije dostupno**

- pozicije: klijent ih ne piše u dnevnike
- borbe drugih pilota: gamelog je samo dnevnik slušatelja
- dnevnici ranijih prijava: svaka prijava piše nove datoteke; one starije od ovog pokretanja klijenta se ne čitaju ponovno
- chat kad je igrač u postavkama klijenta isključio bilježenje chata
- predmemorija i datoteke postavki klijenta: nisu dnevnici, i nisu dokumentirane

**Veličina**: gamelog je 0,1-2 MB po satu (najviše u borbi); chat dnevnici ovise o otvorenim kanalima - zauzet Local ili flota 0,5-3 MB po satu; zstd u heat.raw.parquet ih smanjuje na otprilike desetinu

## Provjereno {#verified}

testirano na sintetičkim redcima gamelog-a u formatu koji objavljuju zajednički razvijači alata; neprovjereno u samoj igri

## Izvor {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
