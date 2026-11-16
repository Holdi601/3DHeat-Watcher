---
title: "VALORANT (replay-i)"
nav_order: 45
lang: "hr"
source: game-valorant-replays.md
source_hash: "10a648aabdf1"
nav_exclude: true
search_exclude: true
---
# VALORANT (replay-i) {#valorant-replays}

Nakon meča u VALORANT-u, watcher pretvara snimku koju je igra spremila u datoteke koje možete pogledati kao statistiku i vremensku crtu.

*Tehnički podaci: adapter `valorant-replays`, vrsta [`replay`](sources-and-rules.md); radi cijelo vrijeme (ne čeka da se igra pokrene) i traži nove podatke svakih 5 s.*

## Što se bilježi {#what-is-recorded}

- karta, ID meča i odabrani agenti; blok podataka snimke (duljina, verzije, naziv, vrijeme snimanja, zastavice sažimanja i šifriranja)
- vremenska crta događaja s servera: ubojstva (ubojica i žrtva kao ID-evi mreže), početak rundi, postavljene, deaktivirane i eksplodirane bombe, korištene ultimate sposobnosti, zamjene strana - svaki sa svojim ID-om i metapodacima
- svaki dio datoteke cijel u heat.raw.parquet; nije dekodirano: položaji, imena ili rezultati - oni su u zamagljenom toku

## Odakle dolaze {#where-it-comes-from}

snimke koje sprema VALORANT: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (samo dijelovi koji nisu zamagljeni)

## Kako ga uključiti {#how-to-switch-it-on}

spremite snimku u VALORANT-u (karijera > meč > preuzmi snimku)

## Kako radi {#how-it-works}

League of Legends i VALORANT snimke: što se od njih može pročitati kakvo jest.

Obje igre spremaju snimke na disk igrača, i obje štite ono što je unutra:
podaci igre od trenutka do trenutka zamagljeni su, i to drukčije sa svakom zakrpom,
da se ne bi mogli koristiti za varanje. Taj se dio nigdje u 3DHeat ne dekodira.
Čita se ono što svaka datoteka nosi otvoreno, a ostalo
se čuva kakvo jest: svaki dio datoteke, cijel, u sesijskoj datoteci
`heat.raw.parquet` (pravilo pretvarača 3DHeat, docs/converters.md u repozitoriju
preglednika), i broji se u `selfCheck.completeness` u meta.json-u.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, lokalna snimka Unreal Enginea
(raspored iz vrfkit-a, Apache-2.0, i ValorantReplayParser-a, MIT). U otvorenom
obliku: blok podataka snimke (duljina, verzija mreže, changelist, njezin naziv,
kad je snimljena, je li sažeta ili šifrirana), karta, ID meča i odabrani agenti
(u zaglavlju), te vlastita vremenska crta događaja servera - ubojstva (ubojica i
žrtva kao ID-evi mreže, ne imena), početak rundi, postavljene, deaktivirane i
eksplodirane bombe, korištene ultimate sposobnosti, zamjene strana - svaki sa
svojim vremenom, ID-om i metapodacima. Položaji, imena, rezultati i sve ostalo
nalazi se u zamagljenom toku (dijelovi s podacima snimke i kontrolnim točkama),
koji se čuva cijel i ne čita.

Isti modul služi i: [League of Legends (replay-i)](game-lol-replays.md).

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | ne |
| Os gore | `z` |
| Jedinice | svjetske jedinice VALORANT-a |
| Zrcaljenje za preglednik | nema |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovo ulazi u `meta.json` (`axes`) svake sesije i, kad sesija ima položaje, u podnožje `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira retke - pogledajte [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `replay`: čita samo ono što igra ili platforma predaje (snimke i demo zapise koje igra sprema), pa bilježi i u igri na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri vrste `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - pogledajte [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Što se bilježi" gore ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeat-a: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je ujedno postalo retcima), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- blok podataka snimke, svako polje (meta.json `vrf`): verzija datoteke, prilagođene verzije, duljina, verzija mreže, changelist, naziv, zastavica uživo, vrijeme snimanja, zastavice sažetog i šifriranog, ključ kako je pohranjen
- dio zaglavlja: karta, ID meča i odabrani agenti (prepoznati prema svom obliku)
- svaki dio događaja: ID, grupa, metapodaci, vrijeme početka i kraja, a iz njegovih podataka naziv događaja, vrijeme u sekundama i brojevi prije njega (ID-evi mreže ubojice i žrtve) - jedan redak po događaju

**Čuva se sirovo**

- svaki dio cijel, redom u datoteci (`offset`), pa su dijelovi sama datoteka: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, `chunk <n>` za vrstu koju raspored ne imenuje, `trailing` za bajte nakon zadnjeg cijelog dijela

**Nije dostupno**

- položaji, imena, rezultati, sposobnosti, svaki okvir igre: podaci snimke i dijelovi kontrolnih točaka su zamagljeni. Čuva se cijelo, ne čita se
- sadržaj šifrirane snimke: prolazi se i čuva cijela, ništa se ne čita unutra

**Veličina**: sirovi pomoćni dio je otprilike veličine same snimke: zamagljeni tok se ne sažima

## Provjereno {#verified}

izgrađeno prema rasporedu kontejnera koji dokumentira vrfkit (Apache-2.0); nije testirano na pravoj snimci, nijedna nije bila dostupna - provjere prije čitanja i preskače ono što se ne podudara

## Izvor {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i ponovno ga pokrenite umjesto uređivanja ove stranice. -->
