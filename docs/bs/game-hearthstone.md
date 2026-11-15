---
title: "Hearthstone (log datoteke)"
nav_order: 25
lang: "bs"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (log datoteke) {#hearthstone-log-files}

Dok igrate Hearthstone, watcher čita datoteke koje igra piše i sprema šta se desilo, da to kasnije možete pogledati kao statistiku i vremensku liniju.

*Tehnički detalji: adapter `hearthstone`, vrsta [`log`](sources-and-rules.md); radi dok je pokrenut `Hearthstone.exe` i svakih 0,5 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- početak i kraj partije, s ishodom (pobjeda, poraz, neriješeno), potezima i imenom protivnika
- svaki potez
- svaka linija Power.log i ostalih logova cijela u heat.raw.parquet
- partije, pobjede, porazi, neriješeni ishodi, potezi, najduža partija

## Odakle dolazi {#where-it-comes-from}

&lt;install>\Logs\Power.log (ili Logs\Hearthstone_\*\Power.log), piše se čim %LOCALAPPDATA%\Blizzard\Hearthstone\log.config ima odjeljak [Power], i svaki drugi \*.log koji igra tamo piše

## Kako ga uključiti {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` dodaje [Power] logging u %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (sigurnosna kopija se čuva); ponovo pokrenite igru

Upišite komandu u terminal otvoren u watcher-ovom folderu (vidite [Prije nego počnete](before-you-start.md)). Ako ne uspije, zadnja linija kaže zašto; [Instalacija i pokretanje](installing-and-running.md) obuhvata uobičajene uzroke.

`python -m heat3d_watch setup hearthstone` ispisuje datoteke koje bi promijenio; `python -m heat3d_watch setup hearthstone --apply` ih mijenja, a original čuva kao `<file>.heat3d-backup` (vidite [Komande](commands.md#setup)). Za svaku promjenu ispisuje `hearthstone: changed: ...`, ili `hearthstone: nothing to change` kad je već uključeno.

## Kako radi {#how-it-works}

Hearthstone: Power.log igre, koji ona piše čim to `log.config` zatraži.

Hearthstone pri pokretanju čita `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config`;
odjeljak `[Power]` s `LogLevel=1` i `FilePrinting=true` tjera ga da piše
promjene stanja svake partije u `<install>\Logs\Power.log` (noviji klijenti stavljaju
logove svakog pokretanja u vlastiti folder, `Logs\Hearthstone_<date>\`). To
je dokumentirano debug logiranje koje deck trackeri uključuju od 2014.
(postavljanje Hearthstone Deck Tracker-a piše isti odjeljak). `setup()` dodaje
odjeljak, uz sigurnosnu kopiju datoteke kakva je bila; igru treba ponovo pokrenuti da ga pročita.

Korištene linije, sve iz `GameState.DebugPrintPower()` (linije `PowerTaskList`
ih ponavljaju i preskaču se):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

Igračeva strana je ona čija početna ruka ima imenovane karte
(protivnikove su skrivene), inače strana koja nije AI (račun 0) ili
"UNKNOWN HUMAN PLAYER". Linije nose samo doba dana; datum je današnji.
Nema položaja.

Svaka linija Power.log čuva se cijela u sirovom sidecaru sesije (3DHeat-ovo
pravilo konvertera), uključujući ponavljanja `PowerTaskList`, opcije, izbore i ažuriranja
entiteta: `type` je metoda koja ju je napisala (`GameState.DebugPrintPower`,
`PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Svaki drugi
log koji igra piše pored njega - `LoadingScreen.log`, `Decks.log`, `Zone.log`,
`Arena.log`, ..., svaki je tu kad ga log.config zatraži (deck trackeri to
često rade) - prati se na isti način i čuva se s njegovim imenom u `log`.

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

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- `CREATE_GAME`, igrači (entitet, id igrača, račun; račun 0 je AI) i njihova imena (`DebugPrintGame`)
- čija je strana igračeva, prema imenovanim kartama početne ruke
- `TAG_CHANGE` za TURN, PLAYSTATE (pobjeda, poraz, neriješeno) i STATE COMPLETE: potezi, ishod, protivnik

**Čuva se sirovo**

- svaka linija Power.log cijela, `type` = metoda koja ju je napisala (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` gdje je postala red: svaka odigrana, izvučena i otkrivena karta, svaka promjena taga, napad, opcija i izbor je ovdje, još ne u redovima
- svaka linija ostalih logova u istom folderu (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - šta god log.config uključi), isti `type`-ovi, s imenom loga u `log`
- linija bez nivoa i doba dana kao `untimed`, ona bez metode kao `untagged`

**Nije dostupno**

- položaji: kartaška igra ih nema
- protivnikove skrivene karte: log imenuje kartu tek kad je otkrivena
- logovi koje log.config ne uključuje: `setup` traži samo [Power]; ostali logovi dolaze kad ih uključi neki drugi alat (deck tracker)
- logovi ranijih pokretanja: svako pokretanje piše novi folder; oni stariji od ovog pokretanja igre ne čitaju se ponovo

**Veličina**: Power.log s Verbose je oko 1-5 MB po partiji, 10-40 MB na sat igre; ostali logovi dodaju malo; zstd u heat.raw.parquet to smanjuje otprilike na desetinu ili manje (linije se mnogo ponavljaju)

## Provjereno {#verified}

testirano na sintetičkim linijama Power.log u formatu igre; nije testirano na igri

## Izvor {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
