---
title: "War Thunder (starea jocului)"
nav_order: 47
lang: "ro"
source: game-warthunder-webmap.md
source_hash: "d6026c277030"
nav_exclude: true
search_exclude: true
---
# War Thunder (starea jocului) {#war-thunder-game-state}

Cât joci War Thunder, watcher-ul salvează ce raportează jocul către programe de pe calculatorul tău, ca să te poți uita mai târziu la ele pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `warthunder-webmap`, tip [`gsi`](sources-and-rules.md); rulează cât timp `aces.exe` este pornit și caută date noi la fiecare 0,5 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția ta (est/nord pe hartă, în metri; înălțimea din /state, în aeronavă, altfel 0) de două ori pe secundă, cap, viteză
- apariții și ieșirea vehiculului tău de pe hartă (distrus, aterizat, înapoi în hangar), câte o sortie fiecare
- alte aeronave și unități terestre de pe minimap, ca poziții cu id-uri urmărite și partidă (fără înălțime)
- aerodromuri, zone de captură și baze, o dată, și zonele care își schimbă partida
- rânduri din fluxul de lovituri și daune (cine, vehicul, verb); eliminările și morțile jucătorului, când numele tău este setat (`config --set player_names.warthunder-webmap=<nume>`)
- apariții, distanța, altitudinea maximă, viteza reală maximă, vehiculul; eliminări și morți, când numele tău este setat
- fiecare răspuns al hărții web, păstrat integral în heat.raw.parquet - /state și /indicators complete, chatul, obiectivele bătăliei și imaginea hărții incluse; între bătălii, într-o sesiune proprie

## De unde vine {#where-it-comes-from}

harta web locală a jocului, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Cum o pornești {#how-to-switch-it-on}

Nu trebuie pornit nimic: watcher-ul citește sursa așa cum o oferă jocul sau platforma.

## Cum funcționează {#how-it-works}

War Thunder: harta web locală a jocului, pe <http://127.0.0.1:8111>.

Jocul servește pagina pe care o poate arăta un al doilea ecran sau un telefon (harta web), și JSON-ul din spatele ei, cât timp rulează - în orice mod, inclusiv în multiplayer:

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

Fiecare răspuns este păstrat integral în sidecar-ul brut al sesiunii, sub endpoint-ul lui (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img); între bătălii, răspunsurile merg într-o sesiune proprie.

O poziție de pe hartă devine metri cu ajutorul întinderii: u = min_x + x \* (max_x - min_x) est, v = max_y - y \* (max_y - min_y) nord (y din imagine merge în jos). Rândurile sunt x = u, y = înălțimea (`H, m` al aeronavei proprii; 0 pentru orice altceva), z = v, deci Y este în sus; z este oglindit pentru vizualizator, ca nordul să nu fie desenat la sud.

Culorile arată taberele așa cum le vede jucătorul: galben pentru ale tale (#faC81E implicit), verde pentru escadrilă, albastru pentru aliați (#174DFF), roșu pentru inamici (#f40C00); paletele pentru daltonism schimbă culorile, deci nuanța decide, nu valoarea exactă. Jocul nu numește pe nimeni de pe hartă și nu dă obiectelor id-uri: alte obiecte primesc aici id-uri urmărindu-le de la o interogare la alta (cel mai apropiat de același tip și icon), ceea ce poate schimba două aeronave de același tip care trec aproape una de alta. Numele propriu al jucătorului nu este nici el în API: dă-l în setări (`config --set player_names.warthunder-webmap=<numele tău>`), și rândurile din fluxul de lovituri despre jucător devin eliminări și morți; fără el, se înregistrează ca flux de lovituri.

Surse: pagina proprie a jocului, de la <http://127.0.0.1:8111>, și JSON-ul ei; faptele despre câmpuri, așa cum sunt documentate de proiectul JoyPro 2 (docs/telemetry-recording.md; GPL, folosit doar pentru fapte).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa în sus | `y` |
| Unități | metri (est/nord pe hartă; înălțime doar pentru aeronava proprie) |
| Oglindită pentru vizualizator | `z` |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, așa că vizualizatorul 3DHeat rotește și scalează singur rândurile - vezi [Datele](the-data.md).

## Joc online {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)”.
- Tip `gsi`: citește doar ce scoate jocul sau platforma (o integrare a stării jocului sau o API locală pe care o servește jocul), deci înregistrează și în jocul online, nu doar offline; steagul decide doar dacă memoria are voie să fie citită vreodată.
- Memorie: **niciodată** citită de acest adaptor. Doar adaptoarele `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online - vezi [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistică pe care codul acestui adaptor le setează după nume (`stats` din `meta.json` al fiecărei sesiuni și tabelul `stats` din `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor jocului nu sunt în această listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: ce are sursa este citit sau păstrat, niciodată aruncat. În afară de rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat integral în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat după nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type` - `lost` este 0.

**Citit**

- /map_info.json: întinderea și grila hărții (metri, id-ul hărții) în meta.json; unul invalid încheie bătălia
- /map_obj.json (de două ori pe secundă): vehiculul tău, alte aeronave și unități terestre (id-uri urmărite, partida după culoare, icon, cap, culoare), precum și aerodromuri, zone și baze, ca rânduri
- /state (de două ori pe secundă, în aeronavă): altitudinea, TAS, IAS, Mach și Vy pe rândurile tale
- /indicators (la fiecare 2 s): armata și tipul vehiculului
- /hudmsg (o dată pe secundă): rândurile din fluxul de lovituri și daune ca eliminări, morți, lovituri și rânduri de flux; alte evenimente HUD ca rânduri

**Păstrat brut**

- fiecare răspuns integral, `text` JSON-ul cum l-a trimis jocul, sub endpoint-ul lui: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` octeții imaginii hărții ca `payload`, o dată pe bătălie
- ce are doar sidecar-ul brut: fiecare câmp /state dincolo de cele cinci citite (AoA, AoS, Ny, Wx, accelerație, turație, combustibil, ... - setul unei aeronave diferă de al alteia), fiecare câmp /indicators (instrumentele de bord ale aeronavelor, viteza, treapta, echipajul și stabilizatorul tancurilor), celelalte chei ale obiectelor de pe hartă (color[], blink, icon_bg, capetele aerodromurilor), sender-ul, inamicul și modul din hudmsg, chatul (/gamechat, o dată pe secundă), obiectivele bătăliei și starea lor (/mission.json, la fiecare 10 s într-o bătălie), replicile spuse înainte să pornească watcher-ul
- între bătălii (hangar, încărcare), răspunsurile merg într-o sesiune proprie, marcată `between_battles` în meta.json, care nu are rânduri

**Nedisponibil**

- nume, id-uri și înălțimi ale vehiculelor altor jucători: harta web nu le are (id-urile sunt date aici urmărind obiectele de la o interogare la alta); fluxul de lovituri numește jucătorii fără poziții
- orice e în afara hărții web: reluările jocului sunt citite de convertorul de reluări War Thunder, iar memoria jocului nu este citită niciodată (un joc online)
- /map_obj.json mai des decât de două ori pe secundă: rata de interogare se ține joasă, ca serverul web al jocului să nu fie încărcat

**Dimensiune**: circa 50-120 MB pe oră de JSON înainte de zstd într-o bătălie (map_obj 5-15 KB de două ori pe secundă, state circa 1,5 KB de două ori pe secundă, indicators la fiecare 2 s, chatul și rândurile HUD mici), plus imaginea hărții o dată pe bătălie (sub 2 MB); 1-2 MB pe oră între bătălii (aspectul hărții de două ori pe secundă, HUD și chatul o dată, fiecare un răspuns scurt); zstd reduce JSON-ul care se repetă de peste zece ori

## Verificat {#verified}

testat cu un server local fals, care servește răspunsuri în formatul hărții web a jocului; netestat cu jocul care rulează

## Sursă {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
