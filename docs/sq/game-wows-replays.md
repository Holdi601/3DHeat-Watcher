---
title: "World of Warships (riprodhime)"
nav_order: 48
lang: "sq"
source: game-wows-replays.md
source_hash: "e7d24a56747e"
nav_exclude: true
search_exclude: true
---
# World of Warships (riprodhime) {#world-of-warships-replays}

Pas një ndeshjeje në World of Warships, watcher-i e kthen riprodhimin që ruajti loja në skedarë që mund t'i shohësh në një hartë në shikuesin 3DHeat.

*Detaje teknike: adapteri `wows-replays`, lloji [`replay`](sources-and-rules.md); punon gjithë kohën (nuk pret të nisë një lojë) dhe kërkon të dhëna të reja çdo 5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni dhe drejtimi i çdo anijeje për sa kohë e pa klienti që regjistronte (rreth 6 deri 7 herë në sekondë gjatë lëvizjes), anija e vetë lojtarit gjatë gjithë kohës
- lojtari, aleat ose kundërshtar, dhe anija (e lojtarit që regjistroi me emër, të tjerat me numrin e anijes në lojë); anijet e fundosura aty ku u fundosën dhe vrasësit e tyre aty ku qëndronin
- harta; anija, vrasjet dhe mbijetesa e lojtarit që regjistroi si statistika

## Nga vjen {#where-it-comes-from}

riprodhimet që ruan World of Warships: &lt;World of Warships>/replays/\*.wowsreplay (me riprodhimet e ndezura), të konvertuara nga konverteri i jashtëm `heat3d-wows-replay` (exporters/ext/wows-replay)

## Si ta ndezësh {#how-to-switch-it-on}

ndiz regjistrimin e riprodhimeve në World of Warships (`isReplayEnabled` te preferences.xml i tij, ose cilësimi i vetë lojës ku ka një) dhe instalo konverterin: pip install -e &lt;3DHeat>/exporters/ext/wows-replay

Cilësimet nga variablat e mjedisit:

- `HEAT3D_WOWS_REPLAY`: dosja e konverterit (një klon ose një version i çpaketuar), kur nuk është i instaluar ose pranë watcher-it

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

#### World of Tanks dhe World of Warships {#world-of-tanks-and-world-of-warships}

Të dyja ruajnë një riprodhim të çdo beteje te `<game>/replays/` kur regjistrimi është i ndezur
(`*.wotreplay`, `*.wowsreplay`); instalimet gjenden përmes listës së Wargaming
Game Center, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, dhe
Steam. Si me War Thunder, watcher-i nuk i lexon vetë skedarët: i lexon një
konverter i jashtëm për secilën (`exporters/ext/wot-replay`, komanda
`heat3d-wot-replay`; `exporters/ext/wows-replay`, komanda
`heat3d-wows-replay`), secili një projekt më vete. Kur gjendet në PATH, i instaluar, ose pranë watcher-it,
çdo riprodhim i ri kthehet në `<map>/<match>.parquet` dhe `<match>.match.json`
në dosjen e sesionit; kur mungon, watcher-i thotë një herë si ta instalosh. Rreshti
i lojtarit që regjistroi - mjeti ose anija, vrasjet, dëmi (World of Tanks),
nëse mbijetoi, dhe rezultati (World of Tanks) - bëhet statistikat e
sesionit. Çfarë lexon çdo konverter, dhe çfarë jo, është në README të tij.

I njëjti modul shërben edhe: [Counter-Strike 2 (riprodhime)](game-cs2-demos.md), [Dota 2 (riprodhime)](game-dota-replays.md), [Squad (riprodhime)](game-squad-demos.md), [War Thunder (riprodhime)](game-warthunder-replays.md), [World of Tanks (riprodhime)](game-wot-replays.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `y` |
| Njësitë | njësitë e botës së World of Warships (x lindje, y lart, z veri; një është 15 m sipas gjeometrisë së bykut, 30 m sipas rrezeve të lojës) |
| E pasqyruar për shikuesin | `z` |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë në `meta.json` të çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, në fundin e `heat.parquet`, që shikuesi 3DHeat t'i rrotullojë dhe shkallëzojë rreshtat vetë - shih [Të dhënat](the-data.md).

## Shumë lojtarë {#multiplayer}

- Shënuar si e luajtur në internet (`multiplayer`): **po**. `games --markdown` e shfaq si "allowed (reads only what the game publishes)".
- Lloji `replay`: lexon vetëm atë që loja ose platforma jep (riprodhimet dhe demot që ruan loja), ndaj regjistron si në lojë në internet ashtu edhe jashtë saj; flamuri vendos vetëm nëse memoria mund të lexohet ndonjëherë.
- Memoria: **kurrë** nuk lexohet nga ky adapter. Vetëm adapterët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur në internet - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adapteri vendos me emër (`stats` e çdo sesioni në `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

Një çelës në kllapa gjarpërore plotësohet gjatë ekzekutimit (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Konverteri që ekzekuton ky adapter ndjek [rregullin e konverterëve](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: ajo që mban riprodhimi lexohet ose ruhet, nuk hidhet kurrë - lexohet në tabelë dhe në dokumentin e ndeshjes, gjithçka tjetër ruhet e plotë në skedarë anësorë pranë tyre, e numëruar në `selfCheck.completeness` të dokumentit të ndeshjes. Dokumentacioni i vetë konverterit liston çfarë lexon, çfarë ruan të papërpunuar dhe çfarë nuk mund të lexojë.

## Verifikuar {#verified}

konverteri është kontrolluar me riprodhime publike nga disa versione të lojës dhe me teste në riprodhime të ndërtuara; ky lidhës me teste me një komandë zëvendësuese

## Burimi {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
