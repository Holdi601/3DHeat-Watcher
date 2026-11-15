---
title: "Hearthstone (dnevniške datoteke)"
nav_order: 25
lang: "sl"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (dnevniške datoteke) {#hearthstone-log-files}

Medtem ko igrate Hearthstone, watcher bere datoteke, ki jih igra zapisuje, in shrani, kaj se je zgodilo, da si to pozneje lahko ogledate kot statistiko in časovnico.

*Tehnične podrobnosti: adapter `hearthstone`, vrsta [`log`](sources-and-rules.md); teče, medtem ko se izvaja `Hearthstone.exe`, in vsakih 0,5 s preverja nove podatke.*

## Kaj se zapiše {#what-is-recorded}

- začetek in konec igre, z rezultatom (zmaga, poraz, neodločeno), potezami in imenom nasprotnika
- vsaka poteza
- vsaka vrstica datoteke Power.log in drugih dnevnikov, celih, v heat.raw.parquet
- igre, zmage, porazi, neodločeni izidi, poteze, najdaljša igra

## Od kod prihajajo {#where-it-comes-from}

&lt;namestitev&gt;\Logs\Power.log (ali Logs\Hearthstone_\*\Power.log), zapisano, ko ima %LOCALAPPDATA%\Blizzard\Hearthstone\log.config oddelek [Power], in vsak drug \*.log, ki ga igra tam zapiše

## Kako vklopiti {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` doda beleženje [Power] v %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (ohrani se varnostna kopija); ponovno zaženite igro

Ukaz vpišite v terminal, odprt v mapi watcherja (glejte [Pred začetkom](before-you-start.md)). Če ne uspe, zadnja vrstica pove zakaj; [Namestitev in zagon](installing-and-running.md) opisuje običajne vzroke.

`python -m heat3d_watch setup hearthstone` našteje datoteke, ki bi jih spremenil; `python -m heat3d_watch setup hearthstone --apply` jih spremeni in izvirnik ohrani kot `<file>.heat3d-backup` (glejte [Ukazi](commands.md#setup)). Za vsako spremembo izpiše `hearthstone: changed: ...`, ali `hearthstone: nothing to change`, če je že vklopljeno.

## Kako deluje {#how-it-works}

Hearthstone: igrina datoteka Power.log, ki jo zapisuje, ko to zahteva log.config.

Hearthstone ob zagonu bere `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config`;
oddelek `[Power]` z `LogLevel=1` in `FilePrinting=true` povzroči, da igra zapiše
spremembe stanja vsake igre v `<namestitev>\Logs\Power.log` (novejši odjemalci dajo
vsak zagon v svojo mapo, `Logs\Hearthstone_<datum>\`). To je dokumentirano odpravljanje
napak, ki ga sledilniki kupov vklapljajo od leta 2014 (nastavitev Hearthstone Deck Tracker zapiše
isti oddelek). `setup()` doda oddelek, z varnostno kopijo datoteke v prvotnem stanju; igra
za branje potrebuje ponovni zagon.

Uporabljene vrstice, vse iz `GameState.DebugPrintPower()` (vrstice `PowerTaskList`
ponavljajo iste in se preskočijo):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

Igralčeva stran je tista, katere začetna roka ima poimenovane karte (nasprotnikove so skrite),
sicer stran, ki ni AI (račun 0) ali "UNKNOWN HUMAN PLAYER". Vrstice nosijo samo čas dneva; datum
je današnji.
Brez položajev.

Vsaka vrstica datoteke Power.log se shrani cela v surovo spremljevalno datoteko seje (pravilo pretvornikov
3DHeat), vključno s ponovljenimi vrsticami `PowerTaskList`, opcijami, izbirami in posodobitvami
vnosov: `type` je metoda, ki jo je zapisala (`GameState.DebugPrintPower`,
`PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Vsak drug dnevnik, ki ga igra
zapiše zraven - `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ..., vsak tam, kadar to zahteva
log.config (sledilniki kupov to pogosto storijo) - se bere na enak način in se shrani z imenom v `log`.

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Zabeleženi položaji | ne |
| Navpična os | `y` |
| Enote | položaji niso zabeleženi |
| Zrcaljenje za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Te vrednosti gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, zato pregledovalnik 3DHeat vrti in meri vrstice sam - glejte [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `log`: bere samo, kar igra ali platforma ponudi (datoteke, ki jih igra zapisuje med delovanjem), zato zapisuje tudi pri igri na spletu in ne samo offline; zastavica odloča samo o tem, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji vrste `memory` berejo pomnilnik, in nikoli za igro, označeno kot igranje na spletu - glejte [Viri in pravila](sources-and-rules.md).

## Zabeležene statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavlja po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz imen statistik igre, na tem seznamu niso; zgoraj v "Kaj se zapiše" so našteti.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir ima, se prebere ali shrani, nikoli ne izgine. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani nedotaknjen v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in polja, shranjena po imenu; `used` označuje, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- `CREATE_GAME`, igralci (entiteta, ID igralca, račun; račun 0 je AI) in njihova imena (`DebugPrintGame`)
- čigava stran je igralčeva, iz poimenovanih kart začetne roke
- `TAG_CHANGE` za TURN, PLAYSTATE (won, lost, tied) in STATE COMPLETE: poteze, rezultat, nasprotnik

**Shranjeno surovo**

- vsaka vrstica datoteke Power.log cela, `type` = metoda, ki jo je zapisala (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` tam, kjer je postala vrstica: vsaka odigrana, vlečena in razkrita karta, vsaka sprememba oznake, napad, opcija in izbira je tukaj, še ni v vrsticah
- vsaka vrstica drugih dnevnikov v isti mapi (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - kar koli vklopi log.config), isti `type`, z imenom dnevnika v `log`
- vrstica brez ravni in časa dneva kot `untimed`, brez metode kot `untagged`

**Ni na voljo**

- položaji: kartna igra jih nima
- skrite karte nasprotnika: dnevnik imenuje karto šele, ko je razkrita
- dnevniki, ki jih log.config ne vklopi: `setup` zahteva samo [Power]; drugi dnevniki pridejo, ko jih vklopi drugo orodje (sledilnik kupov)
- dnevniki prejšnjih zagonov: vsak zagon zapiše novo mapo; tisti, starejši od tega zagona igre, se ne berejo znova

**Velikost**: Power.log z Verbose meri približno 1-5 MB na igro, 10-40 MB na uro igranja; drugi dnevniki dodajo malo; zstd v heat.raw.parquet jih skrči na približno desetino ali manj (vrstice se veliko ponavljajo)

## Preverjeno {#verified}

preizkušeno na sintetičnih vrsticah Power.log v obliki igre; nepreizkušeno z igro

## Vir {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
