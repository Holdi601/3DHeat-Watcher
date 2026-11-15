---
title: "VALORANT (riluajtje)"
nav_order: 44
lang: "sq"
source: game-valorant-replays.md
source_hash: "617e23a33a4c"
nav_exclude: true
search_exclude: true
---
# VALORANT (riluajtje) {#valorant-replays}

Pas një ndeshjeje VALORANT, watcher e kthen riluajtjen që ruajti loja në skedarë që mund t'i shohësh si statistika dhe vijë kohore.

*Detaje teknike: adaptori `valorant-replays`, lloji [`replay`](sources-and-rules.md); punon gjithë kohën (nuk pret që të nisë një lojë) dhe kërkon të dhëna të reja çdo 5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- harta, id e ndeshjes dhe agjentët e zgjedhur; blloku i informacionit të riluajtjes (gjatësia, versionet, emri, ora e regjistrimit, flamujt e kompresimit dhe enkriptimit)
- vija kohore e ngjarjeve të serverit: vrasjet (vrasësi dhe viktima si id rrjeti), raundet që nisin, spike-t e vendosura, çaktivizuara dhe që shpërthejnë, ultimate-t e përdorura, ndërrimet e anëve - secila me id dhe metadata të veta
- çdo chunk i skedarit i plotë te heat.raw.parquet; nuk dekodohet: pozicionet, emrat ose rezultatet - ato janë në rrjedhën e turbulluar

## Nga vjen {#where-it-comes-from}

riluajtjet që ruan VALORANT: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (vetëm pjesët që nuk janë të turbulluara)

## Si ta ndezësh {#how-to-switch-it-on}

ruaje një riluajtje te VALORANT (career > match > download replay) dhe instalo lexuesin: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`)

Cilësime nga ndryshoret e mjedisit:

- `HEAT3D_RIOT_REPLAYS`: dosja e lexuesit (një klon ose një version i shpaketuar), kur nuk është instaluar ose pranë watcher-it

## Si funksionon {#how-it-works}

Riluajtjet e League of Legends dhe Valorant: çfarë prej tyre mund të lexohet siç është.

Të dy lojërat i ruajnë riluajtjet në diskun e lojtarit, dhe të dyja e mbrojnë çfarë ka brenda:
të dhënat e lojës nga çasti në çast janë të turbulluara (obfuscated), dhe ndryshe me çdo patch,
që të mos përdoren për të mashtruar. Të kalosh përmes kësaj do të thotë ta çmontosh kodin
e vetë lojës, gjë që kushtet e Riot e ndalojnë (Terms of Service 3.1 dhe 7.1)
- prandaj nuk bëhet askund në 3DHeat. Çfarë mban çdo skedar të hapur
lexohet, dhe pjesa tjetër ruhet siç është: çdo pjesë e skedarit, e plotë, te
`heat.raw.parquet` i sesionit (rregulli i konvertuesit të 3DHeat, docs/converters.md në
depon e shikuesit), e numëruar te `selfCheck.completeness` i meta.json.

Watcher nuk i lexon vetë skedarët: i lexon një lexues i jashtëm (3DHeat
Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`,
komanda `heat3d-riot-replays`), i mbajtur veçmas që një problem me kushtet e Riot
të prekë vetëm atë lexues. Nëse gjendet në PATH, i instaluar, ose pranë watcher-it, ai
lexon çdo riluajtje të re; nëse mungon, watcher thotë një herë si ta instalosh. Çfarë
lexon ai, watcher e regjistron te sesioni; vijën kohore Match-V5 më poshtë
e merr vetë watcher, sepse nuk është në skedar.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, një riluajtje lokale e Unreal Engine. E hapur:
blloku i informacionit të riluajtjes (gjatësia, versioni i rrjetit, changelist, emri i saj, kur
u regjistrua, nëse është e kompresuar ose e enkriptuar), harta, id e ndeshjes dhe
agjentët e zgjedhur (te koka), dhe vija kohore e ngjarjeve të vetë serverit - vrasjet
(vrasësi dhe viktima si id rrjeti, jo emra), raundet që nisin, spike-t e vendosura,
çaktivizuara dhe që shpërthejnë, ultimate-t e përdorura, ndërrimet e anëve - secila me orën,
id dhe metadatat e veta. Pozicionet, emrat, rezultatet dhe gjithçka tjetër janë në
rrjedhën e turbulluar (chunk-et e të dhënave të riluajtjes dhe të checkpoint-it), që ruhet e plotë
dhe nuk lexohet.

Të njëjtin modul e përdor edhe: [League of Legends (riluajtje)](game-lol-replays.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | jo |
| Boshti lart | `z` |
| Njësitë | njësitë e botës së VALORANT |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `replay`: lexon vetëm atë që loja ose platforma e jep vetë (riluajtje dhe demo që loja i ruan), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- blloku i informacionit, çdo fushë (meta.json `vrf`): versioni i skedarit, versionet e personalizuara, gjatësia, versioni i rrjetit, changelist, emri, flamuri live, ora e regjistrimit, flamujt e kompresuar dhe të enkriptuar, çelësi siç ruhet
- chunk-u i kokës: harta, id e ndeshjes dhe agjentët e zgjedhur (gjetur sipas formës së tyre)
- çdo chunk ngjarjesh: id, grupi, metadata, ora e fillimit dhe e fundit, dhe nga të dhënat e tij emri i ngjarjes, ora e saj në sekonda dhe numrat para saj (id-të e rrjetit të vrasësit dhe viktimës) - një rresht për secilën

**Ruajtur të papërpunuara**

- çdo chunk i plotë, sipas radhës në skedar (`offset`), kështu që pjesët janë skedari: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, `chunk <n>` për një lloj që struktura nuk e emërton, `trailing` për bajtet pas chunk-ut të fundit të plotë

**Nuk ofrohet**

- pozicionet, emrat, rezultatet, aftësitë, çdo kuadër i lojës: chunk-et e të dhënave të riluajtjes dhe të checkpoint-it janë të turbulluara; leximi i tyre do të thotë ta çmontosh klientin, gjë që kushtet e Riot e ndalojnë. Ruhen të plota, nuk lexohen
- përmbajtja e një riluajtjeje të enkriptuar: kalohet dhe ruhet e plotë, nuk lexohet asgjë brenda

**Madhësia**: skedari anësor i papërpunuar është rreth madhësisë së vetë riluajtjes: rrjedha e turbulluar nuk kompresohet

## Verifikuar {#verified}

lexuesi (heat3d-riot-replays) është ndërtuar nga struktura e kontejnerit e dokumentuar nga vrfkit (Apache-2.0); i paprovuar me një riluajtje të vërtetë, nuk pati asnjë - kontrollon para se të lexojë dhe kalon çfarë nuk përputhet

## Burimi {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
