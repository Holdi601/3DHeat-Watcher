---
title: "EVE Online (logfiler)"
nav_order: 20
lang: "da"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (logfiler) {#eve-online-log-files}

Mens du spiller EVE Online, læser watcheren de filer, spillet skriver, og gemmer det, der skete, så du senere kan se det som statistik og en tidslinje.

*Tekniske detaljer: adapter `eve`, type [`log`](sources-and-rules.md); den kører, mens `exefile.exe` kører, og leder efter nye data hver 0.5 s.*

## Hvad der registreres {#what-is-recorded}

- skade givet og modtaget over for det andet skib, piloten, corporation-forkortelsen, våben og trækvalitet
- skud, der missede, givet og modtaget
- belønninger for NPC-dræb (bounty) med ISK
- hop mellem systemer
- hver gamelog- og chatlog-linje hel i heat.raw.parquet
- skade givet og modtaget, træf, misser, bounty-drab og ISK, hop

## Hvor data kommer fra {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt og Chatlogs\\\*.txt ved siden af (alle filer skrevet, siden klienten startede)

## Sådan slår du det til {#how-to-switch-it-on}

Der skal ikke slås noget til: watcheren læser kilden, som spillet eller platformen udleverer den.

## Sådan virker det {#how-it-works}

EVE Online: klientens spillogs, `Documents\EVE\logs\Gamelogs\*.txt`.

Klienten skriver én fil pr. karakter pr. login,
`<yyyymmdd>_<hhmmss>[_<karakter-id>].txt`; logning til fil er slået til som standard. Flere klienter, der kører
side om side, skriver hver deres, så hver fil, der er skrevet, siden spillet startede, følges. Hoved og linjer (EVE-tid er UTC):

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

(combat-linjen er én linje i filen). Formateringstags fjernes, før der matches.
Filen har gennem årene været UTF-8 og UTF-16; begge læses.
Formatet er ikke dokumenteret af CCP; det er klientens rene tekstlog, læst som
community-kampværktøjer læser den (f.eks. <https://docs.rs/crate/eve-log-parser>).
Ingen positioner.

Ved siden af ligger `Documents\EVE\logs\Chatlogs\<kanal>_<yyyymmdd>_<hhmmss>[_<id>].txt`:
én fil pr. chatkanal pr. login (når chatlogning er slået til, hvilket er klientens
standard), UTF-16, en header der navngiver kanalen og lytteren, derefter
`[ yyyy.mm.dd hh:mm:ss ] Afsender > besked`.

Hver linje i begge gemmes hel i kørslens rå sidefil (3DHeats konverterregel):
en gamelog-linje under sin kanal i klammer (`combat`,
`notify`, `bounty`, `None`, ...), en chatlinje som `chat` med sin kanal, og
headerlinjerne som `gamelog header` / `chatlog header`.

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

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, og aldrig smides væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i kørslens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter, der gemmes under deres navn; `used` markerer, hvad der også blev til rækker), og `selfCheck.completeness` i `meta.json` tæller hver `type` - `lost` er 0.

**Læst**

- gamelog `(combat)`-træf givet og modtaget (mængde, den anden pilot, corporation-forkortelsen, skib, våben, trækvalitet) og misser begge veje
- gamelog `(bounty)`-udbetalinger med ISK, og linjerne `Jumping from A to B`
- gamelog-headerens Listener: hvis log det er

**Gemt råt**

- hver gamelog-linje hel, `type` = dens kanal i klammer (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), med `file` og `listener`; `used` hvor den blev til en række; headerlinjerne som `gamelog header`
- hver chatlog-linje hel (Local, corporation, flåde, private kanaler, `EVE System`-meddelelserne såsom en ændring af Local-kanal ved et hop), `type` `chat`, med `channel`, `listener` og `file`; headerlinjerne som `chatlog header`. Endnu ikke gjort til rækker
- formateringstagsene (`<color>`, `<b>`, `<font>`) bliver i den rå tekst; rækkerne har dem fjernet

**Ikke tilgængeligt**

- positioner: klienten skriver ingen til sine logs
- andre piloters kampe: en gamelog er lyttérens egen
- logs fra tidligere logins: hvert login skriver nye filer; dem, der er ældre end denne kørsel af klienten, læses ikke igen
- chat, når spilleren har slået chatlogning fra i klientens indstillinger
- klientens egen cache- og indstillingsfiler: ikke logs, og ikke dokumenteret

**Størrelse**: en gamelog fylder 0,1-2 MB i timen (mest under kamp); chatlogs afhænger af de åbne kanaler - en travl Local- eller flådekanal 0,5-3 MB i timen; zstd i heat.raw.parquet gør det cirka til en tiendedel

## Verificeret {#verified}

testet på syntetiske gamelog-linjer i det format, udbredte parsere bruger; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Genereret fra adapteren af tools/gen_game_pages.py; ret adapteren og kør den igen i stedet for at redigere denne side. -->
