---
title: "League of Legends (replay-i)"
nav_order: 30
lang: "hr"
source: game-lol-replays.md
source_hash: "216b88922360"
nav_exclude: true
search_exclude: true
---
# League of Legends (replay-i) {#league-of-legends-replays}

Nakon meča u League of Legends, watcher pretvara snimku koju je klijent spremio u datoteke koje možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `lol-replays`, vrsta [`replay`](sources-and-rules.md); radi cijelo vrijeme (ne čeka da se igra pokrene) i traži nove podatke svakih 5 s.*

## Što se bilježi {#what-is-recorded}

- svaki igrač: šampion, uloga, tim, ubojstva, smrti, asistencije, zlato, šteta šampionima i ishod, te svaki ostali broj iz tablice rezultata na kraju igre
- vaš vlastiti redak kao statistika, a vaši retci označeni kao vaši (meta.json `player`), uz vaš Riot ID u postavkama
- uz vaš vlastiti ključ Riot API-ja: položaj svakog igrača svake minute sa statistikom te minute i svaki događaj iz vremenske crte (ubojstva gdje su se dogodila, zgrade, čudovišta, stražarska mjesta, predmeti, vještine), u vrijeme na satu koje daje vremenska crta
- svaki dio datoteke snimke cijel u heat.raw.parquet; nije dekodirano: tijek igre od trenutka do trenutka, koji je šifriran i zamagljen protiv varanja

## Odakle dolaze {#where-it-comes-from}

snimke koje sprema League klijent: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (samo jednostavni metapodaci kraja igre); uz vaš ključ Riot API-ja, službena vremenska crta meča iz Riotovog Match-V5 API-ja

## Kako ga uključiti {#how-to-switch-it-on}

spremite snimku u League klijentu (povijest mečeva > preuzmi); za položaje postavite riot_api_key i riot_platform naredbom `config --set`

## Kako radi {#how-it-works}

League of Legends i VALORANT snimke: što se od njih može pročitati kakvo jest.

Obje igre spremaju snimke na disk igrača, i obje štite ono što je unutra:
podaci igre od trenutka do trenutka zamagljeni su, i to drukčije sa svakom zakrpom, da se ne bi mogli koristiti za varanje. Taj se dio nigdje u 3DHeat ne dekodira.
Čita se ono što svaka datoteka nosi otvoreno, a ostalo
se čuva kakvo jest: svaki dio datoteke, cijel, u sesijskoj datoteci
`heat.raw.parquet` (pravilo pretvarača 3DHeat, docs/converters.md u repozitoriju
preglednika), i broji se u `selfCheck.completeness` u meta.json-u.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Obje verzije kontejnera
nose tablicu rezultata sa kraja igre kao običan JSON (`statsJson`): za svakog od
deset igrača šampion, ubojstva, smrti, asistencije, zlato, šteta šampionima,
predmeti, tim, uloga, pobjeda, njihov Riot ID i svaki ostali broj koji igra zbraja
(preko stotinu po igraču); svi postaju retkom `player_result` tog igrača. ROFL1
(zakrpa 14.9 i ranije) ga ima nakon fiksnog zaglavlja (`RIOT\0\0`, potpis od 256
bajta, pa duljine); ROFL2 (14.11 nadalje, `RIOT\2\0`) na kraju datoteke, njezina
duljina u zadnja četiri bajta (navodi Riotov inženjer, ReplayBook issue 299).
Zaglavlje korisnog tereta ROFL1 (ID igre, duljina, broj dijelova i ključnih okvira,
duljina ključa dijela) i njegova tablica dijelova (ID, vrsta, duljina, sljedeći dio,
pomak) su otvoreni i čitaju se; sami dijelovi su šifrirani, pa se čuvaju cijeli
nepročitani. Rasporedi iz roflxd.cs (MIT).

Položaji ne dolaze iz datoteke. Uz Riot developer ključ samog igrača (`riot_api_key`
u postavkama; osobni ključ namijenjen je upravo tome, "prikazivanju (vlastite)
statistike igrača"), službena vremenska crta meča dohvaća se iz Riotovog Match-V5
API-ja: položaj svakog igrača jednom u minuti sa svim što okvir te minute kaže o
njima (zlato, iskustvo, razina, minioni, statistika šampiona i štete), te svaki
događaj vremenske crte - ubojstva, zgrade, elitna čudovišta, stražarska mjesta,
predmeti, vještine, razine - svaki kao redak, gdje se dogodio kad ima mjesto.
Bez ključa se ništa ne dohvaća i ništa ne šalje.

Isti modul služi i: [VALORANT (replay-i)](game-valorant-replays.md).

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Os gore | `y` |
| Jedinice | jedinice karte Summoner's Rift (oko 15000 od ruba do ruba) |
| Zrcaljenje za preglednik | nema |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovo ulazi u `meta.json` (`axes`) svake sesije i, kad sesija ima položaje, u podnožje `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira retke - pogledajte [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `replay`: čita samo ono što igra ili platforma predaje (snimke i demo zapise koje igra sprema), pa bilježi i u igri na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri vrste `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - pogledajte [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Što se bilježi" gore ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeat-a: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je ujedno postalo retcima), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- JSON metapodataka: duljina igre, verzija, ID-evi zadnjeg dijela i ključnog okvira, i `statsJson` - svako polje tablice rezultata svakog igrača na njegovom retku `player_result` (brojevi zapisani kao tekst čitaju se kao brojevi)
- ROFL1: blok duljina, zaglavlje korisnog tereta (ID igre, duljina igre, broj ključnih okvira i dijelova, ID-evi početnog dijela i početka igre, interval ključnih okvira, ključ dijela kako je pohranjen) i tablica dijelova (ID, vrsta, duljina, sljedeći dio, pomak) - u meta.json pod `rofl` i u `text` sirovih redaka
- ROFL2: niz verzije
- vremenska crta Match-V5 (samo uz vlastiti API ključ): svaki okvir sudionika na retku `position` (ili `participant_frame` bez mjesta) sa svim svojim poljima izravnanim (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); svaki događaj kao redak nazvan prema svojoj vrsti, smješten tamo gdje ima `position`, CHAMPION_KILL kao ubojstvo i smrt

**Čuva se sirovo**

- svaki dio .rofl-a cijel, redom u datoteci (`offset`), pa su dijelovi sama datoteka: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); svaki dio koji nijedan dio ne pokriva kao `unknown`
- vremenska crta cijela: `timeline <type>` za svaki događaj, `timeline participantFrame` za okvir svakog igrača (`participant` njegov ID), `timeline` za ostalo

**Nije dostupno**

- sama igra (položaji, sposobnosti, svaka jedinica, od trenutka do trenutka): dijelovi ROFL1 i tijelo ROFL2 su šifrirani, a paketi unutra zamagljeni sa svakom zakrpom. Čuva se cijelo, ne čita se
- položaji bez vašeg vlastitog Riot API ključa: datoteka ih u otvorenom obliku nema

**Veličina**: sirovi pomoćni dio je otprilike veličine same snimke: šifrirani dijelovi se ne sažimaju

## Provjereno {#verified}

čitač metapodataka testiran na datotekama izgrađenima prema rasporedima iz roflxd.cs (MIT); vremenska crta prema dokumentiranom JSON-u Match-V5; nije bilo prave snimke za provjeru

## Izvor {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i ponovno ga pokrenite umjesto uređivanja ove stranice. -->
