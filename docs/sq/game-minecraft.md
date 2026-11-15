---
title: "Minecraft (skedarë regjistri)"
nav_order: 33
lang: "sq"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (skedarë regjistri) {#minecraft-log-files}

Ndërsa luan Minecraft, watcher i lexon skedarët që loja i shkruan dhe ruan çfarë ndodhi, që t'i shohësh më vonë në një hartë në shikuesin 3DHeat.

*Detaje teknike: adaptori `minecraft`, lloji [`log`](sources-and-rules.md); punon sa kohë `javaw.exe` ose `java.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni yt dhe i lojtarëve të tjerë (blloqe = m, y lart) sa herë ruhet bota, dimensioni si sesion
- spawn me pozicion kur një lojtar hyn në serverin (të integruar)
- hyrjet, daljet, vdekjet me mesazhin e vdekjes, arritjet (advancements), rreshtat e bisedës
- vdekjet, arritjet, mesazhet e bisedës; nga skedari i statistikave: koha e lojës, distanca, vrasjet e përbindëshave dhe lojtarëve, kërcimet, dëmi, blloqet e gërmuara, sendet e punuara (pjesa e këtij sesioni)
- çdo rresht i regjistrit dhe çdo skedar i ruajtur i statistikave, arritjeve dhe lojtarit i plotë te heat.raw.parquet

## Nga vjen {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (ndiqet), saves\\&lt;world>\stats\\&lt;uuid>.json dhe saves\\&lt;world>\playerdata\\&lt;uuid>.dat / level.dat (NBT gzip), lexohen kur loja i ruan

## Si ta ndezësh {#how-to-switch-it-on}

Nuk ka asgjë për të ndezur: watcher e lexon burimin ashtu siç e ofron loja ose platforma.

## Si funksionon {#how-it-works}

Minecraft (Java Edition): regjistri, statistikat dhe skedarët e lojtarit që loja i shkruan.

Ku (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - regjistri i lojës, i ri në çdo nisje (i vjetri
  paketohet në një .log.gz me datë). Rreshta `[hh:mm:ss] [thread/LEVEL]: message`
  (ngarkuesit e mod-eve shkruajnë `[ddMMMyyyy hh:mm:ss.mmm] [thread/LEVEL] [logger/]: ...`).
  Çfarë shohin lojtarët te bisedat është aty: hyrjet dhe daljet, mesazhet e vdekjes,
  arritjet, biseda - serveri i integruar i një bote single-player shkruan
  të njëjtat rreshta edhe një herë, kështu që një rresht i përsëritur brenda të njëjtës sekondë numërohet
  një herë. "Setting user: &lt;name>" emërton lojtarin; "&lt;name>[...] logged in with entity id N at (x, y, z)"
  i serverit tregon ku u shfaq.
* `saves\<world>\stats\<uuid>.json` - ekrani i statistikave, shkruhet kur
  ruhet bota (ruajtje automatike çdo disa minuta, dhe kur largohesh): `stats` ->
  `minecraft:custom` (play_time në tick, mob_kills, distancat \*_one_cm, jump,
  ...), `minecraft:mined`, `minecraft:crafted`, ... Totalet për botën; shifrat e
  sesionit janë diferenca me atë që thoshte skedari kur nisi loja.
  Formati: <https://minecraft.wiki/w/Statistics>
* `saves\<world>\playerdata\<uuid>.dat` (dhe `level.dat` -> Data -> Player
  për një host single-player) - NBT i kompresuar me gzip, shkruhet në të njëjtat ruajtje:
  `Pos` [x, y, z] doubles, `Rotation` [yaw, pitch], `Dimension`
  ("minecraft:overworld"; një int 0/-1/1 para 1.16). NBT sipas
  <https://minecraft.wiki/w/NBT_format> - lexohet këtu nga një lexues i vogël i yni.
* `saves\<world>\advancements\<uuid>.json` - ecuria e ekranit të arritjeve,
  shkruhet në të njëjtat ruajtje.

Koordinatat janë blloqe, një bllok një metër, y lart; x lindje, z jug - një kuadër
i djathtë, vizatohet siç është. Pozicionet vijnë vetëm kur ruhet bota, kështu që një
rrugë janë disa pika për çdo ruajtje automatike, jo një gjurmë; dimensioni është
`session`, kështu që Nether nuk vizatohet mbi Overworld.

Gjithçka e lexuar ruhet e plotë te skedari anësor i papërpunuar i sesionit (rregulli i
konvertuesit të 3DHeat): çdo rresht i regjistrit nën nivelin e vet (`INFO`, `WARN`, `ERROR`, ...; një rresht
pa kokën me kllapa, si një stack trace, si `untagged`), dhe çdo skedar i ruajtur
nën llojin e vet (`stats`, `advancements`, `playerdata`,
`level.dat`) - JSON si tekst, NBT si bajtet e tij. Numrat e një skedari statistikash kuptohen
vetëm krahasuar me atë që thoshte kur nisi loja, prandaj ajo kopja e parë
ruhet gjithashtu (`baseline`), herën e parë që skedari ndryshon.

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `y` |
| Njësitë | blloqe (1 bllok = 1 m) |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `log`: lexon vetëm atë që loja ose platforma e jep vetë (skedarë që loja i shkruan teksa punon), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- latest.log: emri i lojtarit (`Setting user`), hyrjet me pozicion, hyrjet, daljet, vdekjet me mesazhin e vdekjes, arritjet, rreshtat e bisedës, ndalimi i serverit
- stats/&lt;uuid>.json: koha e lojës, distanca, vrasjet e përbindëshave dhe lojtarëve, kërcimet, dëmi i shkaktuar dhe i marrë, blloqet e gërmuara, sendet e punuara - pjesa e kësaj seance
- playerdata/&lt;uuid>.dat dhe level.dat (NBT): pozicioni, dimensioni, yaw, pitch, shëndeti, niveli XP

**Ruajtur të papërpunuara**

- çdo rresht i latest.log i plotë, `type` = niveli i tij (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) me thread-in e logger-it te `thread`, `used` ku u bë rresht; një rresht pa kokën me kllapa (një stack trace, një banner i një mod-i) si `untagged`
- çdo stats/&lt;uuid>.json i plotë si tekst, `type` `stats` (`used`: numrat e tij janë te statistikat), me kopjen e tij të parë nga nisja e lojës si `baseline`
- çdo advancements/&lt;uuid>.json i plotë si tekst, `type` `advancements` (çdo kriter dhe kur u plotësua; ende nuk bëhet rreshta)
- çdo playerdata/&lt;uuid>.dat dhe level.dat i plotë si bajte (NBT gzip), `type` `playerdata` / `level.dat`, `used` ku dha një pozicion: inventari, ender chest, efektet, pika e spawn-it, rregullat e lojës, fara dhe koha e botës janë vetëm këtu
- çdo skedar i ruajtur ka `world` dhe `file` (rruga e tij nën `saves`)

**Nuk ofrohet**

- një gjurmë pozicioni: loja e shkruan pozicionin e lojtarit vetëm kur ruhet bota (çdo disa minuta dhe kur largohesh)
- pozicionet në një server që e mban dikush tjetër: skedarët e botës së tij janë në server, jo këtu; atëherë lexohet vetëm regjistri
- vetë bota (skedarët e rajoneve .mca, entitetet, hartat dhe sulmet data/\*.dat): e madhe, dhe është terreni, jo loja
- regjistrat e seancave të mëparshme (logs/\*.log.gz): ruhen kur janë luajtur
- Bedrock Edition: nuk shkruan regjistër dhe skedarë të tillë

**Madhësia**: latest.log 0.1-2 MB në orë (më shumë me mod-e); një skedar statistikash 5-50 KB dhe një skedar lojtari 5-100 KB për çdo ruajtje automatike, level.dat 1-20 KB - rreth 1-5 MB në orë gjithsej; zstd te heat.raw.parquet e bën tekstin rreth një të dhjetën (skedarët NBT janë tashmë gzip)

## Verifikuar {#verified}

u provua me rreshta regjistri sintetikë, JSON statistikash dhe skedarë NBT të ndërtuar sipas formateve të publikuara; i paprovuar me lojën

## Burimi {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
