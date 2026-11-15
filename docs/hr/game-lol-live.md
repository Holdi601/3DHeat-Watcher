---
title: "League of Legends (stanje igre)"
nav_order: 29
lang: "hr"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (stanje igre) {#league-of-legends-game-state}

Dok igrate League of Legends, watcher sprema ono što igra javlja programima na vašem računalu, pa to kasnije možete pogledati kao statistiku i vremensku crtu.

*Tehnički detalji: adapter `lol-live`, vrsta [`gsi`](sources-and-rules.md); radi dok je `League of Legends.exe` pokrenut i traži nove podatke svakih 0,5 s.*

## Što se bilježi {#what-is-recorded}

- nema pozicija: API ih nema
- tok ubojstava: ubojstva, smrti i asistencije igrača, ubojstva drugih prvaka s ubojicom, žrtvom i asistentima
- zmajevi, heraldi, baroni, tornjevi, inhibitori, višestruka ubojstva, ace-ovi, prva krv, početak i kraj igre
- vlastita ubojstva, smrti, asistencije, rezultat stvorenja, rezultat čuvanja, razina, zlato, prvak, vrijeme igre, ishod
- ciljevi koje je uzeo tim igrača

## Odakle dolazi {#where-it-comes-from}

Live Client Data API klijenta igre, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), tijekom utakmice

## Kako to uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

League of Legends: Live Client Data API koji klijent igre poslužuje tijekom utakmice.

Dok utakmica traje (i u vježbalištu i u načinu gledanja), `League of Legends.exe` odgovara na <https://127.0.0.1:2999> s onim što igrač vidi u vlastitom sučelju igre:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} od EventID N naovamo: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Nema pozicija: API ih nema, pa je League sesija događaji i statistika, bez tablice pozicija. Certifikat je samopotpisan, Riotovim vlastitim korijenskim certifikatom (`riotgames.pem`, objavljen na <https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Uvjeti njegove uporabe nisu navedeni, pa se ne isporučuje: stavite ga u `<data>\riotgames.pem` i veza se provjerava njime; bez njega provjera je isključena - i to samo za 127.0.0.1, jedinu adresu s kojom ovaj adapter razgovara.

Riotova politika dopušta alatima prikaz onoga što igrač može znati iz same igre, i ništa izračunato preko toga (bez timera protivnika): ovo bilježi tok ubojstava i rezultatsku tablicu koju igrač vidi, te vlastite brojke igrača.

Svaki odgovor čuva se i cijel (pravilo pretvarača 3DHeat, docs/converters.md u repozitoriju preglednika): `heat.raw.parquet`, `type` je krajnja točka ("allgamedata", "eventdata"), `text` je JSON kako ga je klijent poslao, `status` kad nije bio 200. Odgovor bajt po bajt isti kao prethodni iste krajnje točke (popis događaja dok se ništa ne događa) čuva se jednom i broji se u `unchanged_replies` u meta.json-u. allgamedata sadrži sve što služe ostale krajnje točke (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), pa se one ne pitaju zasebno. Odgovori prije utakmice (ekran učitavanja) čekaju u zaostatku i ulaze u sesiju utakmice; nakon GameEnd sesija ostaje otvorena dok klijent ne ode, pa se odgovori završnog ekrana čuvaju uz nju.

Izvor: <https://developer.riotgames.com/docs/lol#game-client-api>

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Bilježe se pozicije | nema |
| Os prema gore | `z` |
| Jedinice | nema (nema pozicija) |
| Zrcaljeno za preglednik | nema |
| Mjerilo jedinice (`scale`: preglednik ovim množi pozicije) | 1 |

Ovo ide u `meta.json` (`axes`) svake sesije i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `gsi`: čita samo ono što igra ili platforma daje (integraciju stanja igre ili lokalni API koji igra poslužuje), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: adapter je **nikad** ne čita. Memoriju čitaju samo adapteri vrste `memory`, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` u `meta.json` svake sesije i tablica `stats` u `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz imena statistike same igre nisu na ovom popisu; odjeljak „Što se bilježi“ ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeata: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json`-u broji svaki `type` - `lost` je 0.

**Čita se**

- tok ubojstava iz eventdata: svaki događaj jednom, s dekodiranim imenovanim poljima (ubojica, žrtva i asistenti s prvakom i timom, građevine i njihova strana, vrsta zmaja, preuzimanja, višestruka ubojstva, aceovi, prva krv, ishod), a svako ostalo polje događaja na njegovom retku pod vlastitim imenom
- iz allgamedata: vlastita ubojstva, smrti, asistencije, rezultat stvorenja, rezultat čuvanja, razina, zlato, prvak, vrijeme igre, način igre i karta

**Čuva se sirovo**

- `allgamedata`: svaki odgovor cijel (`text`), svake 2 s - activePlayer (sposobnosti, svaka statistika prvaka, cijele rune, zlato, razina), allPlayers (predmeti s mjestima i cijenama, rune, prizivne čarolije, rezultati, razina, mrtav i tajmer oživljavanja, skin, traka, bot), događaji, gameData (način, vrijeme, karta, teren); `used` istinit dok utakmica traje, lažan na završnom ekranu
- `eventdata`: svaki odgovor cijel, traži se svakih 0,5 s od sljedećeg ID-ja događaja; `used` istinit kad je donio nove događaje
- odgovor bajt po bajt isti kao prethodni iste krajnje točke čuva se jednom i broji se (`unchanged_replies` u meta.json-u); odgovori o grešci (RESOURCE_NOT_FOUND na ekranu učitavanja) čuvaju se s `status`-om, prije početka utakmice

**Nije dostupno**

- pozicije: API ih nema (nema minimape, nema koordinata)
- ostale krajnje točke (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): svaka služi dio allgamedata, pa se ne pitaju
- Replay API (`/replay/*` na istom portu): reproducira reprize i gledane igre kad se uključi u game.cfg, nije dio odigrane utakmice
- krajnje točke lockfile-a League klijenta: nije objavljeni API (Izvori i pravila)
- vrijednosti između dva čitanja: API odgovara kad ga se pita i ne šalje sam; rezultatska tablica se pita svake 2 s, a događaji svakih 0,5 s

**Veličina**: allgamedata je 15-40 KB (sadrži cijeli popis događaja, koji raste) svake 2 s: oko 30-70 MB po satu u `raw.bin`; eventdata malo dodaje, jer se nepromijenjeni odgovori broje, a ne spremaju; zstd smanjuje ponovljeni JSON u `heat.raw.parquet` na nekoliko MB po satu (procijenjeno iz dokumentiranog formata)

## Provjereno {#verified}

testirano na lažnom lokalnom poslužitelju koji poslužuje odgovore u dokumentiranom formatu; neprovjereno u samoj igri

## Izvor {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
