---
title: "League of Legends (snimke)"
nav_order: 30
lang: "bs"
source: game-lol-replays.md
source_hash: "216b88922360"
nav_exclude: true
search_exclude: true
---
# League of Legends (snimke) {#league-of-legends-replays}

Nakon meča u League of Legends, watcher pretvara snimku koju je igra sačuvala u datoteke koje možete pogledati na mapi u preglednik 3DHeat-u.

*Tehnički detalji: adapter `lol-replays`, vrsta [`replay`](sources-and-rules.md); radi stalno (ne čeka da se igra pokrene) i svakih 5 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- šampion, uloga, tim, kills, deaths, assists, zlato, šteta šampionima i rezultat svakog igrača, te svaki drugi broj iz tabele rezultata na kraju igre
- vaša vlastita linija kao statistika, a vaši redovi imenovani kao vaši (meta.json `player`), uz vaš Riot ID u postavkama
- s vašim vlastitim Riot API ključem: položaj svakog igrača svake minute sa statistikom te minute, i svaki događaj vremenske linije (kills tamo gdje su se desili, građevine, čudovišta, wards, predmeti, vještine), u stvarnom vremenu koje vremenska linija daje
- svaki dio datoteke snimke čuva se cijel u heat.raw.parquet; nije dekodirano: igra iz trenutka u trenutak, koja je šifrovana i obfuskirana protiv varanja

## Odakle dolazi {#where-it-comes-from}

snimke koje sprema League klijent: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (samo obični metapodaci s kraja igre); s vašim vlastitim Riot API ključem, službena vremenska linija meča iz Riotovog Match-V5 API-ja

## Kako ga uključiti {#how-to-switch-it-on}

sačuvajte snimku u League klijentu (historija mečeva > preuzmite); za položaje postavite riot_api_key i riot_platform pomoću `config --set`

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

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Obje verzije
kontejnera nose tabelu rezultata s kraja igre kao običan JSON (`statsJson`): za svakog
od deset igrača šampiona, kills, deaths, assists, zlato, štetu
šampionima, predmete, tim, ulogu, pobjedu, njegov Riot ID, i svaki drugi broj koji
igra zbraja (preko stotinu po igraču); svi oni postaju igračev
red `player_result`. ROFL1 (patch 14.9 i ranije) ga ima iza fiksnog zaglavlja
(`RIOT\0\0`, potpis od 256 bajta, pa dužine); ROFL2 (od 14.11,
`RIOT\2\0`) na kraju datoteke, a njegova dužina je u zadnja četiri bajta (navodi
Riotov inženjer, ReplayBook issue 299). Zaglavlje payload-a ROFL1 (id igre,
dužina, brojevi chunkova i keyframeova, dužina ključa chunka) i njegova tabela
chunkova (id, vrsta, dužina, sljedeći chunk, pomak) su otvoreni i čitaju se; sami
chunkovi su šifrovani i čuvaju se cijeli, nepročitani. Rasporedite iz
roflxd.cs (MIT).

Položaji ne dolaze iz datoteke. Uz Riotov developerski ključ koji igrač ima
sam (`riot_api_key` u postavkama; lični ključ je namijenjen upravo za ovo,
"showing (self) player stats"), službena vremenska linija meča se dohvata iz
Riotovog Match-V5 API-ja: položaj svakog igrača jednom u minuti sa svim što
okvir te minute kaže o njemu (zlato, iskustvo, nivo, minioni, statistika šampiona i
štete), i svaki događaj vremenske linije - kills, građevine, elitna
čudovišta, wards, predmeti, vještine, nivoi - svaki kao red, tamo gdje se desio kad
ima mjesto. Bez ključa se ništa ne dohvata i ništa ne šalje.

Isti modul služi i za: [VALORANT (snimke)](game-valorant-replays.md).

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Osa gore | `y` |
| Jedinice | jedinice mape Summoner's Rift (oko 15000 u širinu) |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `replay`: čita samo ono što igra ili platforma daje (snimke i demo-e koje igra sprema), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- JSON s metapodacima: dužina igre, verzija, id-ovi zadnjeg chunka i keyframea, i `statsJson` - svako polje tabele rezultata svakog igrača na njegovom redu `player_result` (brojevi dati kao tekst čitaju se kao brojevi)
- ROFL1: blok dužina, zaglavlje payload-a (id igre, dužina igre, brojevi keyframeova i chunkova, id-ovi chunkova pokretanja i početka igre, interval keyframea, ključ chunka onako kako je pohranjen) i tabela chunkova (id, vrsta, dužina, sljedeći chunk, pomak) - u meta.json `rofl` i u `text` sirovih redova
- ROFL2: niz verzije
- vremenska linija Match-V5 (samo s vlastitim API ključem): svaki okvir učesnika na redu `position` (ili `participant_frame` bez mjesta) sa svim njegovim poljima spljoštenim (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); svaki događaj kao red nazvan po svojoj vrsti, smješten tamo gdje ima `position`, a CHAMPION_KILL kao kill i death

**Čuva se sirovo**

- svaki dio .rofl-a, cijel, redom u datoteci (`offset`), pa su dijelovi sama datoteka: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); svaki odsječak koji nijedan dio ne pokriva kao `unknown`
- vremenska linija cijela: `timeline <type>` za svaki događaj, `timeline participantFrame` za okvir svakog igrača (`participant` je njegov id), `timeline` za ostalo

**Nije dostupno**

- sama igra (položaji, sposobnosti, svaka jedinica, iz trenutka u trenutak): chunkovi ROFL1 i tijelo ROFL2 su šifrovani, a paketi unutra obfuskirani sa svakim patchem; probiti se znači rastaviti klijent, što Riotovi uvjeti zabranjuju (3.1, 7.1). Čuva se cijelo, ne čita se
- položaji bez vašeg vlastitog Riot API ključa: datoteka ih nema otvorene

**Veličina**: sirovi sidecar je otprilike veličine same snimke: šifrovani chunkovi se ne kompresuju

## Provjereno {#verified}

čitač metapodataka testiran na datotekama izgrađenim prema rasporedima iz roflxd.cs (MIT); vremenska linija na dokumentiranom JSON-u Match-V5; nije bilo prave snimke za provjeru

## Izvor {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
