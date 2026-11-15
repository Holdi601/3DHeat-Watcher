---
title: "Path of Exile (logfiler)"
nav_order: 35
lang: "da"
source: game-poe.md
source_hash: "b5783b5a5690"
nav_exclude: true
search_exclude: true
---
# Path of Exile (logfiler) {#path-of-exile-log-files}

Mens du spiller Path of Exile, læser watcheren de filer, spillet skriver, og gemmer det, der skete, så du senere kan se det som statistik og en tidslinje.

*Tekniske detaljer: adapter `poe`, type [`log`](sources-and-rules.md); den kører, mens `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` eller `PathOfExile_x64_KG.exe` kører, og leder efter nye data hver 0.5 s.*

## Hvad der registreres {#what-is-recorded}

- zoner betrådt med områdeniveau, områdeid og dets seed
- niveauopgange med klasse og niveau
- dødsfald ("has been slain")
- spillere, der kommer ind i og forlader området, hvisken ind og ud, handelsanmodninger, handler accepteret
- hver Client.txt-linje fra denne session hel i heat.raw.parquet
- dødsfald, niveauer opnået, højeste niveau, zoner betrådt, forskellige zoner, hvisken, handelsanmodninger, handler

## Hvor data kommer fra {#where-it-comes-from}

&lt;install>\logs\Client.txt for Path of Exile eller Path of Exile 2 (følges; installationsmappen er den kørende programfils)

## Sådan slår du det til {#how-to-switch-it-on}

Der skal ikke slås noget til: watcheren læser kilden, som spillet eller platformen udleverer den.

## Sådan virker det {#how-it-works}

Path of Exile og Path of Exile 2: klientlogget, `<install>\logs\Client.txt`.

Begge spil skriver til én Client.txt i deres installationsmappe, så længe de er installeret
(den vokser på tværs af starter). Linjerne ser sådan ud

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- lokal tid, en millisekundtæller, en hash, niveauet og tråden, og derefter det chatvinduet viser. Beskederne er den engelske klients; en klient på et andet sprog skriver dem oversat og forstås ikke her. Intet giver en position. Formatet er ikke dokumenteret af Grinding Gear Games; det er spillets rene tekstlog, sådan som community-værktøjer (handelshjælpere, niveauguider) har læst det i årevis - f.eks. <https://github.com/klayveR/poe-log-monitor> (MIT) for hændelseslisten.

Installationsmappen er den kørende programfils; uden en sådan søges Steam-bibliotekerne
og den selvstændige klients standardmappe.

Hver linje i denne session gemmes hel i kørslens rå sidefil (3DHeats konverterregel),
uanset om den betyder noget her: `type` er niveauet og loggeren i dens klammer (`INFO Client`, `DEBUG Client`, `WARN Client`, ...),
en stemplet linje uden klammer er `untagged`, en linje uden tidsstempel `untimed`.

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | nej |
| Op-akse | `y` |
| Enheder | ingen positioner registreret |
| Spejlet til vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver kørsels `meta.json` (`axes`) og, når kørslen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser det som "tilladt (læser kun det spillet udgiver)".
- Type `log`: den læser kun det spillet eller platformen udleverer (filer spillet skriver, mens det kører), så den optager også i onlinespil og offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: læses **aldrig** af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Registrerede statistikker {#statistics-recorded}

Statistiknøgler, som adapterens kode sætter ved navn (hver kørsels `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, og aldrig smides væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i kørslens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter, der gemmes under deres navn; `used` markerer, hvad der også blev til rækker), og `selfCheck.completeness` i `meta.json` tæller hver `type` - `lost` er 0.

**Læst**

- `You have entered <zone>`, med områdeniveauet, områdeid'et og seedet fra `Generating level`-linjen før den
- `<name> (<class>) is now level <n>`, `<name> has been slain`, spillere, der kommer ind i og forlader området, hvisken ind og ud (med om det er en handelsanmodning), handler accepteret og annulleret

**Gemt råt**

- hver linje fra denne session hel, `type` = niveauet og loggeren i dens klammer (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` hvor den blev til en række: global-, handels-, gruppe- og gildechat, `Connecting to instance server`, AFK- og DND-meddelelser, svarene på chatkommandoer såsom `/played` og `/deaths`, klientens indlæsnings- og motorlinjer - gemt, endnu ikke gjort til rækker
- en stemplet linje uden klammer (`***** LOG FILE OPENING *****`) som `untagged`, en linje uden tidsstempel som `untimed`

**Ikke tilgængeligt**

- positioner: intet i logget giver en
- hvad en klient på et andet sprog skriver: linjerne gemmes, men kun de engelske beskeder gøres til rækker
- linjer fra tidligere starter: Client.txt vokser på tværs af starter; linjer stemplet før denne kørsel af spillet efterlades (de blev gemt, da de blev spillet)
- drab, skade, loot og passivt træ: spillet logger dem ikke

**Størrelse**: Client.txt vokser cirka 0,3-3 MB i timen (mest fra DEBUG-linjer under indlæsning af områder, mere med travl handelschat); zstd i heat.raw.parquet gør det cirka til en tiendedel

## Verificeret {#verified}

testet på syntetiske Client.txt-linjer i spillets format; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Genereret fra adapteren af tools/gen_game_pages.py; ret adapteren og kør den igen i stedet for at redigere denne side. -->
