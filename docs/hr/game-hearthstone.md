---
title: "Hearthstone (datoteke dnevnika)"
nav_order: 25
lang: "hr"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (datoteke dnevnika) {#hearthstone-log-files}

Dok igrate Hearthstone, watcher čita datoteke koje igra piše i sprema što se dogodilo, pa to kasnije možete pogledati kao statistiku i vremensku crtu.

*Tehnički detalji: adapter `hearthstone`, vrsta [`log`](sources-and-rules.md); radi dok je `Hearthstone.exe` pokrenut i traži nove podatke svakih 0,5 s.*

## Što se bilježi {#what-is-recorded}

- početak i kraj igre, s ishodom (pobjeda, poraz, neriješeno), brojem poteza i imenom protivnika
- svaki potez
- svaki redak datoteke Power.log i drugih dnevnika cijel u heat.raw.parquet
- igre, pobjede, porazi, neriješene, potezi, najduža igra

## Odakle dolazi {#where-it-comes-from}

&lt;install>\Logs\Power.log (ili Logs\Hearthstone_\*\Power.log), kad %LOCALAPPDATA%\Blizzard\Hearthstone\log.config ima odjeljak [Power], i svaki ostali \*.log koji igra piše u toj mapi

## Kako to uključiti {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` dodaje zapisivanje [Power] u %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (sigurnosna kopija se čuva); ponovno pokrenite igru

Naredbu upišite u terminalu otvorenom u mapi watchera (vidi [Prije nego što počnete](before-you-start.md)). Ako ne uspije, zadnji redak kaže zašto; [Instalacija i pokretanje](installing-and-running.md) opisuje uobičajene uzroke.

`python -m heat3d_watch setup hearthstone` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup hearthstone --apply` ih mijenja, a original čuva kao `<file>.heat3d-backup` (vidi [Naredbe](commands.md#setup)). Za svaku promjenu ispisuje `hearthstone: changed: ...`, ili `hearthstone: nothing to change` kad je već uključeno.

## Kako radi {#how-it-works}

Hearthstone: igrin Power.log, koji piše čim ga log.config zatraži.

Hearthstone pri pokretanju čita `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config`; odjeljak `[Power]` s `LogLevel=1` i `FilePrinting=true` tjera igru da zapisuje svaku promjenu stanja svake igre u `<install>\Logs\Power.log` (noviji klijenti stavljaju dnevnike svakog pokretanja u vlastitu mapu, `Logs\Hearthstone_<datum>\`). To je dokumentirano otklanjanje grešaka koje praćači špila imaju uključeno od 2014. (postavljanje Hearthstone Deck Trackera piše isti odjeljak). `setup()` dodaje odjeljak, uz sigurnosnu kopiju datoteke kakva je bila; igra treba ponovno pokretanje da ga pročita.

Korišteni redci, svi iz `GameState.DebugPrintPower()` (redci `PowerTaskList` ponavljaju ih i preskaču se):

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

Vaša strana je ona čija su imena karata u početnoj ruci vidljiva (protivnikove su skrivene), inače strana koja nije AI (račun 0) ili „UNKNOWN HUMAN PLAYER“. Redci nose samo vrijeme dana; datum je današnji. Nema pozicija.

Svaki redak Power.log-a čuva se cijel u sirovom pratećem dijelu sesije (pravilo pretvarača 3DHeat), uključujući ponavljanja `PowerTaskList`, opcije, izbore i ažuriranja entiteta: `type` je metoda koja ga je zapisala (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Svaki drugi dnevnik koji igra piše pored njega - `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ..., svaki tamo kad ga log.config zatraži (praćači špila to često čine) - prati se na isti način i čuva pod svojim imenom u `log`.

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

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz imena statistike same igre nisu na ovom popisu; odjeljak „Što se bilježi“ ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeata: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json`-u broji svaki `type` - `lost` je 0.

**Čita se**

- `CREATE_GAME`, igrači (entitet, ID igrača, račun; račun 0 je AI) i njihova imena (`DebugPrintGame`)
- čija je strana igračeva, iz imenovanih karata u početnoj ruci
- `TAG_CHANGE` za TURN, PLAYSTATE (won, lost, tied) i STATE COMPLETE: potezi, ishod, protivnik

**Čuva se sirovo**

- svaki redak Power.log-a cijel, `type` = metoda koja ga je zapisala (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` gdje je postao retkom: svaka odigrana, izvučena i otkrivena karta, svaka promjena oznake, napad, opcija i izbor je ovdje, još nije u retcima
- svaki redak drugih dnevnika iz iste mape (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - što god log.config uključi), isti `type`-ovi, uz ime dnevnika u `log`
- redak bez razine i vremena dana kao `untimed`, bez metode kao `untagged`

**Nije dostupno**

- pozicije: kartaška igra ih nema
- skrivene karte protivnika: dnevnik imenuje kartu tek kad se otkrije
- dnevnici koje log.config ne uključuje: `setup` traži samo [Power]; ostali dnevnici dolaze kad ih uključi neki drugi alat (praćač špila)
- dnevnici ranijih pokretanja: svako pokretanje piše novu mapu; one starije od ovog pokretanja igre se ne čitaju ponovno

**Veličina**: Power.log s opširnim zapisom je oko 1-5 MB po igri, 10-40 MB po satu igre; ostali dnevnici malo dodaju; zstd u heat.raw.parquet ga smanjuje na otprilike desetinu ili manje (redci se jako ponavljaju)

## Provjereno {#verified}

testirano na sintetičkim redcima Power.log-a u formatu igre; neprovjereno u samoj igri

## Izvor {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
