---
title: "Dota 2 (reluări)"
nav_order: 12
lang: "ro"
source: game-dota-replays.md
source_hash: "958b1e1855e8"
nav_exclude: true
search_exclude: true
---
# Dota 2 (reluări) {#dota-2-replays}

După un meci de Dota 2, watcher-ul transformă reluarea salvată de joc în fișiere pe care te poți uita pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `dota-replays`, tip [`replay`](sources-and-rules.md); rulează tot timpul (nu așteaptă ca un joc să pornească) și caută date noi la fiecare 5 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția, înălțimea, viața și nivelul fiecărui erou, de 7,5 ori pe secundă cât este în viață
- eliminări și morți acolo unde s-au produs; turnuri, cazărmi, Roshan și Tormentors acolo unde au căzut; ward-uri acolo unde au fost plantate
- semnalele de hartă, desenele de hartă și comenzile (mișcare, atac, folosire, cumpărare, ...) ale fiecărui jucător, acolo unde au arătat
- scorul și rândul fiecărui jucător; rândul jucătorului conectat, ca statistici
- orice altceva conține reluarea, păstrat integral lângă tabel: fiecare cadru și mesaj de rețea, fiecare schimbare de proprietate a unei entități, fiecare intrare din tabelele de șiruri

## De unde vine {#where-it-comes-from}

reluările salvate de Dota 2: &lt;Dota>/game/dota/replays/&lt;match id>.dem (descărcate în client, sau cu `dota-replay <match id>`)

## Cum o pornești {#how-to-switch-it-on}

descarci reluarea unui meci în Dota 2, sau aduci una publică: `python -m heat3d_watch dota-replay <match id>`; are nevoie de `pip install gem-dota`

Scrie comanda într-un terminal deschis în folderul watcher-ului (vezi [Înainte de a începe](before-you-start.md)). Dacă eșuează, ultima linie spune de ce; [Instalarea și rularea](installing-and-running.md) acoperă cauzele obișnuite.

## Cum funcționează {#how-it-works}

Reluări și demo-uri: ce salvează un joc despre un meci, convertit după ce meciul s-a terminat.

O reluare conține tot ce o interfață live ține ascuns în jocurile multiplayer - poziția fiecărui jucător, fiecare eliminare acolo unde s-a produs - și este un fișier pe care jocul îl scrie pentru jucătorii lui, deci citirea ei nu atinge nimic din joc. Watcher-ul se uită în folderele unde jocurile le salvează, așteaptă până când un fișier nou nu mai crește (altfel jocul încă îl scrie) și îl convertește într-un fir de lucru, așa că o conversie lungă nu oprește restul watcher-ului.

Prima dată când este văzut un folder, reluările deja din el sunt doar notate, nu convertite: un jucător cu ani de demo-uri ar găsi altfel watcher-ul ocupat o zi întreagă. `python -m heat3d_watch replays <adapter> [folder]` convertește pe cerere pe cele existente.

#### Dota 2 {#dota-2}

Dota 2 salvează reluările pe care le descarcă un jucător (detaliile unui meci, sau Watch > Replays) în `<Dota>/game/dota/replays/<match id>.dem`; Valve păstrează reluarea fiecărui meci public pe serverele sale câteva săptămâni, iar `python -m heat3d_watch dota-replay <match id>` aduce una după id-ul ei prin OpenDota. Fiecare este citită cu gem (github.com/whanyu1212/gem-dota, MIT, `pip install gem-dota`) într-un proces propriu (`heat3d_watch/decoders/dota_replay.py`): poziția, înălțimea, viața, nivelul, orientarea, mana, experiența, atributele și obiectele fiecărui erou, de 7,5 ori pe secundă cât este în viață, eliminările și morțile acolo unde s-au produs, turnurile, cazărmile, Roshan și Tormentors acolo unde au căzut, fiecare ward acolo unde a fost plantat și unde s-a încheiat, intrările din jurnalul de luptă despre eroi (daune, vindecări, abilități, obiecte, cumpărături, runele, aurul, experiența, modificatorii), și fiecare semnal de hartă, desen de hartă și comandă a fiecărui jucător - în `dota/<match>.parquet`; fiecare altă unitate (creaturi, invocații, iluzii, curieri, clădiri) o dată pe secundă, în `<match>.units.parquet`; tot jurnalul de luptă, în `<match>.combatlog.parquet`; iar meciul, chatul, draftul, orice altceva extrage parserul și înregistrarea de final de meci a jocului, în `<match>.match.json`, în folderul sesiunii. Restul a ceea ce conține reluarea este păstrat integral lângă ele (regula de convertor a 3DHeat): fiecare cadru și mesaj de rețea în `<match>.packets.parquet`, fiecare schimbare de proprietate a unei entități în `<match>.entities.parquet`, fiecare intrare din tabelele de șiruri în `<match>.strings.parquet`, numărate în `selfCheck.completeness` din documentul meciului. Pozițiile sunt în unitățile lumii Dota, aceleași pe care le raportează integrarea stării jocului. Rândul din tabelul de scor al jucătorului conectat devine statisticile sesiunii: eliminări, morți, asistențe, last hits, denies, valoarea netă, GPM, XPM, daunele aduse eroilor, ward-urile și dacă meciul a fost câștigat. O nouă actualizare Dota poate schimba entitățile din reluare înainte ca gem să o urmeze; o reluare pe care gem nu o poate citi până la capăt este convertită cât poate și marcată `incomplete` în rezumatul ei.

Același modul servește și: [Counter-Strike 2 (reluări)](game-cs2-demos.md), [osu! (reluări)](game-osu-replays.md), [Squad (reluări)](game-squad-demos.md), [War Thunder (reluări)](game-warthunder-replays.md), [World of Tanks (reluări)](game-wot-replays.md), [World of Warships (reluări)](game-wows-replays.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa în sus | `z` |
| Unități | unitățile lumii Dota (unități Hammer; harta are circa 16400 pe lățime) |
| Oglindită pentru vizualizator | `y` |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, așa că vizualizatorul 3DHeat rotește și scalează singur rândurile - vezi [Datele](the-data.md).

## Joc online {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)”.
- Tip `replay`: citește doar ce scoate jocul sau platforma (reluări și demo-uri salvate de joc), deci înregistrează și în jocul online, nu doar offline; steagul decide doar dacă memoria are voie să fie citită vreodată.
- Memorie: **niciodată** citită de acest adaptor. Doar adaptoarele `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online - vezi [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistică pe care codul acestui adaptor le setează după nume (`stats` din `meta.json` al fiecărei sesiuni și tabelul `stats` din `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor jocului nu sunt în această listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Convertorul urmează [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: ce are reluarea este citit sau păstrat, niciodată aruncat. În afara tabelului, tot ce conține reluarea este păstrat integral în fișiere sidecar lângă el, în folderul `dota/` al sesiunii - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (coloanele `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, după caz) - iar `selfCheck.completeness` din documentul meciului (`<match>.match.json`) numără fiecare `type` - `lost` este 0.

**Citit**

- tabelul (`dota/<match>.parquet`): poziția, înălțimea, viața, nivelul, orientarea, mana, experiența, atributele, armura, viteza, daunele, obiectele și cursorul jucătorului, de 7,5 ori pe secundă; eliminări, morți, obiective, ward-uri, intrările din jurnalul de luptă despre eroi; semnalele de hartă (`ping`, DOTA_UM_LocationPing), desenele de hartă (`map_line`, DOTA_UM_MapLine) și fiecare comandă de unitate (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` tipul comenzii, `value` id-ul abilității sau obiectului, `text` clasa țintei; la punctul comandat, altfel la erou)
- `<match>.units.parquet`: fiecare altă unitate, o dată pe secundă; `<match>.combatlog.parquet`: tot jurnalul de luptă așa cum îl citește gem, fiecare câmp
- documentul meciului: tot ce extrage gem, și integral înregistrările proprii ale reluării - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: lungimea redării, numele, id-ul Steam, eroul și echipa fiecărui jucător), `matchDetails` (DOTA_UM_MatchDetails: tabelul de scor de final de meci al coordonatorului de joc, cifrele fiecărui jucător, obiectele, daunele pe tip, alegerile și interdicțiile) și `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: eliminările, morțile, asistențele, nivelul, last hits și denies citite din flux, comparate cu `matchDetails`, pe fiecare jucător

**Păstrat brut**

- `<match>.packets.parquet`: fiecare cadru care nu este pachet (`type` `frame <n>`) și fiecare mesaj de rețea (`message <n>`, `name` numele dat de Valve), integral în `payload`, în ordinea fișierului (`seq`, `frame`), cu `decoded` protobuf-ul ca JSON (un câmp de octeți dat prin lungimea lui), fiecare tip de mesaj decodat: svc_PacketEntities (fluxul de entități), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, mesajele jurnalului de luptă, GE_SosStartSoundEvent, DOTA_UM_TE_\* (proiectile, animații, sânge), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; tabelele de trimitere, lista de clase și informațiile serverului de care are nevoie un decodor ulterior de entități sunt printre ele
- `<match>.entities.parquet`: fiecare proprietate a fiecărei entități, de fiecare dată când s-a schimbat (`type` proprietatea, `name` clasa, `entity` indexul ei; `value`, `vector` sau `decoded`), starea ei completă la creare, și fiecare creare, intrare, ieșire și ștergere - milioane de rânduri pentru un meci întreg
- `<match>.strings.parquet`: fiecare intrare din tabelul de șiruri, din fiecare actualizare și din fiecare instantaneu complet, cu valoarea integrală; `userinfo`, `ActiveModifiers` și `EconItems` decodate din protobuf-urile lor
- `selfCheck.completeness` din documentul meciului numără cadrele și mesajele după numele dat de Valve, intrările din jurnalul de luptă (`combatlog <type>`), evenimentele de joc (`gameevent <name>`), intrările din tabelele de șiruri (`stringtable <name>`) și actualizările de entități (`entity <class>`); câteva sunt păstrate doar brut (instantaneele complete ale entităților pe care gem le sare, fiindcă reconstruiește din diferențe, și intrările din tabelele pe care nimic nu le citește), cu 0 pierdute

**Nedisponibil**

- vocea: reluarea are configurarea vocii, dar nu și datele vocale
- nume din spatele hash-urilor și id-urilor: sunetele și particulele sunt numite prin hash-urile fișierelor jocului, abilitățile prin id-uri; reluarea nu poartă numele (obiectele sunt numite prin catalogul lui gem, unde îl are)
- orice ce știau doar clienții jucătorilor (camera lor, ecranul lor) dincolo de ce a difuzat serverul; cursorul și fiecare comandă sunt incluse

**Dimensiune**: sidecar-urile împreună sunt ceva mai mari decât reluarea însăși, cele mai mari fiind pachetele și entitățile; un meci întreg durează un minut sau două într-un singur proces

## Verificat {#verified}

verificat pe reluarea unui meci public: eliminările, morțile, asistențele, nivelul, last hits și denies se potrivesc cu înregistrarea de final de meci a jocului pentru toți cei zece jucători; fiecare mesaj din sidecar-ul de pachete se re-serializează octet cu octet; tabelul și statisticile testate pe date sintetice

## Sursă {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
