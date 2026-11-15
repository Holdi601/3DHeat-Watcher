---
title: "Minecraft (logfiler)"
nav_order: 33
lang: "da"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (logfiler) {#minecraft-log-files}

Mens du spiller Minecraft, læser watcheren de filer, spillet skriver, og gemmer hvad der skete, så du senere kan se det på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `minecraft`, type [`log`](sources-and-rules.md); den kører, mens `javaw.exe` eller `java.exe` kører, og leder efter nye data hver 0.5 s.*

## Hvad der registreres {#what-is-recorded}

- egen og andre spilleres position (blokke = m, y op) hver gang verden gemmes, dimensionen som session
- spawn med position, når en spiller logger ind på den (integrerede) server
- indlogninger, udlogninger, dødsfald med dødsbeskeden, fremskridt (advancements), chatlinjer
- dødsfald, fremskridt, chatbeskeder; fra statistikfilen: spilletid, distance, mob- og spillerdrab, hop, skade, udgravede blokke, fremstillede items (denne sessions andel)
- hver loglinje og hver gemt statistik-, fremskridts- og spillerfil hel i heat.raw.parquet

## Hvor data kommer fra {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (fulgt), saves\\&lt;world>\stats\\&lt;uuid>.json og saves\\&lt;world>\playerdata\\&lt;uuid>.dat / level.dat (gzip NBT), læst når spillet gemmer dem

## Sådan slår du det til {#how-to-switch-it-on}

Der er intet at slå til: watcheren læser kilden, som spillet eller platformen stiller den til rådighed.

## Sådan virker det {#how-it-works}

Minecraft (Java Edition): loggen, statistikken og spillerfilerne, spillet skriver.

Hvor (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - spillets log, ny ved hver start (den gamle pakkes
  i en datostemplet .log.gz). Linjer `[hh:mm:ss] [tråd/LEVEL]: besked`
  (modloadere skriver `[ddMMMyyyy hh:mm:ss.mmm] [tråd/LEVEL] [logger/]: ...`).
  Det spillerne ser i chatten, står i den: indlogninger og udlogninger, dødsbeskeder,
  fremskridt, chat - den integrerede server i en enkeltspillerverden skriver
  de samme linjer én gang til, så en linje gentaget inden for samme sekund tæller
  én gang. "Setting user: <name>" navngiver spilleren; serverens
  "<name>[...] logged in with entity id N at (x, y, z)" angiver, hvor de
  dukkede op.
* `saves\<world>\stats\<uuid>.json` - statistikskærmen, skrevet når verden gemmes
  (autosave hvert par minut, og ved udgang): `stats` ->
  `minecraft:custom` (play_time i ticks, mob_kills, \*_one_cm afstande, jump,
  ...), `minecraft:mined`, `minecraft:crafted`, ... Totaler for verdenen; sessionens
  tal er forskellen til det, filen sagde, da spillet startede. Format: <https://minecraft.wiki/w/Statistics>
* `saves\<world>\playerdata\<uuid>.dat` (og `level.dat` -> Data -> Player
  for en enkeltspillervært) - gzip-komprimeret NBT, skrevet ved de samme gemninger:
  `Pos` [x, y, z] doubles, `Rotation` [yaw, pitch], `Dimension`
  ("minecraft:overworld"; et int 0/-1/1 før 1.16). NBT efter <https://minecraft.wiki/w/NBT_format> - læst her af en lille læser af vores egen.
* `saves\<world>\advancements\<uuid>.json` - fremskridtsskærmens fremdrift,
  skrevet ved de samme gemninger.

Koordinater er blokke, en blok er en meter, y op; x øst, z syd - et højrehåndet
koordinatsystem, tegnet som det er. Positioner kommer kun, når verden gemmes, så en
rute er få punkter pr. autosave, ikke et spor; dimensionen er
`session`, så Nether tegnes ikke oven på Overworld.

Alt, der læses, gemmes hel i sessionens råsidefil (3DHeats konverterregel): hver loglinje under sit niveau (`INFO`, `WARN`, `ERROR`, ...; en linje uden det hakkede hoved, såsom en stacktrace, som `untagged`), og hver gemt fil under sin type (`stats`, `advancements`, `playerdata`, `level.dat`) - JSON som tekst, NBT som sine bytes. En statistikfils tal forstås kun ud fra, hvad den sagde, da spillet startede, så den første kopi gemmes også (`baseline`), første gang filen ændrer sig.

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | ja |
| Op-akse | `y` |
| Enheder | blokke (1 blok = 1 m) |
| Spejlet for vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, ind i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "tilladt (læser kun det spillet udleverer)".
- Type `log`: den læser kun det, spillet eller platformen udleverer (filer spillet skriver, mens det kører), så den optager også i onlinespil såvel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der registreres {#statistics-recorded}

Statistiknøgler, som denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text`, plus ethvert felt gemt under sit navn; `used` markerer det, der også blev rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- latest.log: spillerens navn (`Setting user`), indlogninger med position, indgange, udgange, dødsfald med dødsbeskeden, fremskridt, chatlinjer, serveren der stopper
- stats/<uuid>.json: spilletid, distance, mob- og spillerdrab, hop, skade givet og taget, udgravede blokke, fremstillede items - denne sessions andel
- playerdata/<uuid>.dat og level.dat (NBT): position, dimension, yaw, pitch, liv, XP-niveau

**Gemt råt**

- hver latest.log-linje hel, `type` = dens niveau (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) med loggerens tråd i `thread`, `used` hvor den blev til en række; en linje uden det hakkede hoved (en stacktrace, en mods banner) som `untagged`
- hver stats/<uuid>.json hel som tekst, `type` `stats` (`used`: dens tal står i statistikken), med dens første kopi fra spillets start som `baseline`
- hver advancements/<uuid>.json hel som tekst, `type` `advancements` (hvert kriterium og hvornår det blev opfyldt; endnu ikke lavet om til rækker)
- hver playerdata/<uuid>.dat og level.dat hel som bytes (gzip NBT), `type` `playerdata` / `level.dat`, `used` hvor den gav en position: inventar, enderkiste, effekter, spawnpunkt, spilregler, verdensfrø og tid findes kun her
- hver gemt fil har `world` og `file` (dens sti under `saves`)

**Ikke tilgængeligt**

- et positionsspor: spillet skriver spillerens position først, når verden gemmes (hvert par minut og ved udgang)
- positioner på en server, en anden er vært for: dens verdensfiler ligger på serveren, ikke her; kun loggen læses så
- selve verdenen (region .mca-filer, entiteter, data/\*.dat-kort og raids): stor, og det er terrænet, ikke spillet
- tidligere sessioners logs (logs/\*.log.gz): gemmes, når de blev spillet
- Bedrock Edition: den skriver ingen sådan log eller filer

**Størrelse**: latest.log 0.1-2 MB i timen (mere med mods); en statistikfil 5-50 KB og en spillerfil 5-100 KB pr. autosave, level.dat 1-20 KB - cirka 1-5 MB i timen i alt; zstd i heat.raw.parquet gør teksten cirka en tiendedel (NBT-filerne er allerede gzip)

## Verificeret {#verified}

testet på syntetiske logLinjer, statistik-JSON og NBT-filer bygget efter de offentliggjorte formater; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
