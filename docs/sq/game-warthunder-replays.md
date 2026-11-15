---
title: "War Thunder (riprodhime)"
nav_order: 45
lang: "sq"
source: game-warthunder-replays.md
source_hash: "23676a6c5441"
nav_exclude: true
search_exclude: true
---
# War Thunder (riprodhime) {#war-thunder-replays}

Pas një ndeshjeje në War Thunder, watcher-i e kthen riprodhimin që ruajti loja në skedarë që mund t'i shohësh në një hartë në shikuesin 3DHeat.

*Detaje teknike: adapteri `warthunder-replays`, lloji [`replay`](sources-and-rules.md); punon gjithë kohën (nuk pret të nisë një lojë) dhe kërkon të dhëna të reja çdo 5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni dhe qëndrimi i çdo avioni rreth 4 herë në sekondë (aq sa mban riprodhimi)
- pozicionet e njësive tokësore nga sinkronizimi tokësor i riprodhimit (në riprodhimet e 2026; jo në ato të 2025)
- kush ishte çdo njësi (lojtari, id e mjetit, ekipi) aty ku një vrasje ose goditje e emërton; vrasjet, vdekjet dhe goditjet aty ku ndodhën; biseda; harta
- vrasjet, vdekjet, pikët dhe kapjet e pikave të autorit të riprodhimit si statistika

## Nga vjen {#where-it-comes-from}

riprodhimet që ruan War Thunder: &lt;War Thunder>/Replays/\*.wrpl (me ruajtjen e riprodhimeve të ndezur), të konvertuara nga konverteri i jashtëm `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## Si ta ndezësh {#how-to-switch-it-on}

ndiz ruajtjen e riprodhimeve te opsionet e War Thunder dhe instalo konverterin: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Cilësimet nga variablat e mjedisit:

- `HEAT3D_WT_REPLAY`: dosja e konverterit (një klon ose një version i çpaketuar), kur nuk është i instaluar ose pranë watcher-it

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

#### War Thunder {#war-thunder}

War Thunder ruan një riprodhim të çdo beteje te `<War Thunder>/Replays/*.wrpl`
kur ruajtja e riprodhimeve është e ndezur te opsionet e saj. Watcher-i nuk i lexon
vetë: i lexon një konverter i jashtëm (konverteri i riprodhimeve War Thunder i 3DHeat,
`exporters/ext/warthunder-replay`, komanda `heat3d-wt-replay`), mbajtur i ndarë që
një problem me të të mos prekë asgjë tjetër. Kur komanda është në PATH, ose
paketa është e instaluar ose pranë watcher-it, çdo riprodhim i ri kalon përmes saj
drejt dosjes së sesionit si `<map>/<match>.parquet` dhe `<match>.match.json`;
kur nuk është, watcher-i thotë një herë si ta instalosh dhe e lë dosjen
në qetësi. Çfarë lexon konverteri, dhe çfarë jo, është në README të tij. Rreshti
i rezultateve të autorit të riprodhimit - vrasjet, vrasjet tokësore, vdekjet, ndihmat,
pikët, kapjet e pikave - bëhet statistikat e sesionit.

I njëjti modul shërben edhe: [Counter-Strike 2 (riprodhime)](game-cs2-demos.md), [Dota 2 (riprodhime)](game-dota-replays.md), [Squad (riprodhime)](game-squad-demos.md), [World of Tanks (riprodhime)](game-wot-replays.md), [World of Warships (riprodhime)](game-wows-replays.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `y` |
| Njësitë | metra (x lindje, y lart, z veri) |
| E pasqyruar për shikuesin | `z` |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë në `meta.json` të çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, në fundin e `heat.parquet`, që shikuesi 3DHeat t'i rrotullojë dhe shkallëzojë rreshtat vetë - shih [Të dhënat](the-data.md).

## Shumë lojtarë {#multiplayer}

- Shënuar si e luajtur në internet (`multiplayer`): **po**. `games --markdown` e shfaq si "allowed (reads only what the game publishes)".
- Lloji `replay`: lexon vetëm atë që loja ose platforma jep (riprodhimet dhe demot që ruan loja), ndaj regjistron si në lojë në internet ashtu edhe jashtë saj; flamuri vendos vetëm nëse memoria mund të lexohet ndonjëherë.
- Memoria: **kurrë** nuk lexohet nga ky adapter. Vetëm adapterët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur në internet - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adapteri vendos me emër (`stats` e çdo sesioni në `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`map`

Një çelës në kllapa gjarpërore plotësohet gjatë ekzekutimit (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Konverteri që ekzekuton ky adapter ndjek [rregullin e konverterëve](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: ajo që mban riprodhimi lexohet ose ruhet, nuk hidhet kurrë - lexohet në tabelë dhe në dokumentin e ndeshjes, gjithçka tjetër ruhet e plotë në skedarë anësorë pranë tyre, e numëruar në `selfCheck.completeness` të dokumentit të ndeshjes. Dokumentacioni i vetë konverterit liston çfarë lexon, çfarë ruan të papërpunuar dhe çfarë nuk mund të lexojë.

## Verifikuar {#verified}

konverteri është kontrolluar me riprodhime publike nga disa versione të lojës (vrasjet dhe emrat përputhen me rezultatet) dhe me teste në riprodhime të ndërtuara; ky lidhës me teste me një komandë zëvendësuese

## Burimi {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
