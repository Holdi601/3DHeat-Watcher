---
title: "NVIDIA highlights (platformë)"
nav_order: 34
lang: "sq"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (platformë) {#nvidia-highlights-platform}

Watcher ruan çfarë mban NVIDIA highlights për lojërat e tua, që ta shohësh historikun më vonë në një hartë në shikuesin 3DHeat.

*Detaje teknike: adaptori `nvidia-highlights`, lloji [`platform`](sources-and-rules.md); punon gjithë kohën (nuk pret që të nisë një lojë) dhe kërkon të dhëna të reja çdo 10 s.*

## Çfarë regjistrohet {#what-is-recorded}

- çdo klip, highlight ose pamje ekrani i ri: loja, skedari, lloji, gjatësia dhe çasti (ms sipas orës së murit)
- id-ja dhe emri i highlight-it kur loja e ka regjistruar te NVIDIA
- ku ishte lojtari në atë çast, kur një adaptor tjetër e regjistroi atëherë të njëjtën lojë
- kërkesat për highlight që lojërat GfeSDK i regjistrojnë, edhe kur nuk ruhet asnjë klip

## Nga vjen {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;game>\config.json; klipet në dosjen e kapjes (%USERPROFILE%\Videos\NVIDIA\\&lt;Game>\\\*.mp4) dhe &lt;temp>\Highlights\\&lt;game>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Si ta ndezësh {#how-to-switch-it-on}

NVIDIA App: Instant Replay ose Highlights të ndezur, klipe të ruajtura me shkurtore tastiere ose nga vetë loja

## Si funksionon {#how-it-works}

Çfarë mbajnë nisësi dhe drejtuesi i grafikës për lojën: statistikat e Steam,
arritjet, koha e luajtur dhe vijat kohore, dhe highlights e klipet e NVIDIA.

Asnjë nga këto burime nuk ka nevojë që një lojë të bashkëpunojë ose të punojë, kështu që të tre
adaptorët këtu janë gjithmonë të ndezur dhe shikojnë disa skedarë çdo disa sekonda.

#### NVIDIA highlights dhe klipe (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Çfarë mban NVIDIA App / GeForce Experience, gjithçka nën
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      the gallery index: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, when the file was written), profileName, drsName
                     (the exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (where clips are saved),
                     settings.tempDirectory (highlights wait in
                     <temp>\Highlights\<game> until saved)
Highlights\<game>\config.json  the highlight kinds a game registered:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
dhe vetë skedarët e klipeve, `<capture folder>\<Game>\<Game> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (pamjet e ekranit: `<Game> Screenshot yyyy.mm.dd - ...png`), ku
ora e emrit është ora lokale kur u ruajt klipi. Lojërat GfeSDK i regjistrojnë edhe
thirrjet e tyre të highlight te `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Çfarë mund dhe çfarë nuk mund të japë kjo: një lojë që mbështet NVIDIA Highlights
(GfeSDK) regjistron llojet e highlight një herë - një id si "kill", një
rëndësi, etiketa, një emër për shfaqje - dhe më vonë thotë vetëm "highlight &lt;id>,
nga &lt;ms> para tani deri &lt;ms> pas". Nuk ka pozicione, as ndeshje ose
raund, as kundërshtar, as të dhëna të personalizuara: SDK-ja nuk ka fushë për asnjërën. Një
klip i ruajtur shton një skedar, një emër loje, një gjatësi dhe një kohë. Pra çfarë
regjistrohet është "ky lloj çasti, në këtë lojë, në këtë kohë" - dhe një vend
vetëm duke e kërkuar kohën te regjistrimi i një adaptori tjetër i së njëjtës lojë
(`position_at`), gjë që ky adaptor e bën për çdo klip që regjistron.
<https://developer.nvidia.com/highlights>

Çdo adaptor ruan çfarë ka parë tashmë te `<data>\state\<id>.json`, kështu që një
rinisje nuk regjistron asgjë dy herë.

Çdo sesion ruan edhe nga ç'erdhën rreshtat e tij, të plota (rregulli i konvertuesit të 3DHeat,
docs/converters.md në depon e shikuesit), te `heat.raw.parquet`:
bajtet e skedarit të statistikave dhe të skemës së tij dhe blloku localconfig i lojës
(steam-stats; një skedar statistikash që dekoderi nuk e lexon merr një sesion që mban vetëm
bajtet e tij), header-i i skedarit të vijës kohore dhe çdo hyrje si JSON
(steam-timeline), hyrja e indeksit të galerisë për çdo klip, përkufizimet e highlight
të lojës dhe çdo rresht i regjistrit GfeSDK, edhe ata që nuk janë kërkesa për highlight
(nvidia-highlights).

Të njëjtin modul e përdorin edhe: [Statistikat e Steam (platformë)](game-steam-stats.md), [Steam Timeline (platformë)](game-steam-timeline.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | vetëm të huazuara: vendi që një regjistrim tjetër i së njëjtës lojë ka për atë çast |
| Boshti lart | `y` |
| Njësitë | metra |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **jo**. `games --markdown` e shfaq këtë si "single-player".
- Lloji `platform`: lexon vetëm atë që loja ose platforma e jep vetë (çfarë mbajnë Steam ose drejtuesi i grafikës), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- çdo klip dhe pamje ekrani i ri: loja, skedari, lloji, media, gjatësia (indeksi, përndryshe header-i MP4), çasti nga emri i skedarit, id-ja dhe emri i highlight kur loja i ka regjistruar, dhe vendi i lojtarit atëherë nga regjistrimi i një adaptori tjetër
- kërkesat për highlight të GfeSDK (çdo `Posted Request HL...` përveç thirrjeve të konfigurimit) me kohën e tyre

**Ruajtur të papërpunuara**

- `UGC`: hyrja e plotë e klipit te indeksi i galerisë UGCTracker.json, çdo fushë që shkruan NVIDIA
- `clip_file`: për një klip që indeksi nuk e liston, rruga e skedarit, madhësia, koha dhe dosja
- `highlights_config`: `Highlights\<game>\config.json` i lojës siç është shkruar (rëndësia, etiketat, emrat në çdo gjuhë), një herë për sesion
- `gfesdk_log`: çdo rresht i regjistrave GfeSDK të lexuar pas nisjes së parë, `used` e vërtetë për kërkesat për highlight dhe e rreme për të tjerat (konfigurimi, cilësimet e videos, mesazhet e vetë SDK-së)

**Nuk ofrohet**

- vetë klipet dhe pamjet e ekranit: videoja dhe imazhet mbeten aty ku i ruajti NVIDIA; rreshtat e emërtojnë skedarin
- çfarë ishte aty para nisjes së parë të adaptorit: merret si e parë tashmë, kështu që vite klipesh nuk kthehen menjëherë në sesione (`baseline`; False i regjistron)
- `apps` dhe `info` të UGCTracker.json dhe GallerySettings.json: cilësimet e aplikacionit, jo çaste loje; dosja e kapjes që ato emërtojnë përdoret
- pozicionet, raundet, kundërshtarët: GfeSDK nuk ka fushë për to

**Madhësia**: rreth 1 KB për klip dhe disa KB përkufizime e rreshta regjistri për çdo nisje loje: shumë nën 1 MB në orë

## Verifikuar {#verified}

i provuar me një indeks galerie të vërtetë, cilësime, përkufizime highlight dhe klipe nga një instalim lokal; rreshtat e kërkesave për highlight të GfeSDK dhe id-të e highlight në klipe janë të paprovuara

## Burimi {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
