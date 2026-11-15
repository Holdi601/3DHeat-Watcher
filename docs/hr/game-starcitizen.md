---
title: "Star Citizen (datoteke dnevnika)"
nav_order: 42
lang: "hr"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (datoteke dnevnika) {#star-citizen-log-files}

Dok igrate Star Citizen, watcher čita datoteke koje igra piše i sprema što se dogodilo, pa to kasnije možete pogledati kao statistiku i vremensku crtu.

*Tehnički detalji: adapter `starcitizen`, vrsta [`log`](sources-and-rules.md); radi dok je `StarCitizen.exe` pokrenut i traži nove podatke svakih 0,5 s.*

## Što se bilježi {#what-is-recorded}

- smrti sa žrtvom, ubojicom, oružjem, vrstom štete i zonom (igrači i NPC-ovi)
- onesposobljena i uništena vozila, s vozačem, uzrokom i zonom
- ciljevi kvantnog putovanja, promjene solarnog sustava, pojavljivanja, ponovna pojavljivanja, onesposobljavanja
- svaki redak Game.log-a cijel u heat.raw.parquet
- ubojstva (igrač i NPC), smrti, samoubojstva, uništena i izgubljena vozila, kvantni skokovi

## Odakle dolazi {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (mapa verzije pokrenute StarCitizen.exe), samo datoteka dnevnika koju igra piše - igra s Easy Anti-Cheat-om: ništa ne dira njezin proces

## Kako to uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Star Citizen: vlastiti dnevnik klijenta, `<install>\StarCitizen\LIVE\Game.log`.

Igra Game.log piše iznova pri svakom pokretanju (prethodni ide u `logbackups\`). Čita se samo ta datoteka: Star Citizen koristi Easy Anti-Cheat, a ovdje se ništa ne približava procesu igre. Redci počinju UTC vremenom i razinom, pa oznakom u kutnim zagradama:

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

(prelomljeno ovdje; u datoteci je svaki redak u jednom retku). Zona smrti obično je brod u kojem je žrtva sjedila, a ne mjesto. Format Cloud Imperium ne dokumentira i mijenja se između zakrpa; obrasci slijede redke koje čitaju zajednički alati za praćenje ubojstava (npr. <https://github.com/DimmaDont/all-slain>, MIT - samo činjenice), a sve što se ne podudara preskače se, ne pogađa. `pos` vozila relativan je zoni i čuva se samo kao tekst: nijedna koordinata se ne crta.

Svaki redak čuva se cijel u sirovom pratećem dijelu sesije (pravilo pretvarača 3DHeat), bez obzira podudara li se: `type` je oznaka retka u kutnim zagradama (`Actor Death`, `Spawn Flow`, ...), inače njegova prva riječ u zagradama (`Notice`, `CSessionManager::OnClientSpawned`), inače `untagged`; redak bez vremena je `untimed`.

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Bilježe se pozicije | nema |
| Os prema gore | `y` |
| Jedinice | nema pozicija |
| Zrcaljeno za preglednik | nema |
| Mjerilo jedinice (`scale`: preglednik ovim množi pozicije) | 1 |

Ovo ide u `meta.json` (`axes`) svake sesije i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `log`: čita samo ono što igra ili platforma daje (datoteke koje igra piše dok radi), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: adapter je **nikad** ne čita. Memoriju čitaju samo adapteri vrste `memory`, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` u `meta.json` svake sesije i tablica `stats` u `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz imena statistike same igre nisu na ovom popisu; odjeljak „Što se bilježi“ ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeata: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json`-u broji svaki `type` - `lost` je 0.

**Čita se**

- `<Actor Death>`: žrtva, ubojica, oružje i njegova klasa, vrsta štete, zona; NPC ili igrač
- `<Vehicle Destruction>`: vozilo, zona, pozicija relativna zoni kao tekst, vozač, uzrok, način, razina uništenja
- `<Quantum Navtarget>` ciljevi, `<Changing Solar System>`, `OnClientSpawned`, ponovna pojavljivanja u bolnici, onesposobljavanja s uzrocima, `EndSession`
- igračev handle iz `<AccountLoginCharacterStatus_Character>` ili retka prijave

**Čuva se sirovo**

- svaki redak Game.log-a cijel, `type` = oznaka retka u kutnim zagradama (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), inače njegova prva riječ u zagradama (`Notice`, `CSessionManager::OnClientSpawned`, ...), inače `untagged`; redci bez vremena (zaglavlje dnevnika, prelomljeni tekst) kao `untimed`; `used` gdje je redak postao retkom

**Nije dostupno**

- pozicije: dnevnik ih ne daje u okviru koji se može nacrtati (`pos` uništenog vozila relativan je zoni čije mjesto nije zabilježeno)
- sve iz procesa ili mreže igre: Star Citizen koristi Easy Anti-Cheat; čita se samo datoteka dnevnika
- dnevnici ranijih pokretanja (`logbackups`): Game.log svakog pokretanja čuva se kad se odigra
- redci u obliku koji zakrpa mijenja: čuvaju se sirovi, dekodiraju se ponovno kad se poznaje novi oblik

**Veličina**: Game.log raste oko 5-15 MB po satu igre (više u zauzetim područjima i uz greške); zstd u heat.raw.parquet ga smanjuje na otprilike desetinu

## Provjereno {#verified}

testirano na sintetičkim redcima Game.log-a u formatu koji dokumentiraju zajednički alati za praćenje; neprovjereno u samoj igri

## Izvor {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
