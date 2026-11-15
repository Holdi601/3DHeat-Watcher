---
title: "Elite Dangerous (fișiere de jurnal)"
nav_order: 18
lang: "ro"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (fișiere de jurnal) {#elite-dangerous-log-files}

Cât timp jucați Elite Dangerous, watcher-ul citește fișierele pe care le scrie jocul și salvează ce s-a întâmplat, ca să le puteți vedea mai târziu pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `elite`, tipul [`log`](sources-and-rules.md); rulează cât timp `EliteDangerous64.exe` este pornit și caută date noi la fiecare 0,25 s.*

## Ce se înregistrează {#what-is-recorded}

- fiecare eveniment din jurnal, sub numele său din jurnal, cu câmpurile sale simple
- poziția în galaxie (StarPos, ani-lumină) la sărituri, la locații, la apariții, la morți, la andocare, la aterizare
- apariția la LoadGame/Resurrect, moartea la Died, andocat/nedocat, atingerea/decolarea de sol, saltul, session_end
- traseul la suprafața planetei din Status.json: latitudine, longitudine, altitudine, direcție și metri într-un plan tangent pentru fiecare corp ceresc (sesiunea = numele corpului), împreună cu celelalte câmpuri simple din Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- fiecare linie din jurnal și fiecare fișier companion, întreg, în `heat.raw.parquet`
- sărituri, distanța parcursă prin salt, morți, uciderile, creditele câștigate, misiunile terminate, corpurile scanate, sistemele vizitate, andocările, aterizările

## De unde vine {#where-it-comes-from}

Jurnalul jucătorului %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (cel mai nou fișier, urmărit pe măsură ce este scris), Status.json și celelalte fișiere companion \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) din același folder

## Cum se activează {#how-to-switch-it-on}

Nu trebuie activat nimic: watcher-ul citește sursa așa cum o oferă jocul sau platforma.

## Cum funcționează {#how-it-works}

Elite Dangerous: jurnalul jucătorului (Player Journal) și Status.json pe care le scrie jocul cât timp rulează.

Unde: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - un obiect JSON pe linie, un fișier pentru fiecare pornire a jocului (o sesiune lungă continuă în partea .02, .03 ...). Fiecare linie are `timestamp` (UTC, ISO 8601) și `event`. Pozițiile galactice sunt `StarPos` [x, y, z] al sistemului, în ani-lumină față de Sol, la `FSDJump`, `Location` și `CarrierJump`. Cadrul galactic al Elite are axa y în sus (spre nordul galactic), z spre centrul galactic și x spre longitudinea galactică 270 - un cadru stângaci, deci vizualizatorul oglindește z ca să-l deseneze corect.
* `Status.json` - rescris integral ori de câte ori se schimbă starea navei: `Flags` și, lângă o planetă, `Latitude`, `Longitude` (grade), `Altitude` (metri), `Heading`, `BodyName` și `PlanetRadius` (metri).
* Celelalte fișiere companion, fiecare rescris integral când se scrie evenimentul corespunzător din jurnal: `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`. Fiecare `*.json` din folder pe care jocul îl scrie în această sesiune este păstrat integral de fiecare dată când se schimbă (regula convertorului 3DHeat: ce conține sursa este citit sau păstrat), sub numele fișierului.

Fiecare linie din jurnal este păstrată întreagă în sidecarul brut al sesiunii, sub `event`-ul ei, iar fiecare fișier companion sub numele fișierului; o linie care nu este JSON ajunge sub `unparsed`.

Pozițiile de suprafață sunt puse într-un plan tangent local pentru fiecare corp, în metri: prima fixare pe un corp este originea, x spre est, z spre nord, y în sus (altitudinea), aceeași dreptaceală ca la cadrul galactic, iar rândurile poartă numele corpului ca `session`, astfel încât o conducere sau o plimbare pe o planetă se desenează ca un traseu aparte. Rândurile galactice au sesiunea „galaxy". Cele două scări sunt într-un singur tabel; alegeți sesiunea în vizualizator.

Format: manualul „Elite Dangerous Player Journal" al Frontier (publicat odată cu fiecare actualizare pe forumurile oficiale, <https://forums.frontier.co.uk/> - „Journal Manual", v4.x), evenimentele și câmpurile conform acelui manual; indicatorii din Status.json conform capitolului „Status File" din același manual.

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa verticală | `y` |
| Unități | ani-lumină (rânduri galactice, sesiunea „galaxy"); metri est/sus/nord de prima fixare pe un corp (rânduri de suprafață, sesiunea = numele corpului) |
| Oglindit pentru vizualizator | `z` |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)".
- Tipul `log`: citește doar ce oferă jocul sau platforma (fișierele pe care le scrie jocul cât timp rulează), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- fiecare linie din jurnal ca rând sub `event`-ul ei, cu câmpurile simple (textul localizat acolo unde jocul îl dă; textele mai lungi de 300 de caractere sunt tăiate în rând)
- rânduri galactice (StarPos) la FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; rânduri de suprafață din Status.json și din Touchdown/Liftoff
- câmpurile simple din Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) pe rândurile de suprafață
- statisticile: sărituri, distanța, morți, uciderile, creditele câștigate, misiunile, corpurile scanate, sistemele vizitate, andocările, aterizările

**Păstrat brut**

- fiecare linie din jurnal, întreagă, `type` = `event`-ul ei (FSDJump, Scan, Music, ReceiveText, ...), `used` adevărat: listele și obiectele pe care rândurile le lasă afară (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) există doar aici
- o linie din jurnal care nu este JSON, `type` `unparsed`
- fiecare fișier companion întreg, de fiecare dată când jocul îl rescrie, `type` = numele fișierului: `Status.json` (`used` când a făcut un rând de suprafață), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json` și orice alt `*.json` pe care jocul îl scrie acolo

**Nu este disponibil**

- poziția între sărituri (în sistem, în supercruise sau în spațiul normal): jocul scrie doar StarPos-ul sistemului și, lângă o planetă, latitudinea, longitudinea și altitudinea
- pozițiile altor nave și ale altor jucători: jurnalul este relatarea comandantului însuși
- viteza, accelerația și alte date de zbor: jocul nu le scrie
- jurnalele și fișierele companion din sesiunile anterioare: sunt păstrate când au fost jucate (urmăritorul pornește de la sfârșitul unui fișier mai vechi decât această rulare a jocului)
- API-ul web companion al Frontier (cAPI): necesită autentificarea jucătorului la Frontier; nu este un fișier scris de joc

**Dimensiune**: aproximativ 1-5 MB de text brut pe oră: jurnalul 0,2-2 MB, Status.json (sub 1 KB, rescris până la o dată pe secundă) 1-2 MB, un set market/outfitting/shipyard 20-150 KB pentru fiecare stație vizitată; zstd din `heat.raw.parquet` îl face cam o zecime

## Verificat {#verified}

parserul a fost reluat pe fișiere reale de jurnal dintr-o instalare locală (numărul de evenimente se potrivește cu statisticile); fixările de suprafață din Status.json au fost testate doar pe instantanee sintetice

## Sursă {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
