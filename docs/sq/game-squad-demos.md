---
title: "Squad (riprodhime)"
nav_order: 40
lang: "sq"
source: game-squad-demos.md
source_hash: "a908f7e6d9c3"
nav_exclude: true
search_exclude: true
---
# Squad (riprodhime) {#squad-replays}

Pas një ndeshjeje në Squad, watcher-i e kthen riprodhimin që ruajti loja në skedarë që mund t'i shohësh në një hartë në shikuesin 3DHeat.

*Detaje teknike: adapteri `squad-demos`, lloji [`replay`](sources-and-rules.md); punon gjithë kohën (nuk pret të nisë një lojë) dhe kërkon të dhëna të reja çdo 5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni, këndi i trupit (yaw) dhe shpejtësia e çdo lojtari sa herë që serveri e përsërit (deri në 8 herë në sekondë), në këmbë dhe në mjete tokësore
- emri, ekipi, fraksioni dhe skuadra e çdo lojtari, duke ndjekur ndërrimet e ekipit
- jo: lëvizja e helikopterëve, vrasjet dhe objektet e vendosura - shih README të lexuesit

## Nga vjen {#where-it-comes-from}

demot e serverit që Squad i regjistron me komandën e administratorit AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, të lexuara nga lexuesi i jashtëm `heat3d-squad-demo` (exporters/ext/squad-demo)

## Si ta ndezësh {#how-to-switch-it-on}

regjistro në server: jepi administratorit lejen `demos` te Admins.cfg, pastaj AdminDemoRec &lt;name> dhe AdminDemoStop në konsolën e lojës; kopjo demon këtu dhe instalo lexuesin: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Cilësimet nga variablat e mjedisit:

- `HEAT3D_SQUAD_DEMO`: dosja e konverterit (një klon ose një version i çpaketuar), kur nuk është i instaluar ose pranë watcher-it

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

#### Squad {#squad}

Serverët e dedikuar të Squad regjistrojnë një demo të ndeshjes kur një administrator me
lejen `demos` ekzekuton AdminDemoRec &lt;name> (dhe AdminDemoStop), te
`<server>/SquadGame/Saved/Demos/<name>.replay` - një riprodhim rrjeti i Unreal Engine
që mban atë që serveri ka përsëritur, përfshirë lëvizjen e çdo lojtari.
Watcher-i nuk i lexon vetë: i lexon një lexues i jashtëm (lexuesi i demove Squad i 3DHeat,
`exporters/ext/squad-demo`, komanda `heat3d-squad-demo`), mbajtur
i ndarë që një problem me të të mos prekë asgjë tjetër. Ai ekzekutohet për çdo demo
të re në dosjet ku shkruan një server lokal, ose në një dosje që e shtojnë cilësimet
për demot e kopjuara nga një server i marrë me qira, drejt dosjes së sesionit si
`<map>/<match>.parquet` dhe `<match>.match.json`. Shtresa (layer), harta, numri i
lojtarëve dhe kohëzgjatja e ndeshjes bëhen statistikat e sesionit.

I njëjti modul shërben edhe: [Counter-Strike 2 (riprodhime)](game-cs2-demos.md), [Dota 2 (riprodhime)](game-dota-replays.md), [War Thunder (riprodhime)](game-warthunder-replays.md), [World of Tanks (riprodhime)](game-wot-replays.md), [World of Warships (riprodhime)](game-wows-replays.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `z` |
| Njësitë | njësi Unreal (centimetra) |
| E pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë në `meta.json` të çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, në fundin e `heat.parquet`, që shikuesi 3DHeat t'i rrotullojë dhe shkallëzojë rreshtat vetë - shih [Të dhënat](the-data.md).

## Shumë lojtarë {#multiplayer}

- Shënuar si e luajtur në internet (`multiplayer`): **po**. `games --markdown` e shfaq si "allowed (reads only what the game publishes)".
- Lloji `replay`: lexon vetëm atë që loja ose platforma jep (riprodhimet dhe demot që ruan loja), ndaj regjistron si në lojë në internet ashtu edhe jashtë saj; flamuri vendos vetëm nëse memoria mund të lexohet ndonjëherë.
- Memoria: **kurrë** nuk lexohet nga ky adapter. Vetëm adapterët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur në internet - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adapteri vendos me emër (`stats` e çdo sesioni në `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

Një çelës në kllapa gjarpërore plotësohet gjatë ekzekutimit (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Konverteri që ekzekuton ky adapter ndjek [rregullin e konverterëve](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: ajo që mban riprodhimi lexohet ose ruhet, nuk hidhet kurrë - lexohet në tabelë dhe në dokumentin e ndeshjes, gjithçka tjetër ruhet e plotë në skedarë anësorë pranë tyre, e numëruar në `selfCheck.completeness` të dokumentit të ndeshjes. Dokumentacioni i vetë konverterit liston çfarë lexon, çfarë ruan të papërpunuar dhe çfarë nuk mund të lexojë.

## Verifikuar {#verified}

lexuesi është kontrolluar me demo publike serveri (lëvizja përputhet me shpejtësinë që mbart; ekipi i çdo rreshti përputhet me fraksionin e ushtarit të tij) dhe me teste në demo të ndërtuara; ky lidhës me teste me një komandë zëvendësuese

## Burimi {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
