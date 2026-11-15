---
title: "Star Citizen (log datoteke)"
nav_order: 42
lang: "bs"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (log datoteke) {#star-citizen-log-files}

Dok igrate Star Citizen, watcher čita datoteke koje igra piše i sprema šta se desilo, da to kasnije možete pogledati kao statistiku i vremensku liniju.

*Tehnički detalji: adapter `starcitizen`, vrsta [`log`](sources-and-rules.md); radi dok je pokrenut `StarCitizen.exe` i svakih 0,5 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- smrti sa žrtvom, ubicom, oružjem, vrstom štete i zonom (igrači i NPC-ovi)
- onesposobljena i uništena vozila, s vozačem, uzrokom i zonom
- ciljevi quantum putovanja, promjene solarnog sistema, spawnovi, respawnovi, onesposobljavanja
- svaka linija Game.log cijela u heat.raw.parquet
- ubistva (igrača i NPC-ova), smrti, samoubistva, uništena i izgubljena vozila, quantum skokovi

## Odakle dolazi {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (build folder pokrenutog StarCitizen.exe), samo log datoteka koju igra piše - igra s Easy Anti-Cheat: ništa ne dira njen proces

## Kako ga uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Star Citizen: vlastiti log klijenta, `<install>\StarCitizen\LIVE\Game.log`.

Igra piše Game.log iznova pri svakom pokretanju (prethodni ide u
`logbackups\`). Čita se samo ta datoteka: Star Citizen koristi Easy Anti-Cheat, a
ništa ovdje se ne približava procesu igre. Linije počinju UTC vremenskom oznakom i
nivoom, pa oznakom u ugaonim zagradama:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(ovdje prelomljeno; u datoteci je svaka u jednoj liniji). Zona smrti je obično
brod u kojem je žrtva sjedila, a ne mjesto. Format Cloud
Imperium nije dokumentirao i mijenja se između patcheva; obrasci prate linije koje čitaju trackeri ubistava
zajednice (npr. <https://github.com/DimmaDont/all-slain>, MIT - samo
činjenice), a sve što se ne poklopi preskače se, ne pogađa se. `pos` vozila
je relativan prema zoni i čuva se samo kao tekst: koordinate se ne crtaju.

Svaka linija se čuva cijela u sirovom sidecaru sesije (3DHeat-ovo pravilo
konvertera), poklopila se ili ne: `type` je oznaka linije u ugaonim zagradama (`Actor
Death`, `Spawn Flow`, ...), inače njena prva riječ u uglastim zagradama (`Notice`,
`CSessionManager::OnClientSpawned`), inače `untagged`; linija bez
vremenske oznake je `untimed`.

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | ne |
| Osa gore | `y` |
| Jedinice | položaji se ne bilježe |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `log`: čita samo ono što igra ili platforma daje (datoteke koje igra piše dok radi), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- `<Actor Death>`: žrtva, ubica, oružje i njegova klasa, vrsta štete, zona; NPC ili igrač
- `<Vehicle Destruction>`: vozilo, zona, položaj relativan prema zoni kao tekst, vozač, uzrok, način, nivo uništenja
- ciljevi `<Quantum Navtarget>`, `<Changing Solar System>`, `OnClientSpawned`, respawnovi u bolnici, onesposobljavanja s uzrocima, `EndSession`
- igračev handle iz `<AccountLoginCharacterStatus_Character>` ili iz linije prijave

**Čuva se sirovo**

- svaka linija Game.log cijela, `type` = njena oznaka u ugaonim zagradama (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), inače njena prva riječ u uglastim zagradama (`Notice`, `CSessionManager::OnClientSpawned`, ...), inače `untagged`; linije bez vremenske oznake (zaglavlje loga, prelomljen tekst) kao `untimed`; `used` gdje je linija postala red

**Nije dostupno**

- položaji: log ne daje nijedan u okviru koji se može crtati (`pos` uništenog vozila relativan je prema zoni čije se mjesto ne bilježi)
- sve iz procesa ili mreže igre: Star Citizen koristi Easy Anti-Cheat; čita se samo log datoteka
- logovi ranijih pokretanja (`logbackups`): Game.log svakog pokretanja čuva se kad se igra
- linije u formatu koji patch promijeni: čuvaju se sirove, ponovo se dekodiraju kad se novi oblik upozna

**Veličina**: Game.log raste oko 5-15 MB na sat igranja (više u prometnim područjima i uz greške); zstd u heat.raw.parquet to smanjuje otprilike na desetinu

## Provjereno {#verified}

testirano na sintetičkim linijama Game.log u formatu koji dokumentiraju trackeri zajednice; nije testirano na igri

## Izvor {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
