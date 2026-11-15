---
title: "VALORANT (snimke)"
nav_order: 45
lang: "bs"
source: game-valorant-replays.md
source_hash: "10a648aabdf1"
nav_exclude: true
search_exclude: true
---
# VALORANT (snimke) {#valorant-replays}

Nakon meča u VALORANT-u, watcher pretvara snimku koju je igra sačuvala u datoteke koje možete pogledati kao statistiku i vremensku liniju.

*Tehnički detalji: adapter `valorant-replays`, vrsta [`replay`](sources-and-rules.md); radi stalno (ne čeka da se igra pokrene) i svakih 5 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- mapa, id meča i odabrani agenti; informacijski blok snimke (dužina, verzije, ime, vrijeme snimanja, oznake kompresije i šifriranja)
- serverova vremenska linija događaja: kills (ubica i žrtva kao mrežni id-ovi), počeci rundi, spike postavljen, deaktiviran i eksplodirao, korištene ultimate sposobnosti, zamjena strana - svaki sa svojim id-om i metapodacima
- svaki chunk datoteke čuva se cijel u heat.raw.parquet; nije dekodirano: položaji, imena ili rezultati - oni su u obfuskiranom toku

## Odakle dolazi {#where-it-comes-from}

snimke koje sprema VALORANT: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (samo dijelovi koji nisu obfuskirani)

## Kako ga uključiti {#how-to-switch-it-on}

sačuvajte snimku u VALORANT-u (career > match > download replay)

## Kako radi {#how-it-works}

Snimke League of Legends i Valorant: ono što se iz njih može pročitati takvo kakvo jest.

Obje igre spremaju snimke na igračev disk i obje štite ono što je unutra:
podaci igre iz trenutka u trenutak su obfuskirani, i to drugačije sa svakim patchem,
da se ne bi mogli koristiti za varanje. Probiti se kroz to znači rastaviti
vlastiti kod igre, što Riotovi uvjeti zabranjuju (Terms of Service 3.1 i 7.1)
- pa se ovdje ne radi. Čita se ono što svaka datoteka nosi otvoreno, a
ostatak se čuva takav kakav jest: svaki dio datoteke, cijel, u
`heat.raw.parquet` sesije (3DHeat-ovo pravilo konvertera, docs/converters.md u
repozitoriju preglednika), a broji se u `selfCheck.completeness` u meta.json.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, lokalna snimka Unreal Enginea
(raspored iz vrfkit, Apache-2.0, i ValorantReplayParser, MIT). Otvoreno je:
informacijski blok snimke (dužina, mrežna verzija, changelist, njeno ime, kad je
snimljena, je li komprimirana ili šifrovana), mapa, id meča i
odabrani agenti (u zaglavlju), te serverova vlastita vremenska linija događaja - kills
(ubica i žrtva kao mrežni id-ovi, ne imena), počeci rundi, spike postavljen,
deaktiviran i eksplodirao, korištene ultimate sposobnosti, zamjena strana - svaki sa svojim vremenom,
id-om i metapodacima. Položaji, imena, rezultati i sve ostalo nalaze se u
obfuskiranom toku (chunkovi podataka snimke i checkpointa), koji se čuva cijel
i ne čita.

Isti modul služi i za: [League of Legends (snimke)](game-lol-replays.md).

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | ne |
| Osa gore | `z` |
| Jedinice | svjetske jedinice VALORANT-a |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `replay`: čita samo ono što igra ili platforma daje (snimke i demo-e koje igra sprema), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- informacijski blok, svako polje (meta.json `vrf`): verzija datoteke, prilagođene verzije, dužina, mrežna verzija, changelist, ime, oznaka uživo, vrijeme snimanja, oznake kompresije i šifriranja, ključ kako je pohranjen
- chunk zaglavlja: mapa, id meča i odabrani agenti (traže se po svom obliku)
- svaki chunk događaja: id, grupa, metapodaci, vrijeme početka i kraja, i iz njegovih podataka ime događaja, njegovo vrijeme u sekundama i brojevi prije njega (mrežni id-ovi ubice i žrtve) - po jedan red

**Čuva se sirovo**

- svaki chunk cijel, redom u datoteci (`offset`), pa su dijelovi sama datoteka: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, `chunk <n>` za vrstu koju raspored ne imenuje, `trailing` za bajtove iza zadnjeg cijelog chunka

**Nije dostupno**

- položaji, imena, rezultati, sposobnosti, svaki frejm igre: chunkovi podataka snimke i checkpointa su obfuskirani; njihovo čitanje znači rastaviti klijent, što Riotovi uvjeti zabranjuju. Čuva se cijelo, ne čita se
- sadržaj šifrovane snimke: prolazi se i čuva cijela, unutra se ništa ne čita

**Veličina**: sirovi sidecar je otprilike veličine same snimke: obfuskirani tok se ne kompresuje

## Provjereno {#verified}

izgrađeno prema rasporedu kontejnera koji dokumentira vrfkit (Apache-2.0); nije testirano na pravoj snimci, nijedna nije bila dostupna - provjerava prije čitanja i preskače ono što se ne poklapa

## Izvor {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
