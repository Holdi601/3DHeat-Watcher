---
title: "League of Legends (gjendja e lojës)"
nav_order: 29
lang: "sq"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (gjendja e lojës) {#league-of-legends-game-state}

Ndërsa luan League of Legends, watcher ruan çfarë i raporton loja programeve në kompjuterin tënd, që ta shohësh më vonë si statistika dhe vijë kohore.

*Detaje teknike: adaptori `lol-live`, lloji [`gsi`](sources-and-rules.md); punon sa kohë `League of Legends.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pa pozicione: API nuk ka
- kill feed: vrasjet, vdekjet dhe asistimet e lojtarit, vrasjet e kampionëve të tjerë me vrasësin, viktimën, asistuesit
- dragonjtë, herald-ët, baron-ët, kullat, inhibitor-ët, multikill-et, ace-t, first blood, fillimi dhe fundi i lojës
- vrasjet, vdekjet, asistimet, creep score, ward score, niveli, ari, kampioni, koha e lojës, rezultati i vetë lojtarit
- objektivat e marrë nga ekipi i lojtarit

## Nga vjen {#where-it-comes-from}

Live Client Data API i klientit të lojës, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), gjatë një ndeshjeje

## Si ta ndezësh {#how-to-switch-it-on}

Nuk ka asgjë për të ndezur: watcher e lexon burimin ashtu siç e ofron loja ose platforma.

## Si funksionon {#how-it-works}

League of Legends: Live Client Data API që klienti i lojës e ofron gjatë një ndeshjeje.

Sa kohë zhvillohet një ndeshje (edhe në practice tool dhe në modalitetin e shikuesit), `League of
Legends.exe` përgjigjet te <https://127.0.0.1:2999> me atë që lojtari mund ta shohë te
ndërfaqja e vetë lojës:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} from EventID N on: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Nuk ka pozicione: API nuk ka, kështu që një sesion League është ngjarje dhe
statistika, pa tabelë heat. Certifikata është e vetënënshkruar, nga rrënja e vetë Riot
(`riotgames.pem`, e publikuar te
<https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Kushtet e saj të
përdorimit nuk janë shprehur, kështu që nuk shpërndahet: vendose te `<data>\riotgames.pem` dhe
lidhja verifikohet me të; pa të verifikimi është i fikur - dhe vetëm
për 127.0.0.1, adresën e vetme me të cilën flet ky adaptor.

Politika e Riot lejon mjete që të tregojnë çfarë mund ta dinte lojtari nga loja
vetë, dhe asgjë të llogaritur përtej saj (pa kohëmatës armiqsh): ky regjistron kill feed
dhe tabelën e rezultateve që sheh lojtari, dhe numrat e vetë lojtarit.

Çdo përgjigje ruhet edhe e plotë (rregulli i konvertuesit të 3DHeat, docs/converters.md në
depon e shikuesit): `heat.raw.parquet`, `type` endpoint-i
("allgamedata", "eventdata"), `text` JSON-i siç e dërgoi klienti, `status`
kur nuk ishte 200. Një përgjigje bajt për bajt si ajo e mëparshme e endpoint-it të vet (lista e
ngjarjeve kur nuk ndodh asgjë) ruhet një herë dhe numërohet te `unchanged_replies` i meta.json.
allgamedata mban gjithçka që ofrojnë endpoint-et e tjerë (activeplayer\*, playerlist,
playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), kështu që ata
nuk kërkohen veç. Përgjigjet para një ndeshjeje (ekrani i ngarkimit) presin në një backlog dhe hyjnë
në sesionin e ndeshjes; pas GameEnd sesioni mbetet i hapur derisa të largohet klienti, kështu që
përgjigjet e ekranit të fundit ruhen me të.

Burimi: <https://developer.riotgames.com/docs/lol#game-client-api>

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | jo |
| Boshti lart | `z` |
| Njësitë | asnjë (pa pozicione) |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `gsi`: lexon vetëm atë që loja ose platforma e jep vetë (një integrim i gjendjes së lojës ose një API lokale që loja e ofron), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- kill feed nga eventdata: çdo ngjarje një herë, fushat e emërtuara të dekoduara (vrasësi, viktima dhe asistuesit me kampionin dhe ekipin, strukturat dhe ana e tyre, lloji i dragoit, vjedhjet, multikill-et, ace-t, first blood, rezultati) dhe çdo fushë tjetër e një ngjarjeje te rreshti i saj nën emrin e vet
- nga allgamedata: vrasjet, vdekjet, asistimet, creep score, ward score, niveli, ari, kampioni i vetë lojtarit, koha e lojës, modaliteti i lojës dhe harta

**Ruajtur të papërpunuara**

- `allgamedata`: çdo përgjigje e plotë (`text`), çdo 2 s - activePlayer (aftësitë, çdo statistikë e kampionit, runat e plota, ari, niveli), allPlayers (sendet me vendet dhe çmimet, runat, magjitë e thirrësit, rezultatet, niveli, i vdekur dhe kohëmatësi i ringjalljes, skin, korsia, bot), ngjarjet, gameData (modaliteti, koha, harta, terreni); `used` e vërtetë sa kohë zhvillohet ndeshja, e rreme në ekranin e fundit
- `eventdata`: çdo përgjigje e plotë, e kërkuar çdo 0.5 s nga id-ja e ngjarjes tjetër e tutje; `used` e vërtetë kur solli ngjarje të reja
- një përgjigje bajt për bajt si ajo e mëparshme e endpoint-it të vet ruhet një herë dhe numërohet (`unchanged_replies` te meta.json); përgjigjet me gabim (RESOURCE_NOT_FOUND i ekranit të ngarkimit) ruhen me `status`-in e tyre, para fillimit të ndeshjes

**Nuk ofrohet**

- pozicionet: API nuk ka (pa minimap, pa koordinata)
- endpoint-et e tjerë (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): secili ofron një pjesë të allgamedata, kështu që nuk kërkohen
- Replay API (`/replay/*` në të njëjtën portë): luan riluajtje dhe lojëra të ndjekura sapo ndizet te game.cfg, nuk është pjesë e një ndeshjeje të luajtur
- endpoint-et e lockfile të klientit League: nuk janë API i publikuar (Burimet dhe rregullat)
- vlerat mes dy leximeve: API përgjigjet kur kërkohet dhe nuk shtyn; tabela e rezultateve kërkohet çdo 2 s, ngjarjet çdo 0.5 s

**Madhësia**: allgamedata është 15-40 KB (mban listën e plotë të ngjarjeve, që rritet) çdo 2 s: rreth 30-70 MB në orë te `raw.bin`; eventdata shton pak, pasi përgjigjet e pandryshuara numërohen, nuk ruhen; zstd e zvogëlon JSON-in e përsëritur te `heat.raw.parquet` në disa MB në orë (vlerësuar nga formati i dokumentuar)

## Verifikuar {#verified}

i provuar me një server lokal të rremë që ofron përgjigje në formatin e dokumentuar; i paprovuar me lojën

## Burimi {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
