---
title: "Minecraft (loggfiler)"
nav_order: 33
lang: "no"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (loggfiler) {#minecraft-log-files}

Mens du spiller Minecraft, leser watcheren filene spillet skriver, og lagrer det som skjedde, slik at du kan se på det senere på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `minecraft`, type [`log`](sources-and-rules.md); den kjører mens `javaw.exe` eller `java.exe` kjører, og ser etter nye data hvert 0,5 s.*

## Hva som lagres {#what-is-recorded}

- egen og andre spilleres posisjon (blokker = m, y opp) hver gang verdenen lagres, dimensjon som økt
- spawn med posisjon når en spiller logger inn på (den integrerte) serveren
- innlogginger, utlogginger, dødsfall med dødsmeldingen, fremskritt, chatlinjer
- dødsfall, fremskritt, chatmeldinger; fra statistikkfilen: spilletid, distanse, drap på mobs og spillere, hopp, skade, utvunnede blokker, craftede gjenstander (denne øktens andel)
- hver loggelinje og hver lagret stats-, fremskritts- og spillerfil hel i heat.raw.parquet

## Hvor dataene kommer fra {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (fulgt), saves\\&lt;verden>\stats\\&lt;uuid>.json og saves\\&lt;verden>\playerdata\\&lt;uuid>.dat / level.dat (gzip NBT), lest når spillet lagrer dem

## Slik slår du det på {#how-to-switch-it-on}

Du må ikke slå noe på: watcheren leser kilden slik spillet eller plattformen leverer den.

## Slik fungerer det {#how-it-works}

Minecraft (Java Edition): loggen, statistikken og spillerfilene spillet skriver.

Hvor (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - spillets logg, ny ved hver start (den gamle pakkes
  inn i en datert .log.gz). Linjer `[tt:mm:ss] [tråd/NIVÅ]: melding`
  (modlastere skriver `[ddMMMyyyy tt:mm:ss.mmm] [tråd/NIVÅ] [logger/]: ...`).
  Det spillerne ser i chatten står der: innlogginger og utlogginger, dødsmeldinger,
  fremskritt, chat - den integrerte serveren i en enspillerverden skriver
  de samme linjene én gang til, så en linje som gjentas innenfor samme sekund telles
  én gang. «Setting user: &lt;navn>» forteller hvem spilleren er; serverens
  «&lt;navn>[...] logged in with entity id N at (x, y, z)» forteller hvor de
  dukket opp.
* `saves\<verden>\stats\<uuid>.json` - statistikkskjermen, skrevet når verdenen lagres (autolagring hvert par minutt, og ved avslutning): `stats` ->
  `minecraft:custom` (play_time i tikk, mob_kills, \*_one_cm-distanser, jump,
  ...), `minecraft:mined`, `minecraft:crafted`, ... Summer for verdenen; øktens tall er forskjellen til det filen sa da spillet startet. Format: <https://minecraft.wiki/w/Statistics>
* `saves\<verden>\playerdata\<uuid>.dat` (og `level.dat` -> Data -> Player
  for en enspillervert) - gzip-komprimert NBT, skrevet ved de samme lagringene:
  `Pos` [x, y, z] som doubler, `Rotation` [yaw, pitch], `Dimension`
  («minecraft:overworld»; et int 0/-1/1 før 1.16). NBT etter
  <https://minecraft.wiki/w/NBT_format> - leses her av en liten leser vi har selv.
* `saves\<verden>\advancements\<uuid>.json` - fremskrittet på fremskrittsskjermen,
  skrevet ved de samme lagringene.

Koordinatene er blokker, én blokk per meter, y opp; x øst, z sør - et høyrehåndssystem, tegnet slik det er. Posisjoner kommer bare når verdenen lagres, så en rute er noen få punkter per autolagring, ikke et spor; dimensjonen er `session`, så Nether tegnes ikke over Overworld.

Alt som leses, lagres hele i øktens rå sidefil (3DHeat sin regel for konvertering): hver loggelinje under sitt nivå (`INFO`, `WARN`, `ERROR`, ...; en linje uten det klammeparentesede hodet, som en stakkspor, som `untagged`), og hver lagret fil under sin type (`stats`, `advancements`, `playerdata`, `level.dat`) - JSON som tekst, NBT som sine bytes. En stats-fils tall forstås bare mot det den sa da spillet startet, så den første kopien lagres også (`baseline`), første gang filen endrer seg.

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner lagres | ja |
| Opp-akse | `y` |
| Enheter | blokker (1 blokk = 1 m) |
| Speilvendt for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet` sin footer, så 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som «tillatt (leser bare det spillet publiserer)».
- Type `log`: den leser bare det spillet eller plattformen gir ut (filer spillet skriver mens det kjører), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som lagres {#statistics-recorded}

Statistikknøklene denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

En nøkkel i klammeparenteser blir fullført under kjøring (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell med spillets felter eller fra spillets egne statistikknavn, står ikke på listen; «Hva som lagres» over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeat sin [regel for konvertering](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller lagres, og slettes aldri. I tillegg til radene blir hver pakke, side, linje eller respons adapteren mottar, lagret uendret i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt som beholdes med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- latest.log: spillerens navn (`Setting user`), innlogginger med posisjon, innlogginger, utlogginger, dødsfall med dødsmeldingen, fremskritt, chatlinjer, at serveren stopper
- stats/&lt;uuid>.json: spilletid, distanse, drap på mobs og spillere, hopp, skade gjort og tatt, utvunnede blokker, craftede gjenstander - denne øktens andel
- playerdata/&lt;uuid>.dat og level.dat (NBT): posisjon, dimensjon, yaw, pitch, helse, XP-nivå

**Lagres uendret**

- hver linje i latest.log hel, `type` = dens nivå (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) med loggerens tråd i `thread`, `used` der den ble til en rad; en linje uten det klammeparentesede hodet (en stakkspor, en mods banner) som `untagged`
- hver stats/&lt;uuid>.json hel som tekst, `type` `stats` (`used`: tallene er i statistikken), med første kopi fra spillets start som `baseline`
- hver advancements/&lt;uuid>.json hel som tekst, `type` `advancements` (hvert kriterium og når det ble oppfylt; ikke gjort om til rader ennå)
- hver playerdata/&lt;uuid>.dat og level.dat hel som bytes (gzip NBT), `type` `playerdata` / `level.dat`, `used` der den ga en posisjon: inventar, enderkiste, effekter, spawnpunkt, spilleregler, verdens frø og tid finnes bare her
- hver lagret fil har `world` og `file` (dens sti under `saves`)

**Ikke tilgjengelig**

- et posisjonsspor: spillet skriver spillerens posisjon bare når verdenen lagres (hvert par minutt og ved avslutning)
- posisjoner på en server noen andre er vert for: verdensfilene ligger på serveren, ikke her; bare loggen leses da
- selve verdenen (region .mca-filer, enheter og data/\*.dat-kart og raids): stor, og terrenget, ikke spillet
- logger fra tidligere økter (logs/\*.log.gz): lagres når de ble spilt
- Bedrock Edition: den skriver ingen slik logg eller slike filer

**Størrelse**: latest.log 0,1-2 MB per time (mer med mods); en stats-fil 5-50 KB og en spillerfil 5-100 KB per autolagring, level.dat 1-20 KB - omtrent 1-5 MB per time til sammen; zstd i heat.raw.parquet gjør teksten omtrent en tidel (NBT-filene er allerede gzip)

## Verifisert {#verified}

testet på syntetiske loggelinjer, stats-JSON og NBT-filer bygd etter de publiserte formatene; ikke testet mot spillet

## Kilde {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
