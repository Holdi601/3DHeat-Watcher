---
title: "League of Legends (stanje igre)"
nav_order: 29
lang: "bs"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (stanje igre) {#league-of-legends-game-state}

Dok igrate League of Legends, watcher sprema ono što igra javlja programima na vašem računaru, da to kasnije možete pogledati kao statistiku i vremensku liniju.

*Tehnički detalji: adapter `lol-live`, vrsta [`gsi`](sources-and-rules.md); radi dok je pokrenut `League of Legends.exe` i svakih 0,5 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- nema položaja: API ih nema
- kill feed: ubistva, smrti i asistencije igrača, ubistva drugih šampiona s ubicom, žrtvom i asistentima
- zmajevi, heraldi, baroni, kule, inhibitori, multikillovi, aceovi, first blood, početak i kraj partije
- vlastita ubistva, smrti, asistencije, creep score, ward score, nivo, zlato, šampion, vrijeme igre, ishod
- ciljevi koje je uzeo igračev tim

## Odakle dolazi {#where-it-comes-from}

Live Client Data API klijenta igre, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), tokom meča

## Kako ga uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

League of Legends: Live Client Data API koji klijent igre služi tokom meča.

Dok meč traje (i u practice toolu i u spectator modu), `League of
Legends.exe` odgovara na <https://127.0.0.1:2999> onim što igrač može vidjeti u
vlastitom sučelju igre:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} from EventID N on: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Položaja nema: API ih nema, pa je League sesija skup događaja i
statistike, bez heat tabele. Certifikat je samopotpisan, Riotovim vlastitim
korijenom (`riotgames.pem`, objavljen na
<https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Uvjeti
korištenja nisu navedeni, pa se ne isporučuje: stavite ga na `<data>\riotgames.pem` i
veza se provjerava njime; bez njega je provjera isključena - i to samo
za 127.0.0.1, jedinu adresu s kojom ovaj adapter razgovara.

Riotova politika dozvoljava alatima da prikažu ono što igrač može znati iz same
igre, i ništa izračunato povrh toga (nema tajmera protivnika): ovo bilježi kill
feed i tabelu rezultata koju igrač vidi, te igračeve vlastite brojke.

Svaki odgovor se čuva i cijel (3DHeat-ovo pravilo konvertera, docs/converters.md
u repozitoriju preglednika): `heat.raw.parquet`, `type` je endpoint
("allgamedata", "eventdata"), `text` je JSON onako kako ga je klijent poslao, `status`
kad nije bio 200. Odgovor bajt po bajt isti kao prethodni istog endpointa (lista
događaja dok se ništa ne dešava) čuva se jednom i broji u `unchanged_replies` u meta.json.
allgamedata sadrži sve što služe ostali endpointi
(activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells,
playermainrunes, gamestats), pa se oni ne traže posebno. Odgovori prije
meča (ekran učitavanja) čekaju u zaostatku i idu u sesiju meča;
poslije GameEnd sesija ostaje otvorena dok klijent ne nestane, pa se odgovori
završnog ekrana čuvaju s njom.

Izvor: <https://developer.riotgames.com/docs/lol#game-client-api>

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | ne |
| Osa gore | `z` |
| Jedinice | nijedna (nema položaja) |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `gsi`: čita samo ono što igra ili platforma daje (game-state integracija ili lokalni API koji igra služi), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- kill feed iz eventdata: svaki događaj jednom, njegova imenovana polja dekodirana (ubica, žrtva i asistenti sa šampionom i timom, građevine i njihova strana, vrsta zmaja, krađe, multikillovi, aceovi, first blood, ishod) i svako drugo polje događaja u njegovom redu pod vlastitim imenom
- iz allgamedata: vlastita ubistva, smrti, asistencije, creep score, ward score, nivo, zlato, šampion, vrijeme igre, mod igre i mapa

**Čuva se sirovo**

- `allgamedata`: svaki odgovor cijel (`text`), svake 2 s - activePlayer (sposobnosti, svaka statistika šampiona, potpune rune, zlato, nivo), allPlayers (predmeti sa slotovima i cijenama, rune, summoner spellovi, rezultati, nivo, mrtav i tajmer oživljavanja, skin, lane, bot), događaji, gameData (mod, vrijeme, mapa, teren); `used` je istinito dok meč traje, neistinito na završnom ekranu
- `eventdata`: svaki odgovor cijel, traži se svake 0,5 s od sljedećeg id-a događaja nadalje; `used` je istinito kad je donio nove događaje
- odgovor bajt po bajt isti kao prethodni istog endpointa čuva se jednom i broji (`unchanged_replies` u meta.json); odgovori s greškom (RESOURCE_NOT_FOUND ekrana učitavanja) čuvaju se sa svojim `status`, prije početka meča

**Nije dostupno**

- položaji: API ih nema (nema minimape, nema koordinata)
- ostali endpointi (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): svaki služi dio allgamedata, pa se ne traže
- Replay API (`/replay/*` na istom portu): reproducira snimke i gledane partije kad se uključi u game.cfg, nije dio odigranog meča
- endpointi iz lockfile-a League klijenta: nije objavljen API (Izvori i pravila)
- vrijednosti između dva čitanja: API odgovara kad se pita i ne šalje sam; tabela rezultata se traži svake 2 s, događaji svake 0,5 s

**Veličina**: allgamedata je 15-40 KB (nosi cijelu listu događaja, koja raste) svake 2 s: oko 30-70 MB na sat u `raw.bin`; eventdata dodaje malo, jer se nepromijenjeni odgovori broje, a ne spremaju; zstd smanjuje ponovljeni JSON u `heat.raw.parquet` na nekoliko MB na sat (procjena iz dokumentiranog formata)

## Provjereno {#verified}

testirano prema lažnom lokalnom serveru koji služi odgovore u dokumentiranom formatu; nije testirano na igri

## Izvor {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
