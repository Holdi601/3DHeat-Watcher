---
title: "Path of Exile (skedarë regjistri)"
nav_order: 35
lang: "sq"
source: game-poe.md
source_hash: "b5783b5a5690"
nav_exclude: true
search_exclude: true
---
# Path of Exile (skedarë regjistri) {#path-of-exile-log-files}

Ndërsa luan Path of Exile, watcher lexon skedarët që shkruan loja dhe ruan çfarë ndodhi, që ta shohësh më vonë si statistika dhe vijë kohore.

*Detaje teknike: adaptori `poe`, lloji [`log`](sources-and-rules.md); punon sa kohë `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` ose `PathOfExile_x64_KG.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- zonat e hyra me nivelin e zonës, id-në e zonës dhe seed-in e saj
- rritjet e nivelit me klasën dhe nivelin
- vdekjet ("has been slain")
- lojtarët që hyjnë e dalin nga zona, pëshpëritjet hyrëse e dalëse, kërkesat për tregti, tregtitë e pranuara
- çdo rresht i Client.txt i kësaj seance i plotë te heat.raw.parquet
- vdekjet, nivelet e fituara, niveli më i lartë, zonat e hyra, zonat e veçanta, pëshpëritjet, kërkesat për tregti, tregtitë

## Nga vjen {#where-it-comes-from}

&lt;install>\logs\Client.txt i Path of Exile ose Path of Exile 2 (ndiqet; dosja e instalimit është ajo e skedarit të ekzekutueshëm që punon)

## Si ta ndezësh {#how-to-switch-it-on}

Nuk ka asgjë për të ndezur: watcher e lexon burimin ashtu siç e ofron loja ose platforma.

## Si funksionon {#how-it-works}

Path of Exile dhe Path of Exile 2: regjistri i klientit, `<install>\logs\Client.txt`.

Të dyja lojërat shtojnë në një Client.txt të vetëm në dosjen e instalimit për aq kohë sa
janë të instaluara (rritet nga një nisje te tjetra). Rreshtat duken kështu

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- ora lokale, një numërues milisekondash, një hash, niveli dhe thread-i, pastaj çfarë
  tregon dritarja e bisedës. Mesazhet janë ato të klientit anglisht; klienti i një gjuhe
  tjetër i shkruan të përkthyera dhe këtu nuk kuptohet. Asgjë nuk jep një
  pozicion. Formati nuk është dokumentuar nga Grinding Gear Games; është
  regjistri tekst i thjeshtë i lojës, siç e kanë lexuar për vite mjetet e komunitetit (ndihmës tregtie, udhëzues nivelesh) - p.sh. <https://github.com/klayveR/poe-log-monitor> (MIT) për
  listën e ngjarjeve.

Dosja e instalimit është ajo e skedarit të ekzekutueshëm që punon; pa të kërkohen bibliotekat
e Steam dhe dosja e parazgjedhur e klientit të pavarur.

Çdo rresht i kësaj seance ruhet i plotë te skedari anësor i papërpunuar i sesionit (rregulli i
konvertuesit të 3DHeat), kuptim ose jo këtu: `type` është niveli dhe
logger-i në kllapat e tij (`INFO Client`, `DEBUG Client`, `WARN Client`, ...), një
rresht me kohë pa kllapa është `untagged`, një rresht pa kohë
`untimed`.

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | jo |
| Boshti lart | `y` |
| Njësitë | nuk regjistrohen pozicione |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `log`: lexon vetëm atë që loja ose platforma e jep vetë (skedarë që loja i shkruan sa kohë punon), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- `You have entered <zone>`, me nivelin e zonës, id-në e zonës dhe seed-in e rreshtit `Generating level` para tij
- `<name> (<class>) is now level <n>`, `<name> has been slain`, lojtarët që hyjnë e dalin nga zona, pëshpëritjet hyrëse e dalëse (me faktin nëse janë kërkesë tregtie), tregtitë e pranuara e të anuluara

**Ruajtur të papërpunuara**

- çdo rresht i kësaj seance i plotë, `type` = niveli dhe logger-i në kllapat e tij (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` ku u bë rresht: biseda globale, e tregtisë, e grupit dhe e gildës, `Connecting to instance server`, njoftimet AFK dhe DND, përgjigjet e komandave të bisedës si `/played` dhe `/deaths`, rreshtat e ngarkimit dhe të motorit të klientit - ruhen, ende nuk bëhen rreshta
- një rresht me kohë pa kllapa (`***** LOG FILE OPENING *****`) si `untagged`, një rresht pa kohë si `untimed`

**Nuk ofrohet**

- pozicionet: asgjë në regjistër nuk jep një
- çfarë shkruan klienti i një gjuhe tjetër: rreshtat ruhen, por vetëm mesazhet anglisht bëhen rreshta
- rreshtat e nisjeve të mëparshme: Client.txt rritet nga një nisje te tjetra; rreshtat me kohë para këtij punimi të lojës lihen (u ruajtën kur u luajtën)
- vrasjet, dëmi, plaçkitja dhe pema e pasive: loja nuk i regjistron

**Madhësia**: Client.txt rritet rreth 0.3-3 MB në orë (shumica nga rreshtat DEBUG gjatë ngarkimit të zonave, më shumë me bisedë tregtie të zënë); zstd te heat.raw.parquet e bën afërsisht një të dhjetën

## Verifikuar {#verified}

i provuar me rreshta sintetikë Client.txt në formatin e lojës; i paprovuar me lojën

## Burimi {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
