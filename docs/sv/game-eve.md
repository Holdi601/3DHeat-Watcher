---
title: "EVE Online (loggfiler)"
nav_order: 20
lang: "sv"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (loggfiler) {#eve-online-log-files}

När du spelar EVE Online läser watchern de filer spelet skriver och sparar vad som hände, så att du senare kan titta på det som statistik och en tidslinje.

*Tekniska detaljer: adapter `eve`, slag [`log`](sources-and-rules.md); den körs medan `exefile.exe` är igång och letar efter ny data var 0,5 s.*

## Vad som spelas in {#what-is-recorded}

- skada som delats ut och tagits emot, med det andra skeppet, piloten, korporationens ticker, vapnet och träffkvaliteten
- missar som delats ut och tagits emot
- belöningar utbetalda (NPC-dödanden) med ISK
- hopp mellan system
- varje rad i spel- och chattloggen helt i `heat.raw.parquet`
- skada som delats ut och tagits emot, träffar, missar, belöningsdödanden och ISK, hopp

## Var datan kommer ifrån {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt och Chatlogs\\\*.txt bredvid dem (varje fil som skrivits sedan klienten startade)

## Så slår du på det {#how-to-switch-it-on}

Inget behöver slås på: watchern läser källan så som spelet eller plattformen tillhandahåller den.

## Så fungerar det {#how-it-works}

EVE Online: klientens spelloggar, `Documents\EVE\logs\Gamelogs\*.txt`.

Klienten skriver en fil per karaktär och inloggning, `<yyyymmdd>_<hhmmss>[_<character id>].txt`; loggning till fil är på som standard. Flera klienter som kör samtidigt skriver var sin, så varje fil som skrivits sedan spelet startade följs. Huvud och rader (EVE-tiden är UTC):

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

(stridsraden är en rad i filen). Formateringstaggar tas bort innan matchning. Filen har över åren varit både UTF-8 och UTF-16; båda läses. Formatet är inte dokumenterat av CCP; det är klientens vanliga textlogg, läst på det sätt som communityns stridsloggverktyg läser den (t.ex. <https://docs.rs/crate/eve-log-parser>). Inga positioner.

Bredvid den: `Documents\EVE\logs\Chatlogs\<channel>_<yyyymmdd>_<hhmmss>[_<id>].txt`: en fil per chattkanal per inloggning (när chattloggning är på, klientens standard), UTF-16, ett huvud som anger kanalen och lyssnaren, sedan `[ yyyy.mm.dd hh:mm:ss ] Sender > message`.

Varje rad i båda sparas helt i sessionens råa sidfil (3DHeats konverterarregel): en spelloggsrad under sin kanal i hakparenteser (`combat`, `notify`, `bounty`, `None`, ...), en chattrad som `chat` med sin kanal, och huvudraderna som `gamelog header` / `chatlog header`.

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | nej |
| Upp-axel | `y` |
| Enheter | inga positioner registreras |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "allowed (reads only what the game publishes)".
- Slag `log`: den läser bara det spelet eller plattformen lämnar ut (filer som spelet skriver medan det körs), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- gamelogg `(combat)`-träffar som delats ut och tagits emot (mängd, andra piloten, korporationens ticker, skepp, vapen, träffkvalitet) och missar åt båda håll
- gamelogg `(bounty)`-utbetalningar med ISK, och raderna `Jumping from A to B`
- gamelogghuvudets Listener: vems logg det är

**Sparas råa**

- varje gamelogg-rad helt, `type` = dess kanal i hakparenteser (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), med `file` och `listener`; `used` där den blev en rad; huvudraderna som `gamelog header`
- varje chattloggsrad helt (Local, korporation, flotta, privata kanaler, `EVE System`-meddelanden som ett byte av Local-kanal vid ett hopp), `type` `chat`, med `channel`, `listener` och `file`; huvudraderna som `chatlog header`. Ännu inte gjorda till rader
- formateringstaggarna (`<color>`, `<b>`, `<font>`) finns kvar i råtexten; raderna har dem borttagna

**Finns inte**

- positioner: klienten skriver inga till sina loggar
- andra piloters strider: en gamelogg är lyssnarens egen
- loggar från tidigare inloggningar: varje inloggning skriver nya filer; de som är äldre än den här körningen av klienten läses inte igen
- chatt när spelaren har stängt av chattloggning i klientens inställningar
- klientens egna cache- och inställningsfiler: inte loggar, och inte dokumenterade

**Storlek**: en gamelogg är 0,1-2 MB per timme (mest i strid); chattloggar beror på vilka kanaler som är öppna - en livlig Local- eller flottkanal 0,5-3 MB per timme; zstd i `heat.raw.parquet` gör det ungefär en tiondel

## Verifierat {#verified}

testad på syntetiska gamelogg-rader i det format som communityns tolkare publicerat; ännu inte testad mot spelet

## Källa {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
