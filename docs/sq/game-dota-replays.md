---
title: "Dota 2 (riluajtjet)"
nav_order: 12
lang: "sq"
source: game-dota-replays.md
source_hash: "88539ee6dc65"
nav_exclude: true
search_exclude: true
---
# Dota 2 (riluajtjet) {#dota-2-replays}

Pas një ndeshjeje Dota 2, watcher-i e kthen riluajtjen që ruajti loja në skedarë që mund t'i shohësh në një hartë në shikuesin 3DHeat.

*Detaje teknike: adapteri `dota-replays`, lloji [`replay`](sources-and-rules.md); ekzekutohet gjatë gjithë kohës (nuk pret të niset një lojë) dhe kërkon të dhëna të reja çdo 5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni, lartësia, jeta dhe niveli i çdo heroi, 7.5 herë në sekondë ndërsa është gjallë
- vrasjet dhe vdekjet aty ku ndodhën; kullat, barrakat, Roshan dhe Tormentors aty ku ranë; wards aty ku u vendosën
- pingjet në hartë, vizatimet në hartë dhe urdhrat (lëviz, sulmo, hidh, bli, ...) e çdo lojtari aty ku i drejtoi
- rezultati dhe rreshti i çdo lojtari; ai i lojtarit të kyçur si statistika
- çdo gjë tjetër që mban riluajtja, e ruajtur e plotë pranë tabelës: çdo kuadër dhe mesazh rrjeti, çdo ndryshim vetie të entiteteve, çdo hyrje e tabelave të vargjeve

## Nga vjen {#where-it-comes-from}

riluajtjet që ruan Dota 2: &lt;Dota>/game/dota/replays/&lt;match id>.dem (shkarkuar në klient, ose me `dota-replay <match id>`)

## Si aktivizohet {#how-to-switch-it-on}

shkarko riluajtjen e një ndeshjeje në Dota 2, ose merr një publike: `python -m heat3d_watch dota-replay <match id>`; instalo lexuesin: github.com/Holdi601/3DHeat-Ext-DotaReplay (`heat3d-dota-replay`, sjell gem-dota)

Shkruaje komandën në një terminal të hapur në dosjen e watcher-it (shih [Para se të fillosh](before-you-start.md)). Nëse dështon, rreshti i fundit tregon pse; [Instalimi dhe ekzekutimi](installing-and-running.md) përmban shkaqet më të zakonshme.

Cilësime nga variablat e mjedisit:

- `HEAT3D_DOTA_REPLAY`: dosja e lexuesit (një klon ose një release i shpaketuar), kur nuk është i instaluar ose pranë watcher-it

## Si funksionon {#how-it-works}

Riluajtjet dhe demot: çfarë ruan një lojë nga një ndeshje, e konvertuar kur ndeshja ka mbaruar.

Një riluajtje mban gjithçka që një ndërfaqe e drejtpërdrejtë e mban të fshehur në lojërat me shumë lojtarë -
pozicionin e çdo lojtari, çdo vrasje aty ku ndodhi - dhe është një skedar që
loja e shkruan për lojtarët e vet, ndaj leximi i tij nuk prek asgjë në lojë. Watcher-i
shikon dosjet ku lojërat i ruajnë, pret derisa një skedar i ri të ketë ndaluar së
rrituri (përndryshe loja ende po e shkruan), dhe e konverton në një
thread punëtor, kështu që një konvertim i gjatë nuk e ndalon kurrë pjesën tjetër të watcher-it.

Herën e parë që shihet një dosje, riluajtjet që ka tashmë vetëm shënohen, nuk
konvertohen: një lojtar me vite demo do ta gjente watcher-in të zënë
për një ditë të tërë. `python -m heat3d_watch replays <adapter> [folder]` i konverton
ato ekzistueset sipas kërkesës.

#### Dota 2 {#dota-2}

Dota 2 ruan riluajtjet që shkarkon një lojtar (detajet e një ndeshjeje, ose Watch >
Replays) te `<Dota>/game/dota/replays/<match id>.dem`; Valve mban riluajtjen e çdo ndeshjeje
publike në serverët e vet për disa javë, dhe `python -m heat3d_watch
dota-replay <match id>` e merr një me id-në e saj përmes OpenDota. Watcher-i
nuk i lexon vetë: i lexon një lexues i jashtëm (3DHeat Dota Replay,
github.com/Holdi601/3DHeat-Ext-DotaReplay, `exporters/ext/dota-replay`, komanda
`heat3d-dota-replay`, që lexon përmes gem-dota, MIT), një projekt më vete,
dhe ekzekutohet në një proces të vetin për çdo
riluajtje të re kur është në PATH, i instaluar, ose pranë watcher-it; nëse mungon,
watcher-i thotë një herë si të instalohet. Ai shkruan pozicionin, lartësinë, jetën, nivelin, drejtimin, manën, përvojën, atributet dhe sendet e çdo heroi, 7.5
herë në sekondë ndërsa është gjallë, vrasjet dhe vdekjet aty ku ndodhën, kullat,
barrakat, Roshan dhe Tormentors aty ku ranë, çdo ward aty ku u
vendos dhe ku mbaroi, hyrjet e combat log-ut për heronjtë
(dëm, shërime, aftësi, sende, blerje, runa, flori, përvojë,
modifikues), dhe pingjet në hartë, vizatimet në hartë dhe urdhrat e çdo lojtari - në
`dota/<match>.parquet`; çdo njësi tjetër (creeps, summons, iluzione,
couriers, ndërtesa) një herë në sekondë në `<match>.units.parquet`; të gjithë
combat log-un në `<match>.combatlog.parquet`; dhe ndeshjen, chat-in,
draft-in, çdo gjë tjetër që nxjerr parseri dhe regjistrimin e vetë lojës të
fundit të ndeshjes në `<match>.match.json`, në dosjen e seancës. Çdo gjë tjetër
që mban riluajtja ruhet e plotë pranë tyre (rregulli i konvertuesve të 3DHeat):
çdo kuadër dhe mesazh rrjeti në `<match>.packets.parquet`, çdo ndryshim
vetie të entiteteve në `<match>.entities.parquet`, çdo hyrje e tabelave të vargjeve në
`<match>.strings.parquet`, e numëruar në `selfCheck.completeness` të dokumentit të ndeshjes. Pozicionet janë njësitë botërore të Dota,
të njëjtat që raporton integrimi i gjendjes së lojës. Rreshti i tabelës së pikëve të
lojtarit të kyçur bëhet statistikat e seancës: kills, deaths, assists,
last hits, denies, net worth, GPM, XPM, hero damage, wards, dhe nëse
ndeshja u fitua. Një patch i ri i Dota mund t'i ndryshojë entitetet e riluajtjes para se gem
t'i ndjekë; një riluajtje që gem nuk mund ta lexojë deri në fund konvertohet aq sa
shkon dhe shënohet `incomplete` në përmbledhjen e saj.

I njëjti modul shërben edhe: [Counter-Strike 2 (riluajtjet)](game-cs2-demos.md), [Squad (riluajtjet)](game-squad-demos.md), [War Thunder (riluajtjet)](game-warthunder-replays.md), [World of Tanks (riluajtjet)](game-wot-replays.md), [World of Warships (riluajtjet)](game-wows-replays.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet regjistrohen | po |
| Boshti lart | `z` |
| Njësitë | njësi botërore Dota (njësi Hammer; harta është rreth 16400 e gjerë) |
| Pasqyruar për shikuesin | `y` |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto shkojnë në `meta.json` të çdo seance (`axes`) dhe, kur seanca ka pozicione, në fundin e `heat.parquet`, që shikuesi 3DHeat t'i rrotullojë dhe shkallëzojë rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si luajtur online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `replay`: lexon vetëm çfarë jep loja ose platforma (riluajtjet dhe demot që ruan loja), ndaj regjistron edhe në lojë online edhe offline; flamuri vendos vetëm nëse mund të lexohet ndonjëherë memoria.
- Memoria: **kurrë** nuk lexohet nga ky adapter. Vetëm adapterat `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adapteri i vendos me emër (`stats` e çdo seance në `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Një çelës në kllapa gjarpëruese plotësohet gjatë ekzekutimit (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë fushash të lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Konvertuesi ndjek [rregullin e konvertuesve](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban riluajtja lexohet ose ruhet, nuk hidhet kurrë. Përveç tabelës, çdo gjë tjetër që mban riluajtja ruhet e plotë në skedarë anësorë pranë saj në dosjen `dota/` të seancës - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (kolonat `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, sipas rastit) - dhe `selfCheck.completeness` i dokumentit të ndeshjes (`<match>.match.json`) numëron çdo `type` - `lost` është 0.

**Lexohet**

- tabela (`dota/<match>.parquet`): pozicioni, lartësia, jeta, niveli, drejtimi, mana, përvoja, atributet, forca mbrojtëse, shpejtësia, dëmi, sendet e çdo heroi dhe kursori i lojtarit 7.5 herë në sekondë; vrasjet, vdekjet, objektivat, wards, hyrjet e combat log-ut për heronjtë; pingjet në hartë (`ping`, DOTA_UM_LocationPing), vizatimet në hartë (`map_line`, DOTA_UM_MapLine) dhe çdo urdhër njësie (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` lloji i urdhrit, `value` id-ja e aftësisë ose e sendit, `text` klasa e objektivit; në pikën e urdhëruar, përndryshe te heroi)
- `<match>.units.parquet`: çdo njësi tjetër një herë në sekondë; `<match>.combatlog.parquet`: i gjithë combat log-u siç e lexon gem, çdo fushë
- dokumenti i ndeshjes: gjithçka që nxjerr gem, dhe të plota regjistrimet e vetë riluajtjes - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: gjatësia e riluajtjes, emri, heroi, id-ja Steam, ekipi i çdo lojtari), `matchDetails` (DOTA_UM_MatchDetails: tabela e pikëve e koordinatorit të lojës në fund të ndeshjes, numrat e çdo lojtari, sendet, dëmi sipas llojit, zgjedhjet dhe ndalimet) dhe `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: kills, deaths, assists, level, last hits dhe denies siç lexohen nga rryma kundrejt `matchDetails`, për lojtar

**Ruhet i papërpunuar**

- `<match>.packets.parquet`: çdo kuadër që nuk është paketë (`type` `frame <n>`) dhe çdo mesazh rrjeti (`message <n>`, `name` i Valve), i plotë në `payload`, sipas renditjes në skedar (`seq`, `frame`), me `decoded` protobuf-in si JSON (një fushë bajtesh e dhënë si gjatësia e saj), çdo lloj mesazhi i dekoduar: svc_PacketEntities (rryma e entiteteve), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, mesazhet e combat log-ut, GE_SosStartSoundEvent, DOTA_UM_TE_\* (predha, animacione, gjak), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; tabelat e dërgimit, lista e klasave dhe informacioni i serverit që i duhen një dekoduesi të mëvonshëm të entiteteve janë mes tyre
- `<match>.entities.parquet`: çdo veti e çdo entiteti sa herë ndryshoi (`type` vetia, `name` klasa, `entity` indeksi i tij; `value`, `vector` ose `decoded`), gjendja e tij e plotë kur u krijua, dhe çdo krijim, hyrje, dalje dhe fshirje - miliona rreshta për një ndeshje të tërë
- `<match>.strings.parquet`: çdo hyrje e tabelave të vargjeve nga çdo përditësim dhe çdo pamje e plotë, vlera e plotë; `userinfo`, `ActiveModifiers` dhe `EconItems` të dekoduara nga protobuf-et e tyre
- `selfCheck.completeness` në dokumentin e ndeshjes numëron kuadrot dhe mesazhet sipas emrit të Valve, hyrjet e combat log-ut (`combatlog <type>`), ngjarjet e lojës (`gameevent <name>`), hyrjet e tabelave të vargjeve (`stringtable <name>`) dhe përditësimet e entiteteve (`entity <class>`); disa ruhen vetëm të papërpunuara (pamje të plota të entiteteve që gem i kapërcen sepse rindërton nga deltat, dhe hyrje të tabelave vlerat e të cilave nuk i lexon askush), lost 0

**Nuk disponohet**

- zëri: riluajtja ka konfigurimin e zërit por jo të dhëna zëri
- emrat pas hash-eve dhe id-ve: tingujt dhe grimcat emërtohen me hash-e të skedarëve të lojës, aftësitë me id; riluajtja nuk i mban emrat (sendet emërtohen përmes katalogut të gem ku i ka)
- çdo gjë që e dinin vetëm klientët e vetë lojtarëve (kamera, ekrani i tyre) përtej asaj që transmetoi serveri; kursori dhe çdo urdhër janë brenda

**Madhësia**: skedarët anësorë së bashku janë disi më të mëdhenj se vetë riluajtja, paketat dhe entitetet më të mëdhenjtë; një ndeshje e tërë merr një a dy minuta në një proces

## Verifikuar {#verified}

kontrolluar në riluajtjen e një ndeshjeje publike: kills, deaths, assists, level, last hits dhe denies përputhen me regjistrimin e vetë lojës në fund të ndeshjes për të dhjetë lojtarët; çdo mesazh në skedarin anësor të paketave serializohet përsëri bajt për bajt; tabela dhe statistikat me teste në të dhëna sintetike

## Burimi {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Gjeneruar nga adapteri me tools/gen_game_pages.py; ndrysho adapterin dhe ekzekuto përsëri, mos e redakto këtë faqe. -->
