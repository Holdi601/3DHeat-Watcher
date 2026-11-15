---
title: "Counter-Strike 2 (riprodhime)"
nav_order: 8
lang: "sq"
source: game-cs2-demos.md
source_hash: "82fe00f0f2f0"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (riprodhime) {#counter-strike-2-replays}

Pas një ndeshjeje në Counter-Strike 2, watcher-i e kthen riprodhimin që ruajti loja në skedarë që mund t'i shohësh në një hartë në shikuesin 3DHeat.

*Detaje teknike: adapteri `cs2-demos`, lloji [`replay`](sources-and-rules.md); punon gjithë kohën (nuk pret të nisë një lojë) dhe kërkon të dhëna të reja çdo 5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni, drejtimi i shikimit, shëndeti dhe paratë e çdo lojtari (çdo tik i 8-të)
- vrasjet, vdekjet, dëmi, granatat, vendosjet dhe çaktivizimet e bombës aty ku ndodhën
- raundet, rezultati, ekonomia; rreshti i tabelës së rezultateve për lojtarin e kyçur si statistika

## Nga vjen {#where-it-comes-from}

demot që ruan CS2: &lt;CS2>/game/csgo/replays/\*.dem (shkarkuar nga historiku i ndeshjeve) dhe &lt;CS2>/game/csgo/\*.dem (të regjistruara)

## Si ta ndezësh {#how-to-switch-it-on}

shkarko demon e një ndeshjeje në CS2 (Watch > Your Matches), ose regjistro një me `record` në konsolë

Cilësimet nga variablat e mjedisit:

- `HEAT3D_CS2`: dosja e 3DHeat CS2, kur nuk është pranë watcher-it ose e instaluar

## Si funksionon {#how-it-works}

Riprodhimet dhe demot: ajo që një lojë ruan nga një ndeshje, e konvertuar një herë kur ndeshja mbaron.

Një riprodhim mban gjithçka që një ndërfaqe e drejtpërdrejtë e mban të fshehur në
lojërat me shumë lojtarë - pozicionin e çdo lojtari, çdo vrasje aty ku ndodhi - dhe është një skedar që
loja e shkruan për lojtarët e saj, ndaj leximi i tij nuk prek asgjë në lojë. Watcher-i
shikon dosjet ku lojërat i ruajnë, pret derisa një skedar i ri
të mos rritet më (përndryshe loja ende po e shkruan) dhe e konverton në një
fije pune, që një konvertim i gjatë të mos e ngadalësojë pjesën tjetër të watcher-it.

Herën e parë që shihet një dosje, riprodhimet që janë tashmë aty vetëm shënohen, nuk
konvertohen: një lojtar me vite demo do ta gjente watcher-in të zënë
për një ditë të tërë. `python -m heat3d_watch replays <adapter> [folder]` i konverton
ato ekzistueset sipas kërkesës.

#### Counter-Strike 2 {#counter-strike-2}

CS2 i ruan demot që një lojtar i shkarkon nga historiku i ndeshjeve (skeda Watch) te
`<CS2>/game/csgo/replays/` dhe ato të regjistruara me komandën e konsolës `record`
te `<CS2>/game/csgo/`. Secila konvertohet me konverterin CS2 të këtij depoje
(3DHeat CS2, github.com/Holdi601/3DHeat-CS2: pozicioni, drejtimi i shikimit, shëndeti dhe
paratë e çdo lojtari çdo tik të tetë; vrasjet, vdekjet, dëmi, granatat, vendosjet dhe çaktivizimet e bombës
aty ku ndodhën; raundet, rezultati, ekonomia) në dosjen e sesionit, si tabela
`<map>/<match>.parquet` dhe përmbledhja `<match>.match.json` që skedat e nxehtësisë
dhe të ndeshjes të shikuesit i lexojnë. Tabela e rezultateve e ndeshjes bëhet statistikat e sesionit:
për lojtarin llogaria Steam e të cilit është e kyçur në këtë kompjuter (nga
`loginusers.vdf` i Steam) me emrat e tyre të thjeshtë - vrasje, vdekje, ndihma, ADR, KAST,
përqindja e goditjeve në kokë, vrasjet e para, clutch-et - si dhe rezultati dhe raundet.

I njëjti modul shërben edhe: [Dota 2 (riprodhime)](game-dota-replays.md), [Squad (riprodhime)](game-squad-demos.md), [War Thunder (riprodhime)](game-warthunder-replays.md), [World of Tanks (riprodhime)](game-wot-replays.md), [World of Warships (riprodhime)](game-wows-replays.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `z` |
| Njësitë | inç (njësi Source) |
| E pasqyruar për shikuesin | `y` |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë në `meta.json` të çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, në fundin e `heat.parquet`, që shikuesi 3DHeat t'i rrotullojë dhe shkallëzojë rreshtat vetë - shih [Të dhënat](the-data.md).

## Shumë lojtarë {#multiplayer}

- Shënuar si e luajtur në internet (`multiplayer`): **po**. `games --markdown` e shfaq si "allowed (reads only what the game publishes)".
- Lloji `replay`: lexon vetëm atë që loja ose platforma jep (riprodhimet dhe demot që ruan loja), ndaj regjistron si në lojë në internet ashtu edhe jashtë saj; flamuri vendos vetëm nëse memoria mund të lexohet ndonjëherë.
- Memoria: **kurrë** nuk lexohet nga ky adapter. Vetëm adapterët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur në internet - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adapteri vendos me emër (`stats` e çdo sesioni në `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

Një çelës në kllapa gjarpërore plotësohet gjatë ekzekutimit (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Konverteri që ekzekuton ky adapter ndjek [rregullin e konverterëve](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: ajo që mban riprodhimi lexohet ose ruhet, nuk hidhet kurrë - lexohet në tabelë dhe në dokumentin e ndeshjes, gjithçka tjetër ruhet e plotë në skedarë anësorë pranë tyre, e numëruar në `selfCheck.completeness` të dokumentit të ndeshjes. Dokumentacioni i vetë konverterit liston çfarë lexon, çfarë ruan të papërpunuar dhe çfarë nuk mund të lexojë.

## Verifikuar {#verified}

konverteri është testuar me demo reale turneu; vëzhgimi i dosjes dhe statistikat me teste

## Burimi {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
