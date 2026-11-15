---
title: "osu! (snimci)"
nav_order: 35
lang: "bs"
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (snimci) {#osu-replays}

Poslije meča u osu!, watcher pretvara snimak koji je igra spremila u datoteke koje možete pogledati na mapi u preglednik 3DHeat-u.

*Tehnički detalji: adapter `osu-replays`, vrsta [`replay`](sources-and-rules.md); radi cijelo vrijeme (ne čeka da se igra pokrene) i svakih 5 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- putanja kursora preko polja za igru (x 0..512, y 0..384) i držani tasteri, u svakom frejmu
- rezultat, combo, 300-ice/100-ice/50-ice/gekiji/katui/promašaji, tačnost, modovi, full combo
- traka života tokom igranja, hashevi beatmape i snimka, random seed, online id rezultata

## Odakle dolazi {#where-it-comes-from}

snimci koje osu! (stable) sprema: %LOCALAPPDATA%/osu!/Data/r/\*.osr (svako igranje) i osu!/Replays/\*.osr (izvezeni)

## Kako ga uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Snimci i demoi: ono što igra spremi o meču, pretvoreno kad meč završi.

Snimak drži sve što živi interfejs u multiplayer igrama zadržava za sebe -
poziciju svakog igrača, svako ubistvo gdje se desilo - a to je datoteka koju
igra piše za svoje igrače, pa čitanje ništa ne dira u igri. Watcher
gleda foldere u koje igre spremaju snimke, čeka da nova datoteka prestane
rasti (inače je igra još piše) i pretvara je u
radnoj niti, pa duga konverzija nikad ne zadržava ostatak watchera.

Kad se folder prvi put vidi, snimci koji su već u njemu samo se zabilježe, ne
pretvaraju: igrač s godinama demoa inače bi našao watcher zauzet
cijeli dan. `python -m heat3d_watch replays <adapter> [folder]` pretvara
postojeće na zahtjev.

#### osu! {#osu}

osu! (stable) sprema svako igranje u `osu!/Data/r/*.osr`, a izvezene u
`osu!/Replays/`. Watcher ih čita sam, prema formatu koji osu! wiki
objavljuje: putanja kursora i tasteri u svakom frejmu, linija rezultata, traka
života, seed i id rezultata; datoteka se čuva i cijela pored, dio po dio,
u `heat.raw.parquet` sesije.

Isti modul služi i za: [Counter-Strike 2 (snimci)](game-cs2-demos.md), [Dota 2 (snimci)](game-dota-replays.md), [Squad (snimci)](game-squad-demos.md), [War Thunder (snimci)](game-warthunder-replays.md), [World of Tanks (snimci)](game-wot-replays.md), [World of Warships (snimci)](game-wows-replays.md).

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Osa gore | `y` |
| Jedinice | osu! pikseli (polje za igru 512 x 384) |
| Zrcaljeno za preglednik | `z` |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `replay`: čita samo ono što igra ili platforma daje (snimke i demoe koje igra sprema), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`accuracy`, `full_combo`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- svaki frejm: red u njegovom vremenu (milisekunde zbrojene), x i y na polju za igru, `keys` bitovi tastera (miš 1 i 2, tasteri 1 i 2, smoke); u maniji x drži držane tastere umjesto mjesta
- zaglavlje, svako polje: mod, verzija, MD5 beatmape (datoteka beatmapu imenuje samo njime), igrač, MD5 snimka, 300-ice, 100-ice, 50-ice, gekiji, katui, promašaji, rezultat, maksimalni combo, full combo, modovi (po imenu u meta.json `osu.modNames`), vrijeme igranja - kao statistika i u meta.json `osu`
- graf trake života: red `life` po tački (vrijeme, život 0..1)
- frejm `-12345`: random seed (`osu.seed`); online id rezultata (`osu.scoreId`); kod Target Practice, njegova tačnost (`osu.targetPracticeAccuracy`)

**Čuva se sirovo**

- datoteka cijela, dio po dio, u heat.raw.parquet (`offset` gdje svaki počinje, pa su dijelovi datoteka): `header`, `replay_data` (frejmovi komprimirani LZMA-om onako kako su spremljeni), `score_id`, `mod_info`, i `trailing` za sve što slijedi iza dijelova koje format opisuje (izvozi osu!lazer-a tu dodaju podatke) - čuva se, ne čita

**Nije dostupno**

- sama beatmapa (hit objekti, vremena): nije u snimku; imenuje se samo njenim MD5
- vlastiti snimci osu!lazer-a: čuvaju se u njegovoj bazi, ne kao datoteke

**Veličina**: sirovi sidecar je otprilike veličine snimka (deseci do stotine kilobajta)

## Provjereno {#verified}

testirano na snimcima izgrađenim prema objavljenom .osr formatu; osu!lazer čuva snimke u vlastitoj pohrani i ne čita se

## Izvor {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
