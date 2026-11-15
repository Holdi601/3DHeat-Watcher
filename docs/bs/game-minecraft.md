---
title: "Minecraft (log datoteke)"
nav_order: 33
lang: "bs"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (log datoteke) {#minecraft-log-files}

Dok igrate Minecraft, watcher čita datoteke koje igra piše i sprema šta se desilo, da to kasnije možete pogledati na mapi u preglednik 3DHeat-u.

*Tehnički detalji: adapter `minecraft`, vrsta [`log`](sources-and-rules.md); radi dok je pokrenut `javaw.exe` ili `java.exe` i svakih 0,5 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- položaj vlastitog i drugih igrača (blokovi = m, y gore) svaki put kad se svijet sprema, dimenzija kao sesija
- pojavljivanje (spawn) s položajem kad se igrač prijavi na (integrirani) server
- ulasci, izlasci, smrti s porukom o smrti, advancements, linije chata
- smrti, advancements, poruke chata; iz stats datoteke: vrijeme igranja, pređena distanca, ubijeni mobovi i igrači, skokovi, šteta, iskopani blokovi, izrađeni predmeti (udio ove sesije)
- svaka linija loga i svaka sačuvana datoteka stats, advancements i igrača cijela u heat.raw.parquet

## Odakle dolazi {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (prati se), saves\\&lt;world>\stats\\&lt;uuid>.json i saves\\&lt;world>\playerdata\\&lt;uuid>.dat / level.dat (gzip NBT), čitaju se kad ih igra sprema

## Kako ga uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Minecraft (Java Edition): log, statistika i datoteke igrača koje igra piše.

Gdje (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - log igre, nov pri svakom pokretanju (stari se
  pakuje u datirani .log.gz). Linije `[hh:mm:ss] [thread/LEVEL]: message`
  (učitavači modova pišu `[ddMMMyyyy hh:mm:ss.mmm] [thread/LEVEL] [logger/]: ...`).
  Ono što igrači vide u chatu je u njemu: ulasci i izlasci, poruke o smrti,
  advancements, chat - integrirani server svijeta za jednog igrača piše
  iste linije još jednom, pa se linija ponovljena unutar iste sekunde računa
  jednom. "Setting user: &lt;name>" imenuje igrača; serverov
  "&lt;name>[...] logged in with entity id N at (x, y, z)" daje mjesto gdje je
  nastao.
* `saves\<world>\stats\<uuid>.json` - ekran statistike, piše se kad se
  svijet sprema (automatsko spremanje svakih nekoliko minuta, i pri izlasku): `stats` ->
  `minecraft:custom` (play_time u tickovima, mob_kills, udaljenosti \*_one_cm, jump,
  ...), `minecraft:mined`, `minecraft:crafted`, ... Zbirovi za svijet; brojke
  sesije su razlika u odnosu na ono što je datoteka govorila kad se igra
  pokrenula. Format: <https://minecraft.wiki/w/Statistics>
* `saves\<world>\playerdata\<uuid>.dat` (i `level.dat` -> Data -> Player
  za domaćina u igri za jednog igrača) - gzip-komprimirani NBT, piše se pri istim spremanjima:
  `Pos` [x, y, z] doubleovi, `Rotation` [yaw, pitch], `Dimension`
  ("minecraft:overworld"; int 0/-1/1 prije 1.16). NBT prema
  <https://minecraft.wiki/w/NBT_format> - ovdje ga čita mali vlastiti čitač.
* `saves\<world>\advancements\<uuid>.json` - napredak sa ekrana advancements,
  piše se pri istim spremanjima.

Koordinate su blokovi, jedan blok je metar, y gore; x istok, z jug - desnoruki
okvir, crta se kakav jest. Položaji dolaze samo kad se svijet sprema, pa je
ruta nekoliko tačaka po automatskom spremanju, a ne trag; dimenzija je
`session`, pa se Nether ne crta preko Overworlda.

Sve pročitano čuva se cijelo u sirovom sidecar-u sesije (3DHeat-ovo pravilo
konvertera): svaka linija loga pod svojim nivoom (`INFO`, `WARN`, `ERROR`, ...; linija
bez zagradom označenog početka, poput stack trace-a, kao `untagged`), a svaka
sačuvana datoteka pod svojom vrstom (`stats`, `advancements`, `playerdata`,
`level.dat`) - JSON kao tekst, NBT kao bajtovi. Brojevi stats datoteke se mogu
razumjeti samo u odnosu na ono što je govorila kad se igra pokrenula, pa se i ta prva kopija
čuva (`baseline`), prvi put kad se datoteka promijeni.

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Osa gore | `y` |
| Jedinice | blokovi (1 blok = 1 m) |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `log`: čita samo ono što igra ili platforma daje (datoteke koje igra piše dok radi), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- latest.log: ime igrača (`Setting user`), prijave s položajem, ulasci, izlasci, smrti s porukom o smrti, advancements, linije chata, zaustavljanje servera
- stats/&lt;uuid>.json: vrijeme igranja, pređena distanca, ubijeni mobovi i igrači, skokovi, zadana i primljena šteta, iskopani blokovi, izrađeni predmeti - udio ove sesije
- playerdata/&lt;uuid>.dat i level.dat (NBT): položaj, dimenzija, yaw, pitch, zdravlje, XP nivo

**Čuva se sirovo**

- svaka linija latest.log cijela, `type` = njen nivo (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) s threadom loggera u `thread`, `used` gdje je postala red; linija bez zagradom označenog početka (stack trace, baner moda) kao `untagged`
- svaki stats/&lt;uuid>.json cijel kao tekst, `type` `stats` (`used`: njegovi brojevi su u statistici), s prvom kopijom s početka igre kao `baseline`
- svaki advancements/&lt;uuid>.json cijel kao tekst, `type` `advancements` (svaki kriterij i kad je ispunjen; još nije pretvoreno u redove)
- svaki playerdata/&lt;uuid>.dat i level.dat cijel kao bajtovi (gzip NBT), `type` `playerdata` / `level.dat`, `used` gdje je dao položaj: inventar, ender chest, efekti, tačka spawna, pravila igre, seed i vrijeme svijeta nalaze se samo ovdje
- svaka sačuvana datoteka ima `world` i `file` (njenu putanju pod `saves`)

**Nije dostupno**

- trag položaja: igra piše igračev položaj samo kad se svijet sprema (svakih nekoliko minuta i pri izlasku)
- položaji na serveru koji hostuje neko drugi: njegove datoteke svijeta su na serveru, ne ovdje; tada se čita samo log
- sam svijet (region .mca datoteke, entiteti, data/\*.dat mape i raids): veliko je, i to je teren, a ne igra
- logovi ranijih sesija (logs/\*.log.gz): čuvaju se kad su se igrale
- Bedrock Edition: ne piše takav log ni takve datoteke

**Veličina**: latest.log 0,1-2 MB na sat (više s modovima); stats datoteka 5-50 KB i datoteka igrača 5-100 KB po automatskom spremanju, level.dat 1-20 KB - ukupno oko 1-5 MB na sat; zstd u heat.raw.parquet svodi tekst otprilike na desetinu (NBT datoteke su već gzip)

## Provjereno {#verified}

testirano na sintetičkim linijama loga, stats JSON-u i NBT datotekama izgrađenim iz objavljenih formata; nije testirano na igri

## Izvor {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
