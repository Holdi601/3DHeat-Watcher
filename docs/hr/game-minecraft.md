---
title: "Minecraft (datoteke dnevnika)"
nav_order: 33
lang: "hr"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (datoteke dnevnika) {#minecraft-log-files}

Dok igrate Minecraft, watcher čita datoteke koje igra piše i sprema što se dogodilo, pa to kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `minecraft`, vrsta [`log`](sources-and-rules.md); radi dok su `javaw.exe` ili `java.exe` pokrenuti i traži nove podatke svakih 0,5 s.*

## Što se bilježi {#what-is-recorded}

- vlastiti i tuđi položaji igrača (blokovi = m, y gore) svaki put kad se svijet spremi, dimenzija kao sesija
- pojava s položajem kad se igrač prijavi na (integrirani) server
- ulasci, izlasci, smrti s porukom smrti, postignuća, redci razgovora
- smrti, postignuća, poruke u razgovoru; iz datoteke statistike: vrijeme igre, udaljenost, ubojstva mobova i igrača, skokovi, šteta, iskopani blokovi, izrađeni predmeti (udio ove sesije)
- svaki redak dnevnika i sva spremljena statistika, postignuća i datoteke igrača cijeli u heat.raw.parquet

## Odakle dolaze {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (prati se), saves\\&lt;world>\stats\\&lt;uuid>.json i saves\\&lt;world>\playerdata\\&lt;uuid>.dat / level.dat (gzip NBT), čitaju se kad igra spremi

## Kako ga uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Minecraft (Java Edition): dnevnik, statistika i datoteke igrača koje igra piše.

Gdje (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - dnevnik igre, nov pri svakom pokretanju (stari se pakira
  u datirani .log.gz). Redci `[hh:mm:ss] [thread/LEVEL]: poruka` (mod loaderi
  pišu `[ddMMMyyyy hh:mm:ss.mmm] [thread/LEVEL] [logger/]: ...`). Ono što igrači
  vide u razgovoru nalazi se u njemu: ulasci i izlasci, poruke smrti,
  postignuća, razgovor - integrirani server jednoigračkog svijeta piše iste
  retke još jednom, pa se redak ponovljen unutar iste sekunde broji jednom.
  "Setting user: <name>" imenuje igrača; serverov
  "<name>[...] logged in with entity id N at (x, y, z)" kaže gdje se pojavio.
* `saves\<world>\stats\<uuid>.json` - ekran statistike, piše se kad se svijet
  sprema (automatsko spremanje svakih nekoliko minuta, i pri izlasku): `stats` ->
  `minecraft:custom` (play_time u tickovima, mob_kills, \*_one_cm udaljenosti,
  jump, ...), `minecraft:mined`, `minecraft:crafted`, ... Ukupno za svijet; brojke
  sesije su razlika u odnosu na ono što je datoteka pokazivala kad je igra
  krenula. Format: <https://minecraft.wiki/w/Statistics>
* `saves\<world>\playerdata\<uuid>.dat` (i `level.dat` -> Data -> Player za
  jednoigračkog domaćina) - NBT komprimiran gzipom, piše se pri istim spremanjima:
  `Pos` [x, y, z] kao double, `Rotation` [yaw, pitch], `Dimension`
  ("minecraft:overworld"; int 0/-1/1 prije 1.16). NBT prema
  <https://minecraft.wiki/w/NBT_format> - ovdje ga čita mali vlastiti čitač.
* `saves\<world>\advancements\<uuid>.json` - napredak ekrana postignuća,
  piše se pri istim spremanjima.

Koordinate su blokovi, jedan blok je jedan metar, y gore; x istok, z jug - desno
orijentiran okvir, crta se onako kakav jest. Položaji dolaze samo kad se svijet
spremi, pa je ruta nekoliko točaka po automatskom spremanju, a ne trag; dimenzija
je `session`, pa se Nether ne crta preko Overworlda.

Sve pročitano čuva se cijelo u sesijskoj sirovoj pomoćnoj datoteci (pravilo
pretvarača 3DHeat): svaki redak dnevnika pod svojom razinom (`INFO`, `WARN`,
`ERROR`, ...; redak bez uglate oznake na početku, kao trag stoga ili baner moda,
kao `untagged`), a svaka spremljena datoteka pod svojom vrstom (`stats`,
`advancements`, `playerdata`, `level.dat`) - JSON kao tekst, NBT kao svoji bajti.
Brojke datoteke statistike razumiju se samo u odnosu na ono što je pokazivala kad
je igra krenula, pa se i ta prva kopija čuva (`baseline`), pri prvoj promjeni datoteke.

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Os gore | `y` |
| Jedinice | blokovi (1 blok = 1 m) |
| Zrcaljenje za preglednik | nema |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovo ulazi u `meta.json` (`axes`) svake sesije i, kad sesija ima položaje, u podnožje `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira retke - pogledajte [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `log`: čita samo ono što igra ili platforma predaje (datoteke koje igra piše dok radi), pa bilježi i u igri na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri vrste `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - pogledajte [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Što se bilježi" gore ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeat-a: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je ujedno postalo retcima), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- latest.log: ime igrača (`Setting user`), prijave s položajem, ulasci, izlasci, smrti s porukom smrti, postignuća, redci razgovora, zaustavljanje servera
- stats/<uuid>.json: vrijeme igre, udaljenost, ubojstva mobova i igrača, skokovi, učinjena i primljena šteta, iskopani blokovi, izrađeni predmeti - udio ove sesije
- playerdata/<uuid>.dat i level.dat (NBT): položaj, dimenzija, yaw, pitch, zdravlje, razina iskustva

**Čuva se sirovo**

- svaki redak latest.log cijel, `type` = njegova razina (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) s dretvom zapisnika u `thread`, `used` gdje je postao retkom; redak bez uglate oznake na početku (trag stoga, baner moda) kao `untagged`
- svaki stats/<uuid>.json cijel kao tekst, `type` `stats` (`used`: njegovi brojevi su u statistici), s prvom kopijom iz početka igre kao `baseline`
- svaki advancements/<uuid>.json cijel kao tekst, `type` `advancements` (svaki kriterij i kad je ispunjen; još nije pretvoreno u retke)
- svaki playerdata/<uuid>.dat i level.dat cijel kao bajti (gzip NBT), `type` `playerdata` / `level.dat`, `used` gdje je dao položaj: inventar, ender chest, efekti, točka pojavljivanja, pravila igre, sjeme svijeta i vrijeme su samo ovdje
- svaka spremljena datoteka ima `world` i `file` (njezin put pod `saves`)

**Nije dostupno**

- trag položaja: igra piše položaj igrača samo kad se svijet spremi (svakih nekoliko minuta i pri izlasku)
- položaji na serveru koji netko drugi drži: njegove datoteke svijeta su na serveru, ne ovdje; tada se čita samo dnevnik
- sam svijet (datoteke regiona .mca, entiteti, karte data/\*.dat i racije): veliko je, a riječ je o terenu, ne o igri
- dnevnici ranijih sesija (logs/\*.log.gz): čuvaju se kad su se igrale
- Bedrock Edition: ne piše takav dnevnik ni datoteke

**Veličina**: latest.log 0,1-2 MB po satu (više s modovima); datoteka statistike 5-50 KB i datoteka igrača 5-100 KB po automatskom spremanju, level.dat 1-20 KB - ukupno oko 1-5 MB po satu; zstd u heat.raw.parquet čini tekst otprilike desetinom (NBT datoteke su već u gzipu)

## Provjereno {#verified}

testirano na sintetičkim redcima dnevnika, JSON-u statistike i NBT datotekama izgrađenima prema objavljenim formatima; nije testirano na samoj igri

## Izvor {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i ponovno ga pokrenite umjesto uređivanja ove stranice. -->
