---
title: "Path of Exile (loggfiler)"
nav_order: 35
lang: "no"
source: game-poe.md
source_hash: "b5783b5a5690"
nav_exclude: true
search_exclude: true
---
# Path of Exile (loggfiler) {#path-of-exile-log-files}

Mens du spiller Path of Exile, leser watcheren filene spillet skriver, og lagrer det som skjedde, slik at du senere kan se på det som statistikk og en tidslinje.

*Tekniske detaljer: adapter `poe`, type [`log`](sources-and-rules.md); den kjører mens `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` eller `PathOfExile_x64_KG.exe` går og ser etter nye data hvert 0,5 s.*

## Hva som tas opp {#what-is-recorded}

- soner gått inn i, med områdenivå, områdeid og dens seed
- nivåopprykk, med klasse og nivå
- dødsfall ("has been slain")
- spillere som kommer inn i og går ut av området, whisper inn og ut, handelsforespørsler, aksepterte handler
- hver Client.txt-linje av denne økten hel i `heat.raw.parquet`
- dødsfall, nivåer fått, høyeste nivå, soner gått inn i, ulike soner, whisper, handelsforespørsler, handler

## Hvor det kommer fra {#where-it-comes-from}

&lt;installasjon>\logs\Client.txt til Path of Exile eller Path of Exile 2 (følges; installasjonsmappen er den kjørende kjørbare filens)

## Slik slår du det på {#how-to-switch-it-on}

Ingenting må slås på: watcheren leser kilden slik spillet eller plattformen gir den.

## Slik fungerer det {#how-it-works}

Path of Exile og Path of Exile 2: klientloggen, `<installasjon>\logs\Client.txt`.

Begge spill legger til i én Client.txt i installasjonsmappen sin så lenge de er installert (den vokser over flere starter). Linjene ser slik ut:

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- lokal tid, en millisekundteller, en hash, nivået og tråden, og så det chatvinduet viser. Meldingene er den engelske klientens; en klient på et annet språk skriver dem oversatt, og de forstås ikke her. Ingen gir en posisjon. Formatet er ikke dokumentert av Grinding Gear Games; det er spillets rene tekstlogg, slik fellesskapsverktøy (handelshjelpere, nivåguider) har lest den i årevis - f.eks. <https://github.com/klayveR/poe-log-monitor> (MIT) for hendelseslisten.

Installasjonsmappen er den kjørende kjørbare filens; uten en søkes Steam-bibliotekene og den frittstående klientens standardmappe.

Hver linje i denne økten tas vare på hel i øktens rå sidefil (3DHeats konverteringsregel), enten den betyr noe her eller ikke: `type` er nivået og loggeren i klammene (`INFO Client`, `DEBUG Client`, `WARN Client`, ...), en tidsstemplet linje uten klammer er `untagged`, og en linje uten tidsstempel er `untimed`.

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | nei |
| Opp-akse | `y` |
| Enheter | ingen posisjoner tatt opp |
| Speilet for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse legges i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s fotnote, slik at 3DHeat-vieweren selv vender og skalerer radene - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "tillatt (leser bare det spillet publiserer)".
- Type `log`: den leser bare det spillet eller plattformen gir ut (filer spillet skriver mens det kjører), så den tar opp også i nettspill, ikke bare frakoblet; flagget avgjør bare om minne noensinne får leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

En nøkkel i klammer fullføres ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt, eller fra spillets egne statistikknavn, står ikke på denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slippes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt tatt vare på med navn; `used` markerer det som også ble rader), og `meta.json`s `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Leses**

- `You have entered <sone>`, med områdenivået, områdeid-en og seeden fra `Generating level`-linjen før den
- `<navn> (<klasse>) is now level <n>`, `<navn> has been slain`, spillere som kommer inn i og går ut av området, whisper inn og ut (med om de er en handelsforespørsel), aksepterte og avbrutte handler

**Tatt vare på rått**

- hver linje i denne økten hel, `type` = nivået og loggeren i klammene (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` der den ble en rad: global-, handels-, gruppe- og gildechat, `Connecting to instance server`, AFK- og DND-meldinger, svarene på chattkommandoer som `/played` og `/deaths`, klientens lasting- og motorlinjer - tatt vare på, ikke gjort om til rader ennå
- en tidsstemplet linje uten klammer (`***** LOG FILE OPENING *****`) som `untagged`, en linje uten tidsstempel som `untimed`

**Ikke tilgjengelig**

- posisjoner: ingenting i loggen gir en
- hva en klient på et annet språk skriver: linjene tas vare på, men bare de engelske meldingene gjøres om til rader
- linjer fra tidligere starter: Client.txt vokser over flere starter; linjer stemplet før denne kjøringen av spillet er latt være (de ble tatt vare på da de ble spilt)
- drap, skade, plunder og passivtreet: spillet logger dem ikke

**Størrelse**: Client.txt vokser omtrent 0,3-3 MB i timen (mest fra DEBUG-linjer under lasting av områder, mer med travel handelschat); zstd i `heat.raw.parquet` gjør det omtrent en tiendedel

## Verifisert {#verified}

testet på syntetiske Client.txt-linjer i spillets format; ikke testet mot spillet

## Kilde {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
