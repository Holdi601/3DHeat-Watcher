---
title: "Minecraft (loggfiler)"
nav_order: 33
lang: "sv"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (loggfiler) {#minecraft-log-files}

När du spelar Minecraft läser watchern de filer som spelet skriver och sparar vad som hände, så att du senare kan titta på det på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `minecraft`, slag [`log`](sources-and-rules.md); den körs medan `javaw.exe` eller `java.exe` är igång och letar efter ny data var 0,5 s.*

## Vad som spelas in {#what-is-recorded}

- egen och andra spelares position (block = m, y uppåt) varje gång världen sparas, dimensionen som session
- uppstånd med position när en spelare loggar in på den (integrerade) servern
- inloggningar, utloggningar, dödsfall med dödsmeddelandet, framsteg, chattrader
- dödsfall, framsteg, chattmeddelanden; från statistikfilen: speltid, sträcka, dödade mobs och spelare, hopp, skada, block brutna, föremål tillverkade (denna sessions andel)
- varje loggrad och varje sparad statistik-, framsteg- och spelarfil helt i heat.raw.parquet

## Var datan kommer ifrån {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (följs), saves\\&lt;värld>\stats\\&lt;uuid>.json och saves\\&lt;värld>\playerdata\\&lt;uuid>.dat / level.dat (gzip-NBT), lästa när spelet sparar dem

## Så slår du på det {#how-to-switch-it-on}

Inget behöver slås på: watchern läser källan så som spelet eller plattformen tillhandahåller den.

## Så fungerar det {#how-it-works}

Minecraft (Java Edition): loggen, statistiken och spelarfilerna som spelet skriver.

Var (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - spelets logg, ny vid varje start (den gamla packas
  i en daterad .log.gz). Rader `[hh:mm:ss] [tråd/NIVÅ]: meddelande`
  (modladdare skriver `[ddMMMyyyy hh:mm:ss.mmm] [tråd/NIVÅ] [loggare/]: ...`).
  Det spelarna ser i chatten finns där: inloggningar och utloggningar, dödsmeddelanden,
  framsteg, chatt - den integrerade servern i en enspelarvärld skriver
  samma rader en gång till, så en rad som upprepas inom samma sekund räknas
  en gång. "Setting user: <namn>" anger spelaren; serverns
  "<namn>[...] logged in with entity id N at (x, y, z)" anger var de
  dök upp.
* `saves\<värld>\stats\<uuid>.json` - statistikskärmen, skriven när världen
  sparas (autospara var några minuter, och vid utgång): `stats` ->
  `minecraft:custom` (play_time i ticks, mob_kills, \*_one_cm sträckor, jump,
  ...), `minecraft:mined`, `minecraft:crafted`, ... Summor för världen; sessionens
  siffror är skillnaden mot vad filen sade när spelet startade. Format: <https://minecraft.wiki/w/Statistics>
* `saves\<värld>\playerdata\<uuid>.dat` (och `level.dat` -> Data -> Player
  för en enspelarvärd) - gzip-komprimerad NBT, skriven vid samma sparningar:
  `Pos` [x, y, z] doubles, `Rotation` [yaw, pitch], `Dimension`
  ("minecraft:overworld"; en int 0/-1/1 före 1.16). NBT enligt
  <https://minecraft.wiki/w/NBT_format> - läst här av en liten läsare vi själva skrivit.
* `saves\<värld>\advancements\<uuid>.json` - framstegsskärmens framsteg,
  skriven vid samma sparningar.

Koordinaterna är block, ett block en meter, y uppåt; x österut, z söderut - en högerhänt
ram, ritad som den är. Positionerna kommer bara när världen sparas, så en rutt är några
punkter per autospara, inte ett spår; dimensionen är `session`, så Nether
ritas inte över Overworld.

Allt som läses sparas helt i sessionens råa sidofil (3DHeats
konverterarregel): varje loggrad under sin nivå (`INFO`, `WARN`, `ERROR`, ...; en rad
utan den hakparentesade rubriken, till exempel en stackspårning, som `untagged`), och
varje sparad fil under sitt slag (`stats`, `advancements`, `playerdata`,
`level.dat`) - JSON som text, NBT som sina byte. En statistikfils siffror förstås
bara mot vad den sade när spelet startade, så den första kopian sparas också
(`baseline`), första gången filen ändras.

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Upp-axel | `y` |
| Enheter | block (1 block = 1 m) |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåtet (läser bara det spelet publicerar)".
- Slag `log`: den läser bara det spelet eller plattformen lämnar ut (filer som spelet skriver medan det körs), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- latest.log: spelarens namn (`Setting user`), inloggningar med position, inträden, utträden, dödsfall med dödsmeddelandet, framsteg, chattrader, att servern stoppas
- stats/<uuid>.json: speltid, sträcka, dödade mobs och spelare, hopp, skada given och tagen, block brutna, föremål tillverkade - denna sessions andel
- playerdata/<uuid>.dat och level.dat (NBT): position, dimension, yaw, pitch, hälsa, erfarenhetsnivå

**Sparas råa**

- varje latest.log-rad helt, `type` = dess nivå (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) med loggerns tråd i `thread`, `used` där den blev en rad; en rad utan den hakparentesade rubriken (en stackspårning, en mods banderoll) som `untagged`
- varje stats/<uuid>.json helt som text, `type` `stats` (`used`: dess siffror finns i statistiken), med dess första kopia från spelets start som `baseline`
- varje advancements/<uuid>.json helt som text, `type` `advancements` (varje kriterium och när det uppfylldes; ännu inte gjorda till rader)
- varje playerdata/<uuid>.dat och level.dat helt som byte (gzip-NBT), `type` `playerdata` / `level.dat`, `used` där den gav en position: inventarium, enderkista, effekter, spawnpunkt, spelregler, världens seed och tid finns bara här
- varje sparad fil har `world` och `file` (dess sökväg under `saves`)

**Finns inte**

- ett positionsspår: spelet skriver spelarens position bara när världen sparas (var några minuter och vid utgång)
- positioner på en server som någon annan är värd för: dess världsfiler ligger på servern, inte här; bara loggen läses då
- världen självt (region-filerna .mca, entiteter, data/\*.dat-kartor och raids): stor, och terrängen, inte spelet
- tidigare sessioners loggar (logs/\*.log.gz): sparas när de spelades
- Bedrock Edition: den skriver ingen sådan logg eller sådana filer

**Storlek**: latest.log 0,1-2 MB per timme (mer med mods); en statistikfil 5-50 KB och en spelarfil 5-100 KB per autospara, level.dat 1-20 KB - ungefär 1-5 MB per timme sammanlagt; zstd i heat.raw.parquet gör texten till ungefär en tiondel (NBT-filerna är redan gzip)

## Verifierat {#verified}

testad på syntetiska loggrader, statistik-JSON och NBT-filer byggda efter de publicerade formaten; ännu inte testad mot spelet

## Källa {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
