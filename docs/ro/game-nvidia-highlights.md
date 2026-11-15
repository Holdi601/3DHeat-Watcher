---
title: "NVIDIA highlights (platformă)"
nav_order: 34
lang: "ro"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (platformă) {#nvidia-highlights-platform}

Watcher-ul salvează ce păstrează NVIDIA Highlights despre jocurile voastre, ca să vă puteți vedea istoricul mai târziu pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `nvidia-highlights`, tipul [`platform`](sources-and-rules.md); rulează tot timpul (nu așteaptă ca un joc să pornească) și caută date noi la fiecare 10 s.*

## Ce se înregistrează {#what-is-recorded}

- fiecare clip, highlight sau captură de ecran nou: joc, fișier, tip, lungime și momentul (ms de ceas)
- id-ul și numele highlight-ului, când jocul l-a înregistrat la NVIDIA
- unde se afla jucătorul în acel moment, când un alt adaptor a înregistrat atunci același joc
- cererile de highlight pe care le jurnalizează jocurile GfeSDK, chiar când nu se păstrează niciun clip

## De unde vine {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;game>\config.json; clipurile în folderul de captură (%USERPROFILE%\Videos\NVIDIA\\&lt;Game>\\\*.mp4) și &lt;temp>\Highlights\\&lt;game>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Cum se activează {#how-to-switch-it-on}

NVIDIA App: Instant Replay sau Highlights activat, clipuri salvate cu tasta rapidă sau de joc

## Cum funcționează {#how-it-works}

Ce păstrează lansatorul și driverul plăcii grafice despre joc: statisticile, realizările, timpul de joc și cronologiile Steam, precum și highlight-urile și clipurile NVIDIA.

Niciuna dintre aceste surse nu are nevoie ca un joc să coopereze sau să ruleze, deci cele trei adaptoare de aici sunt mereu active și citesc câteva fișiere la fiecare câteva secunde.

#### Highlight-urile și clipurile NVIDIA (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Ce păstrează NVIDIA App / GeForce Experience, toate sub `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
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
Și fișierele de clip în sine, `<capture folder>\<Game>\<Game> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (capturile de ecran: `<Game> Screenshot yyyy.mm.dd - ...png`), ora din nume fiind ora locală la care a fost salvat clipul. Jocurile GfeSDK își jurnalizează și apelurile de highlight în `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Ce poate și ce nu poate livra aceasta: un joc care suportă NVIDIA Highlights (GfeSDK) înregistrează tipurile de highlight o singură dată - un id precum „kill”, o importanță, etichete, un nume afișat - iar mai târziu spune doar „highlight <id>, from <ms> before now to <ms> after”. Nu există poziții, meci sau rundă, adversar, date personalizate: SDK-ul nu are câmp pentru nimic din acestea. Un clip salvat adaugă un fișier, un nume de joc, o lungime și un moment. Deci ce se înregistrează este „acest tip de moment, în acest joc, la acest moment” - iar un loc doar prin căutarea momentului în înregistrarea unui alt adaptor a aceluiași joc (`position_at`), lucru pe care acest adaptor îl face pentru fiecare clip înregistrat. <https://developer.nvidia.com/highlights>

Fiecare adaptor păstrează ce a văzut deja în `<data>\state\<id>.json`, deci o repornire nu înregistrează nimic de două ori.

Fiecare sesiune păstrează și de unde provin rândurile ei, întreg (regula convertorului 3DHeat, docs/converters.md din depozitul vizualizatorului), în `heat.raw.parquet`: fișierul de statistici și octeții schemei lui, precum și blocul localconfig al jocului (steam-stats; un fișier de statistici pe care decodorul nu îl poate citi primește o sesiune care conține doar octeții lui), fișierul de cronologie - antetul și fiecare intrare ca JSON (steam-timeline), fiecare intrare din indexul galeriei pentru fiecare clip, definițiile de highlight ale jocului și fiecare linie GfeSDK (nvidia-highlights), inclusiv cele care nu sunt cereri de highlight.

Același modul servește și: [Statistici Steam (platformă)](game-steam-stats.md), [Cronologia Steam (platformă)](game-steam-timeline.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | doar împrumutate: locul pe care îl are pentru acel moment o altă înregistrare a aceluiași joc |
| Axa verticală | `y` |
| Unități | metri |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **nu**. `games --markdown` arată asta ca „un singur jucător”.
- Tipul `platform`: citește doar ce oferă jocul sau platforma (ce păstrează Steam sau driverul plăcii grafice), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- fiecare clip nou și captură de ecran: joc, fișier, tip, suport, lungime (indexul, altfel antetul MP4), momentul din numele fișierului, id-ul și numele highlight-ului unde jocul le-a înregistrat, și locul jucătorului atunci din înregistrarea altui adaptor
- cererile de highlight GfeSDK (fiecare `Posted Request HL...`, mai puțin apelurile de configurare) cu momentul lor

**Păstrat brut**

- `UGC`: intrarea întreagă a clipului din indexul galeriei UGCTracker.json, fiecare câmp pe care îl scrie NVIDIA
- `clip_file`: pentru un clip pe care indexul nu-l listează, calea fișierului, dimensiunea, ora și folderul său
- `highlights_config`: `Highlights\<game>\config.json` al jocului așa cum este scris (importanță, etichete, nume în fiecare limbă), o dată pe sesiune
- `gfesdk_log`: fiecare linie din jurnalele GfeSDK citite după prima rulare, `used` adevărat pentru cererile de highlight și fals pentru celelalte (configurare, setările video, mesajele proprii ale SDK-ului)

**Nu este disponibil**

- clipurile și capturile de ecran în sine: videoclipul și imaginile rămân unde le-a salvat NVIDIA; rândurile numesc fișierul
- ce era înainte de prima rulare a adaptorului: luat ca deja văzut, deci anii de clipuri nu devin sesiuni dintr-odată (`baseline`; False le înregistrează)
- `apps` și `info` din UGCTracker.json și GallerySettings.json: setările aplicației, nu momente de joc; folderul de captură pe care îl numesc este folosit
- poziții, runde, adversari: GfeSDK nu are câmp pentru ele

**Dimensiune**: aproximativ 1 KB pe clip și câțiva KB de definiții și linii de jurnal pe lansare a jocului: mult sub 1 MB pe oră

## Verificat {#verified}

testat pe un index real de galerie, setări, definiții de highlight și clipuri dintr-o instalare locală; liniile de cerere de highlight GfeSDK și id-urile de highlight din clipuri sunt netestate

## Sursă {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
