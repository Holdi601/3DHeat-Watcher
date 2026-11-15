---
title: "osu! (replay-i)"
nav_order: 35
lang: "hr"
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (replay-i) {#osu-replays}

Nakon utakmice osu!, watcher pretvara replay koji je igra spremila u datoteke koje možete pogledati na karti u 3DHeat pregledniku.

*Tehnički detalji: adapter `osu-replays`, vrsta [`replay`](sources-and-rules.md); radi cijelo vrijeme (ne čeka da se igra pokrene) i traži nove podatke svakih 5 s.*

## Što se bilježi {#what-is-recorded}

- putanja kursora preko igrališta (x 0..512, y 0..384) i tipke koje su bile pritisnute, svaki okvir
- rezultat, kombo, 300-ice/100-ice/50-ice/gekiji/katui/promašaji, točnost, modovi, puni kombo
- traka života tijekom igre, hashevi mape i replaya, slučajno sjeme, ID online rezultata

## Odakle dolazi {#where-it-comes-from}

replay-i koje sprema osu! (stabilna verzija): %LOCALAPPDATA%/osu!/Data/r/\*.osr (svaka igra) i osu!/Replays/\*.osr (izvezeni)

## Kako to uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Replay-i i demo-i: što igra sprema o utakmici, pretvoreno kad se utakmica završi.

Replay sadrži sve što živo sučelje u igrama za više igrača zadržava - položaj svakog igrača, svako ubojstvo tamo gdje se dogodilo - i datoteka je koju igra piše za svoje igrače, pa njegovo čitanje ništa ne dira u igri. Watcher gleda mape u koje igre spremaju te datoteke, čeka da nova datoteka prestane rasti (inače je igra još piše) i pretvara je u radnoj niti, pa dugo pretvaranje ne zaustavlja ostatak watchera.

Kad se mapa prvi put vidi, replay-i koji su već u njoj samo se zabilježe, ne pretvaraju se: igrač s godinama demo-a inače bi zatekao watcher zauzetog cijeli dan. `python -m heat3d_watch replays <adapter> [folder]` pretvara postojeće na zahtjev.

#### osu! {#osu}

osu! (stabilna verzija) sprema svaku igru u `osu!/Data/r/*.osr`, a izvezene u `osu!/Replays/`. Watcher ih sam čita, prema formatu koji objavljuje osu! wiki: putanja kursora i tipke svaki okvir, linija rezultata, traka života, sjeme i ID rezultata; datoteka se uz to čuva cijela, dio po dio, u `heat.raw.parquet` sesije.

Isti modul služi i: [Counter-Strike 2 (replay-i)](game-cs2-demos.md), [Dota 2 (replay-i)](game-dota-replays.md), [Squad (replay-i)](game-squad-demos.md), [War Thunder (replay-i)](game-warthunder-replays.md), [World of Tanks (replay-i)](game-wot-replays.md), [World of Warships (replay-i)](game-wows-replays.md).

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Bilježe se pozicije | da |
| Os prema gore | `y` |
| Jedinice | osu! pikseli (igralište 512 x 384) |
| Zrcaljeno za preglednik | `z` |
| Mjerilo jedinice (`scale`: preglednik ovim množi pozicije) | 1 |

Ovo ide u `meta.json` (`axes`) svake sesije i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `replay`: čita samo ono što igra ili platforma daje (replay-e i demo-e koje igra sprema), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: adapter je **nikad** ne čita. Memoriju čitaju samo adapteri vrste `memory`, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` u `meta.json` svake sesije i tablica `stats` u `watcher.sqlite`):

`accuracy`, `full_combo`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz imena statistike same igre nisu na ovom popisu; odjeljak „Što se bilježi“ ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeata: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json`-u broji svaki `type` - `lost` je 0.

**Čita se**

- svaki okvir: redak u njegovom vremenu (milisekunde zbrojene), x i y na igralištu, `keys` bitovi tipki (miš 1 i 2, tipke 1 i 2, dim); u načinu mania x označava pritisnute tipke umjesto mjesta
- zaglavlje, svako polje: način, verzija, MD5 beatmape (datoteka beatmapu imenuje samo njime), igrač, MD5 replaya, 300-ice, 100-ice, 50-ice, gekiji, katui, promašaji, rezultat, najveći kombo, puni kombo, modovi (po imenu u meta.json `osu.modNames`), vrijeme igre - kao statistika i u meta.json `osu`
- grafikon trake života: redak `life` po točki (vrijeme, život 0..1)
- okvir `-12345`: slučajno sjeme (`osu.seed`); ID online rezultata (`osu.scoreId`); uz Target Practice, njegova točnost (`osu.targetPracticeAccuracy`)

**Čuva se sirovo**

- datoteka cijela, dio po dio, u heat.raw.parquet (`offset` gdje svaki dio počinje, pa su dijelovi datoteka): `header`, `replay_data` (okviri kompresirani LZMA-om kako su pohranjeni), `score_id`, `mod_info`, i `trailing` za sve što slijedi iza dijelova koje format opisuje (izvozi osu!lazera tu dodaju podatke) - čuva se, ne čita se

**Nije dostupno**

- sama beatmapa (objekti pogotka, vremenski raspored): nije u replayu; imenovana je samo svojim MD5-om
- osu!lazer-ovi vlastiti replay-i: čuvaju se u njegovoj bazi, ne kao datoteke

**Veličina**: sirovi prateći dio otprilike je veličine replaya (desetci do stotine kilobajta)

## Provjereno {#verified}

testirano na replay-ima izrađenim prema objavljenom .osr formatu; osu!lazer čuva replay-e u vlastitoj pohrani i ne čita se

## Izvor {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
