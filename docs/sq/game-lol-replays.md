---
title: "League of Legends (riluajtje)"
nav_order: 30
lang: "sq"
source: game-lol-replays.md
source_hash: "6a86dc8a45bb"
nav_exclude: true
search_exclude: true
---
# League of Legends (riluajtje) {#league-of-legends-replays}

Pas një ndeshjeje League of Legends, watcher e kthen riluajtjen që ruajti loja në skedarë që mund t'i shohësh në një hartë në shikuesin 3DHeat.

*Detaje teknike: adaptori `lol-replays`, lloji [`replay`](sources-and-rules.md); punon gjithë kohën (nuk pret që të nisë një lojë) dhe kërkon të dhëna të reja çdo 5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- kampioni, roli, ekipi, vrasjet, vdekjet, asistimet, ari, dëmi ndaj kampionëve dhe rezultati i çdo lojtari, dhe çdo numër tjetër i tabelës së rezultateve në fund të lojës
- rreshti yt si statistika, dhe rreshtat e tua të emërtuar si të tutët (meta.json `player`), me Riot ID-në tënde te cilësimet
- me çelësin tënd Riot API: pozicioni i çdo lojtari çdo minutë me statistikat e minutës, dhe çdo ngjarje e vijës kohore (vrasje aty ku ndodhën, ndërtesa, përbindësha, wards, sende, aftësi), në orën e murit që jep vija kohore
- çdo pjesë e skedarit të riluajtjes e plotë te heat.raw.parquet; nuk dekodohet: loja nga çasti në çast, që është e enkriptuar dhe e turbulluar kundër mashtrimit

## Nga vjen {#where-it-comes-from}

riluajtjet që ruan klienti League: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (vetëm metadata e thjeshtë e fundit të lojës); me çelësin tënd Riot API, vija zyrtare kohore e ndeshjes nga Match-V5 API i Riot

## Si ta ndezësh {#how-to-switch-it-on}

ruaje një riluajtje te klienti League (match history > download) dhe instalo lexuesin: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`); për pozicionet vendos riot_api_key dhe riot_platform me `config --set`

Cilësime nga ndryshoret e mjedisit:

- `HEAT3D_RIOT_REPLAYS`: dosja e lexuesit (një klon ose një version i shpaketuar), kur nuk është instaluar ose pranë watcher-it

## Si funksionon {#how-it-works}

Riluajtjet e League of Legends dhe Valorant: çfarë prej tyre mund të lexohet siç është.

Të dy lojërat i ruajnë riluajtjet në diskun e lojtarit, dhe të dyja e mbrojnë çfarë ka brenda:
të dhënat e lojës nga çasti në çast janë të turbulluara (obfuscated), dhe ndryshe me çdo patch,
që të mos përdoren për të mashtruar. Kjo pjesë nuk dekodohet askund në
3DHeat. Çfarë mban çdo skedar të hapur
lexohet, dhe pjesa tjetër ruhet siç është: çdo pjesë e skedarit, e plotë, te
`heat.raw.parquet` i sesionit (rregulli i konvertuesit të 3DHeat, docs/converters.md në
depon e shikuesit), e numëruar te `selfCheck.completeness` i meta.json.

Watcher nuk i lexon vetë skedarët: i lexon një lexues i jashtëm (3DHeat
Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`,
komanda `heat3d-riot-replays`), një projekt më vete. Nëse gjendet në PATH, i instaluar, ose pranë watcher-it, ai
lexon çdo riluajtje të re; nëse mungon, watcher thotë një herë si ta instalosh. Çfarë
lexon ai, watcher e regjistron te sesioni; vijën kohore Match-V5 më poshtë
e merr vetë watcher, sepse nuk është në skedar.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Të dy versionet e
kontejnerit mbajnë tabelën e rezultateve në fund të lojës si JSON të thjeshtë (`statsJson`): për çdo
nga dhjetë lojtarët kampionin, vrasjet, vdekjet, asistimet, arin, dëmin ndaj
kampionëve, sendet, ekipin, rolin, fitoren, Riot ID-në e tyre, dhe çdo numër tjetër që
loja e mbledh (mbi njëqind për lojtar); të gjithë bëhen rreshti `player_result` i lojtarit.
ROFL1 (patch 14.9 e më parë) e ka pas një koke fikse
(`RIOT\0\0`, një nënshkrim 256 bajte, pastaj gjatësitë); ROFL2 (nga 14.11,
`RIOT\2\0`) në fund të skedarit, gjatësia e tij në katër bajtet e fundit (thënë
nga një inxhinier i Riot, ReplayBook issue 299). Koka e payload-it të ROFL1 (id e lojës,
gjatësia, numri i chunk-eve dhe keyframe-ve, gjatësia e çelësit të chunk-ut) dhe tabela e tij
e chunk-eve (id, lloji, gjatësia, chunk-u tjetër, offset) janë të hapura dhe lexohen; chunk-et
vetë janë të enkriptuara, dhe ruhen të plota pa u lexuar.

Pozicionet nuk vijnë nga skedari. Me një çelës zhvillues Riot të vetë lojtarit
(`riot_api_key` te cilësimet; një çelës personal është menduar pikërisht për këtë,
"showing (self) player stats"), vija zyrtare kohore e ndeshjes merret nga
Match-V5 API i Riot: pozicioni i çdo lojtari një herë në minutë me gjithçka që kuadri i
minutës thotë për ta (ari, përvoja, niveli, minionët, statistikat e kampionit dhe të dëmit),
dhe çdo ngjarje e vijës kohore - vrasje, ndërtesa, përbindësha elitë, wards, sende, aftësi, nivele -
secila një rresht, aty ku ndodhi kur ka vend. Pa çelës nuk merret asgjë dhe nuk dërgohet asgjë.

Të njëjtin modul e përdor edhe: [VALORANT (riluajtje)](game-valorant-replays.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `y` |
| Njësitë | njësitë e hartës Summoner's Rift (rreth 15000 në gjerësi) |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `replay`: lexon vetëm atë që loja ose platforma e jep vetë (riluajtje dhe demo që loja i ruan), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- JSON i metadatave: gjatësia e lojës, versioni, id-të e chunk-ut dhe keyframe-it të fundit, dhe `statsJson` - çdo fushë e tabelës së rezultateve të çdo lojtari te rreshti i tij `player_result` (numrat e dhënë si tekst lexohen si numra)
- ROFL1: blloku i gjatësive, koka e payload-it (id e lojës, gjatësia e lojës, numri i keyframe-ve dhe chunk-eve, id-të e chunk-ut të nisjes dhe të fillimit të lojës, intervali i keyframe-ve, çelësi i chunk-ut siç ruhet) dhe tabela e chunk-eve (id, lloji, gjatësia, chunk-u tjetër, offset) - te `rofl` i meta.json dhe te `text` i rreshtave të papërpunuar
- ROFL2: vargu i versionit
- vija kohore Match-V5 (vetëm me çelësin tënd API): çdo kuadër pjesëmarrësi te një rresht `position` (ose `participant_frame` pa vend) me të gjitha fushat e sheshuara (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); çdo ngjarje si rresht me emrin e llojit të vet, vendosur aty ku ka `position`, CHAMPION_KILL si vrasje dhe si vdekje

**Ruajtur të papërpunuara**

- çdo pjesë e .rofl, e plotë, sipas radhës në skedar (`offset`), kështu që pjesët janë skedari: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); çdo copë që asnjë pjesë nuk e mbulon si `unknown`
- vija kohore e plotë: `timeline <type>` për çdo ngjarje, `timeline participantFrame` për kuadrin e çdo lojtari (`participant` id e tij), `timeline` për pjesën tjetër

**Nuk ofrohet**

- vetë loja (pozicionet, aftësitë, çdo njësi, çast pas çasti): chunk-et e ROFL1 dhe trupi i ROFL2 janë të enkriptuar dhe paketat brenda të turbulluara me çdo patch. Ruhen të plota, nuk lexohen
- pozicionet pa çelësin tënd Riot API: skedari nuk ka asnjë të hapur

**Madhësia**: skedari anësor i papërpunuar është rreth madhësisë së vetë riluajtjes: chunk-et e enkriptuara nuk kompresohen

## Verifikuar {#verified}

lexuesi (heat3d-riot-replays) u provua me skedarë të ndërtuar sipas strukturave në roflxd.cs (MIT); vija kohore me JSON-in e dokumentuar të Match-V5; nuk pati asnjë riluajtje të vërtetë për të kontrolluar

## Burimi {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
