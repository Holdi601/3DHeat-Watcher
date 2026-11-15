---
title: "EVE Online (skedarë regjistri)"
nav_order: 20
lang: "sq"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (skedarë regjistri) {#eve-online-log-files}

Ndërsa luan EVE Online, watcher lexon skedarët që shkruan loja dhe ruan çfarë ndodhi, që ta shohësh më vonë si statistika dhe vijë kohore.

*Detaje teknike: adaptori `eve`, lloji [`log`](sources-and-rules.md); punon sa kohë `exefile.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- dëmi i shkaktuar dhe i marrë me anijen tjetër, pilotin, shkurtesën e korporatës, armën dhe cilësinë e goditjes
- huqet e shkaktuara dhe të marra
- shpërblimet e paguara (vrasje NPC) me ISK
- kërcimet mes sistemeve
- çdo rresht i gamelog dhe i chat log i plotë te heat.raw.parquet
- dëmi i shkaktuar dhe i marrë, goditjet, huqet, vrasjet me shpërblim dhe ISK, kërcimet

## Nga vjen {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt dhe Chatlogs\\\*.txt pranë tyre (çdo skedar i shkruar që nga nisja e klientit)

## Si ta ndezësh {#how-to-switch-it-on}

Nuk ka asgjë për të ndezur: watcher e lexon burimin ashtu siç e ofron loja ose platforma.

## Si funksionon {#how-it-works}

EVE Online: regjistrat e lojës të klientit, `Documents\EVE\logs\Gamelogs\*.txt`.

Klienti shkruan një skedar për çdo personazh për çdo hyrje,
`<yyyymmdd>_<hhmmss>[_<character id>].txt`; regjistrimi në skedar është i ndezur si parazgjedhje. Disa klientë që punojnë
bashkë shkruajnë secili të vetin, kështu që ndiqet çdo skedar i shkruar që nga nisja e lojës.
Header-i dhe rreshtat (ora e EVE është UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(rreshti combat është një rresht i vetëm në skedar). Etiketat e formatimit hiqen para
krahasimit. Skedari ka qenë UTF-8 dhe UTF-16 gjatë viteve; lexohen të dyja.
Formati nuk është dokumentuar nga CCP; është regjistri tekst i thjeshtë i klientit, i lexuar siç
e lexojnë mjetet e komunitetit për regjistrin e luftës (p.sh. <https://docs.rs/crate/eve-log-parser>).
Pa pozicione.

Pranë tij, `Documents\EVE\logs\Chatlogs\<channel>_<yyyymmdd>_<hhmmss>[_<id>].txt`:
një skedar për çdo kanal bisede për çdo hyrje (kur regjistrimi i bisedës është i ndezur, parazgjedhja e klientit),
UTF-16, një header që emërton kanalin dhe dëgjuesin, pastaj
`[ yyyy.mm.dd hh:mm:ss ] Sender > message`.

Çdo rresht i të dyjave ruhet i plotë te skedari anësor i papërpunuar i sesionit (rregulli i
konvertuesit të 3DHeat): një rresht gamelog nën kanalin e vet në kllapa katrore (`combat`,
`notify`, `bounty`, `None`, ...), një rresht bisede si `chat` me kanalin e vet, rreshtat e
header-it si `gamelog header` / `chatlog header`.

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

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- goditjet `(combat)` të gamelog të shkaktuara dhe të marra (sasia, piloti tjetër, shkurtesa e korporatës, anija, arma, cilësia e goditjes) dhe huqet në të dyja drejtimet
- pagesat `(bounty)` të gamelog me ISK, dhe rreshtat `Jumping from A to B`
- Listener i header-it të gamelog: i kujt është regjistri

**Ruajtur të papërpunuara**

- çdo rresht gamelog i plotë, `type` = kanali i tij në kllapa katrore (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), me `file` dhe `listener`; `used` ku u bë rresht; rreshtat e header-it si `gamelog header`
- çdo rresht i chat log i plotë (Local, korporata, flota, kanalet private, njoftimet `EVE System` si ndryshimi i kanalit Local gjatë një kërcimi), `type` `chat`, me `channel`, `listener` dhe `file`; rreshtat e header-it si `chatlog header`. Ende nuk bëhen rreshta
- etiketat e formatimit (`<color>`, `<b>`, `<font>`) mbeten në tekstin e papërpunuar; rreshtat i kanë të hequra

**Nuk ofrohet**

- pozicionet: klienti nuk shkruan asnjë në regjistrat e vet
- luftimet e pilotëve të tjerë: një gamelog është i dëgjuesit vetë
- regjistrat e hyrjeve të mëparshme: çdo hyrje shkruan skedarë të rinj; ata më të vjetër se ky punim i klientit nuk lexohen sërish
- biseda kur lojtari e ka fikur regjistrimin e bisedës te cilësimet e klientit
- skedarët e cache-it dhe të cilësimeve të vetë klientit: nuk janë regjistra, dhe nuk janë të dokumentuar

**Madhësia**: një gamelog është 0.1-2 MB në orë (më shumë në luftë); regjistrat e bisedës varen nga kanalet e hapura - një Local ose kanal flote i zënë 0.5-3 MB në orë; zstd te heat.raw.parquet e bën afërsisht një të dhjetën

## Verifikuar {#verified}

i provuar me rreshta sintetikë gamelog në formatin e publikuar nga parser-at e komunitetit; i paprovuar me lojën

## Burimi {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
