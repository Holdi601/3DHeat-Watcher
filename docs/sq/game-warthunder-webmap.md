---
title: "War Thunder (gjendja e lojës)"
nav_order: 46
lang: "sq"
source: game-warthunder-webmap.md
source_hash: "34a876e38f09"
nav_exclude: true
search_exclude: true
---
# War Thunder (gjendja e lojës) {#war-thunder-game-state}

Ndërsa luan War Thunder, watcher-i ruan çfarë i raporton loja programeve në kompjuterin tënd, që më vonë ta shohësh në një hartë në shikuesin 3DHeat.

*Detaje teknike: adapteri `warthunder-webmap`, lloji [`gsi`](sources-and-rules.md); ekzekutohet sa kohë `aces.exe` është në punë dhe kërkon të dhëna të reja çdo 0.5 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni yt (lindje/veri e hartës në metra; lartësia nga /state në avion, përndryshe 0) dy herë në sekondë, drejtimi, shpejtësia
- shfaqjet dhe largimi i mjetit tënd nga harta (shkatërruar, ulur, kthyer në hangar), një sortie secila
- avionët e tjerë dhe njësitë tokësore në minihartë si pozicione me id të ndjekura dhe anën (pa lartësi)
- aeroportet, zonat e pushtimit dhe bazat një herë, dhe zonat që ndryshojnë anë
- rreshtat e kill feed dhe damage feed (kush, mjeti, folja); vrasjet dhe vdekjet e lojtarit kur emri yt është vendosur (`config --set player_names.warthunder-webmap=<name>`)
- shfaqjet, largësia, lartësia më e madhe, shpejtësia e vërtetë më e madhe, mjeti; vrasjet dhe vdekjet kur emri yt është vendosur
- çdo përgjigje e hartës web e ruajtur e plotë në heat.raw.parquet - /state dhe /indicators të plota, chat-i, objektivat e betejës dhe pamja e hartës përfshirë; mes betejave në një seancë të vetën

## Nga vjen {#where-it-comes-from}

harta web lokale e lojës, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Si aktivizohet {#how-to-switch-it-on}

Asgjë nuk duhet aktivizuar: watcher-i e lexon burimin siç e jep loja ose platforma.

## Si funksionon {#how-it-works}

War Thunder: harta web lokale e vetë lojës te <http://127.0.0.1:8111>.

Loja shërben faqen që mund ta shfaqë një ekran i dytë ose një telefon ("harta web"),
dhe JSON-in prapa saj, sa kohë është në punë - në çdo mënyrë, edhe lojë me shumë lojtarë:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: the map's extent in metres; valid false in the hangar
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 of the map picture, y down), "dx", "dy" (direction),
                  airfields "sx", "sy", "ex", "ey"}]: what the minimap shows, the player's own
                  vehicle with icon "Player"; no ids, no heights
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: flight values,
                  valid only in an aircraft
/indicators      {"valid", "army": air|tank|..., "type": the vehicle}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} newer than the ids given, each
                  {"id", "msg", "sender", "enemy", "mode", "time"}; damage lines read like
                  "Name (Vehicle) shot down Name (Vehicle)"
/gamechat?lastId=N  the chat newer than the id given, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    the battle's objectives and their status
/map.img         the map's picture the page draws the objects on
```

Çdo përgjigje ruhet e plotë në skedarin raw anësor të seancës nën endpoint-in e saj
(map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img);
mes betejave përgjigjet shkojnë në një seancë të vetën.

Një pozicion në hartë bëhet metra me përmasat: u = min_x + x \* (max_x - min_x)
lindje, v = max_y - y \* (max_y - min_y) veri (y i pamjes shkon poshtë). Rreshtat janë
x = u, y = lartësia ("H, m" i avionit tënd; 0 për gjithçka tjetër), z = v, kështu që
Y është lart; z pasqyrohet për shikuesin që veriu të mos vizatohet në jug.

Ngjyrat tregojnë anët siç i sheh lojtari: vetja e verdhë (#faC81E parazgjedhje),
skuadra e gjelbër, aleatët blu (#174DFF), armiqtë të kuq (#f40C00); paletat për
verbëri ngjyrash i ndryshojnë, ndaj vendos nuanca, jo vlera e saktë. Loja nuk emërton askënd
në hartë dhe nuk u jep objekteve id: objekteve të tjera këtu u jepen id duke i ndjekur
nga një pyetje te tjetra (më i afërti i të njëjtit lloj dhe ikonë), gjë që mund të ndërrojë dy
avionë të një lloji që kalojnë pranë njëri-tjetrit. Emri i vetë lojtarit nuk është as në
API: jepe në cilësime (`config --set
player_names.warthunder-webmap=<your name>`) dhe rreshtat e kill feed për
lojtarin bëhen vrasje dhe vdekje; pa të regjistrohen si kill feed.

Burimet: faqja e vetë lojës te <http://127.0.0.1:8111> dhe JSON-i i saj; faktet e fushave
siç i dokumenton projekti JoyPro 2 (docs/telemetry-recording.md; GPL, përdorur vetëm për
fakte).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet regjistrohen | po |
| Boshti lart | `y` |
| Njësitë | metra (lindje/veri e hartës; lartësia vetëm për avionin tënd) |
| Pasqyruar për shikuesin | `z` |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto shkojnë në `meta.json` të çdo seance (`axes`) dhe, kur seanca ka pozicione, në fundin e `heat.parquet`, që shikuesi 3DHeat t'i rrotullojë dhe shkallëzojë rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si luajtur online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `gsi`: lexon vetëm çfarë jep loja ose platforma (një integrim i gjendjes së lojës ose API lokale që e shërben loja), ndaj regjistron edhe në lojë online edhe offline; flamuri vendos vetëm nëse mund të lexohet ndonjëherë memoria.
- Memoria: **kurrë** nuk lexohet nga ky adapter. Vetëm adapterat `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adapteri i vendos me emër (`stats` e çdo seance në `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Një çelës në kllapa gjarpëruese plotësohet gjatë ekzekutimit (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë fushash të lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher-i ndjek [rregullin e konvertuesve](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, nuk hidhet kurrë. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që merr adapteri ruhet e plotë në `heat.raw.parquet` të seancës (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e mbajtur me emër; `used` shënon çfarë u bë edhe rresht), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexohet**

- /map_info.json: përmasat dhe rrjeta e hartës (metra, id-ja e hartës) në meta.json; një e pavlefshme e mbyll betejën
- /map_obj.json (dy herë në sekondë): mjeti yt, avionët e tjerë dhe njësitë tokësore (id të ndjekura, ana nga ngjyra, ikona, drejtimi, ngjyra) dhe aeroportet, zonat e bazat si rreshta
- /state (dy herë në sekondë, në avion): lartësia, TAS, IAS, Mach dhe Vy në rreshtat e tu
- /indicators (çdo 2 s): ushtria dhe lloji i mjetit
- /hudmsg (një herë në sekondë): rreshtat e kill dhe damage feed si vrasje, vdekje, goditje dhe rreshta feed; ngjarjet e tjera HUD si rreshta

**Ruhet i papërpunuar**

- çdo përgjigje e plotë, `text` JSON-i siç e dërgoi loja, nën endpoint-in e saj: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` bajtet e pamjes së hartës si `payload`, një herë në betejë
- çfarë mban vetëm skedari raw anësor: çdo fushë e /state përtej të pesave të lexuara (AoA, AoS, Ny, Wx, gazi, RPM, karburanti, ... - grupi i një avioni ndryshon nga ai i tjetrit), çdo fushë e /indicators (instrumentet e kabinës së avionëve, shpejtësia, ingranazhi, ekuipazhi dhe stabilizuesi i tankeve), çelësat e tjerë të objekteve të hartës (color[], blink, icon_bg, skajet e aeroportit), sender, enemy dhe mode të hudmsg, chat-i (/gamechat, një herë në sekondë), objektivat e betejës dhe statusi i tyre (/mission.json, çdo 10 s në betejë), rreshtat e thënë para se të niste watcher-i
- mes betejave (hangar, ngarkim) përgjigjet shkojnë në një seancë të vetën, e shënuar `between_battles` në meta.json, që nuk ka rreshta

**Nuk disponohet**

- emrat, id-të dhe lartësitë e mjeteve të lojtarëve të tjerë: harta web nuk ka asnjë (id-të jepen këtu duke ndjekur objektet nga një pyetje te tjetra); kill feed emërton lojtarë pa pozicione
- gjithçka jashtë hartës web: riluajtjet e lojës i lexon konvertuesi i riluajtjeve të War Thunder, dhe memoria e lojës nuk lexohet kurrë (lojë online)
- /map_obj.json më shpejt se dy herë në sekondë: shpejtësia e pyetjes mbahet e ulët, që serveri web i vetë lojës të mos ngarkohet

**Madhësia**: rreth 50-120 MB në orë JSON para zstd në betejë (map_obj 5-15 KB dy herë në sekondë, state rreth 1.5 KB dy herë në sekondë, indicators çdo 2 s, chat-i dhe rreshtat HUD të vegjël) plus pamja e hartës një herë në betejë (nën 2 MB); 1-2 MB në orë mes betejave (pamja e hartës dy herë në sekondë, HUD dhe chat një herë, secila një përgjigje e shkurtër); zstd e zvogëlon JSON-in e përsëritur shumë më shumë se dhjetë herë

## Verifikuar {#verified}

provuar kundrejt një serveri lokal të rremë që jep përgjigje në formatin e hartës web të lojës; i paprovuar me lojën në punë

## Burimi {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Gjeneruar nga adapteri me tools/gen_game_pages.py; ndrysho adapterin dhe ekzekuto përsëri, mos e redakto këtë faqe. -->
