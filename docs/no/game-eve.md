---
title: "EVE Online (loggfiler)"
nav_order: 20
lang: "no"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (loggfiler) {#eve-online-log-files}

Mens du spiller EVE Online, leser watcheren filene spillet skriver, og lagrer det som skjedde, slik at du senere kan se på det som statistikk og en tidslinje.

*Tekniske detaljer: adapter `eve`, type [`log`](sources-and-rules.md); den kjører mens `exefile.exe` går og ser etter nye data hvert 0,5 s.*

## Hva som tas opp {#what-is-recorded}

- skade gitt og mottatt fra det andre skipet, piloten, korporasjonens forkortelse (ticker), våpen og trefferkvalitet
- bom gitt og mottatt
- belønninger utbetalt (NPC-drap) med ISK
- hopp mellom systemer
- hver gamelog- og chatlogg-linje hel i `heat.raw.parquet`
- skade gitt og mottatt, treff, bom, belønningsdrap og ISK, hopp

## Hvor det kommer fra {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt og Chatlogs\\\*.txt ved siden av dem (hver fil skrevet siden klienten startet)

## Slik slår du det på {#how-to-switch-it-on}

Ingenting må slås på: watcheren leser kilden slik spillet eller plattformen gir den.

## Slik fungerer det {#how-it-works}

EVE Online: klientens spillogger, `Documents\EVE\logs\Gamelogs\*.txt`.

Klienten skriver én fil per karakter per innlogging, `<yyyymmdd>_<hhmmss>[_<karakter-id>].txt`; logging til fil er på som standard. Flere klienter som kjører side om side skriver hver sin, så hver fil skrevet siden spillet startet følges. Topptekst og linjer (EVE-tid er UTC):

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

(combat-linjen er én linje i filen). Formateringstagger fjernes før matching. Filen har vært UTF-8 og UTF-16 gjennom årene; begge leses. Formatet er ikke dokumentert av CCP; det er klientens rene tekstlogg, lest slik fellesskapets kamploggverktøy leser den (f.eks. <https://docs.rs/crate/eve-log-parser>). Ingen posisjoner.

Ved siden av, `Documents\EVE\logs\Chatlogs\<kanal>_<yyyymmdd>_<hhmmss>[_<id>].txt`: én fil per chattkanal per innlogging (når chattlogging er på, klientens standard), UTF-16, en topptekst som nevner kanalen og lytteren, deretter `[ yyyy.mm.dd hh:mm:ss ] Avsender > melding`.

Hver linje i begge tas vare på hel i øktens rå sidefil (3DHeats konverteringsregel): en gamelog-linje under sin kanal i klammer (`combat`, `notify`, `bounty`, `None`, ...), en chattlinje som `chat` med sin kanal, og topptekstlinjene som `gamelog header` / `chatlog header`.

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

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

En nøkkel i klammer fullføres ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt, eller fra spillets egne statistikknavn, står ikke på denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slippes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt tatt vare på med navn; `used` markerer det som også ble rader), og `meta.json`s `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Leses**

- gamelog `(combat)`-treff gitt og mottatt (mengde, annen pilot, korporasjonens forkortelse, skip, våpen, trefferkvalitet) og bom begge veier
- gamelog `(bounty)`-utbetalinger med ISK, og `Jumping from A to B`-linjene
- gamelog-topptekstens Listener: hvis logg det er

**Tatt vare på rått**

- hver gamelog-linje hel, `type` = dens kanal i klammer (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), med `file` og `listener`; `used` der den ble en rad; topptekstlinjene som `gamelog header`
- hver chatlogg-linje hel (Local, korporasjon, flåte, private kanaler, `EVE System`-meldingene som en endring av Local-kanal ved et hopp), `type` `chat`, med `channel`, `listener` og `file`; topptekstlinjene som `chatlog header`. Ikke gjort om til rader ennå
- formateringstaggene (`<color>`, `<b>`, `<font>`) står i den rå teksten; radene har dem fjernet

**Ikke tilgjengelig**

- posisjoner: klienten skriver ingen i loggene sine
- andre piloters kamper: en gamelog er lytterens egen
- logger fra tidligere innlogginger: hver innlogging skriver nye filer; de som er eldre enn denne kjøringen av klienten, leses ikke på nytt
- chat når spilleren har slått av chattlogging i klientens innstillinger
- klientens egen cache og innstillingsfiler: ikke logger, og ikke dokumentert

**Størrelse**: en gamelog er 0,1-2 MB i timen (mest i kamp); chattlogger avhenger av kanalene som er åpne - en travel Local- eller flåtekanal 0,5-3 MB i timen; zstd i `heat.raw.parquet` gjør det omtrent en tiendedel

## Verifisert {#verified}

testet på syntetiske gamelog-linjer i formatet fellesskapets parsere publiserer; ikke testet mot spillet

## Kilde {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
