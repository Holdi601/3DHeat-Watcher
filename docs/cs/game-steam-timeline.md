---
title: "Časová osa Steamu (platforma)"
nav_order: 44
lang: "cs"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Časová osa Steamu (platforma) {#steam-timeline-platform}

Watcher ukládá, co Časová osa Steamu eviduje o vašich hrách, abyste se na svou historii mohli později podívat jako na statistiky a časovou osu.

*Technické podrobnosti: adaptér `steam-timeline`, druh [`platform`](sources-and-rules.md); běží pořád (nečeká, až začne hra) a hledá nová data každých 10 s.*

## Co se zaznamenává {#what-is-recorded}

- jedna relace na soubor časové osy: jeho začátek a konec (session_start, session_end)
- achievementy odemčené během hraní, s časem
- změny herního režimu (hraní, příprava, menu, obrazovka načítání)
- události, které hry přidávají přes ISteamTimeline, s názvem a popisem, pod názvem jejich ikony
- herní fáze (zápas, mise) s jejich štítky; události uvnitř nich nesou jejich id jako relace
- popisy stavů, které hra ukazuje na časové ose ("Kolo 3")
- vlastní chyby nahrávání Steamu

## Odkud to pochází {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Jak to zapnout {#how-to-switch-it-on}

Steam > Settings > Game Recording: nahrávat na pozadí nebo na vyžádání (Steam pak časové osy zapisuje)

## Jak to funguje {#how-it-works}

Co launcher a grafický ovladač uchovávají o hraní: statistiky Steamu, achievementy, čas hraní a časové osy, a highlighty a klipy NVIDIE.

Žádný z těchto zdrojů nepotřebuje, aby hra spolupracovala nebo běžela, takže tři adaptéry zde jsou vždy zapnuté a každých několik sekund se dívají na pár souborů.

#### Časová osa Steamu (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`, zapisovaný, zatímco je zapnuté nahrávání her Steamu. Soubor je JSON s čísly jako řetězci: "daterecorded" (sekundy Unixu), "starttime"/"endtime" (ms) a "entries", každý {"id", "time" (ms od daterecorded), "type", ...}. Typy viděné na skutečných souborech:
```text
achievement        achievement_name - Steam přidává pro každou hru
gamemode           mode, ETimelineGameMode: 1 hraní, 2 příprava,
                   3 menu, 4 obrazovka načítání
error              description - Steamova vlastní ("#GameRecording_RecordingFailed")
event              AddInstantaneousTimelineEvent/AddRangeTimelineEvent hry:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              rozpětí StartGamePhase..EndGamePhase: duration (ms),
                   tags [{name, icon, group, priority}] (režim, mapa ...)
```
Rozložení souboru je Steamu a není zdokumentováno; pole jsou parametry rozhraní API. Každý jiný typ se zaznamená pod svým vlastním názvem se svými poli.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Stejný modul slouží také: [NVIDIA highlights (platforma)](game-nvidia-highlights.md), [Statistiky Steamu (platforma)](game-steam-stats.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ne |
| Osa nahoru | `y` |
| Jednotky | metry |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapisují do `meta.json` každé relace (`axes`) a, má-li relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat řádky sám otáčí a měří – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hra po síti (`multiplayer`): **ne**. `games --markdown` to ukazuje jako „single-player“.
- Druh `platform`: čte jen to, co hra nebo platforma poskytuje (co uchovává Steam nebo grafický ovladač), takže zaznamenává i v online hře, stejně jako offline; příznak rozhoduje jen o tom, zda smí být paměť vůbec čtena.
- Paměť: tímto adaptérem **nikdy** nečtena. Paměť čtou jen adaptéry `memory` a nikdy u hry označené jako hraná po síti – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (`stats` každé relace v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Klíč ve složených závorkách se doplňuje za běhu (`score.{team}` je jeden klíč na tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Watcher dodržuje [pravidlo převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uchová, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér přijme, uchová celá v `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uchovaná podle názvu; `used` označuje to, co se stalo také řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- každou položku jednou, jako řádek v jejím čase: její typ, každé prosté pole (title, description, icon, priority, duration, possible_clip, název achievementu, režim, ...), štítky fáze podle skupin, zobrazovaný název achievementu ze schématu statistik; začátek a konec souboru

**Uchováno surové**

- každou položku celou jako JSON pod typem Steamu (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, jakýkoli jiný): vnořená pole – ikona a priorita štítku, cokoli, co přidá pozdější Steam – jsou jen tady
- `timeline`: vlastní pole souboru (daterecorded, starttime, endtime, jakákoli jiná), když se relace otevře, a znovu, když se změní

**Nedostupné**

- samotné nahrávání (video): Steam ho uchovává ve svých vlastních složkách; relace odkazuje na soubor časové osy jménem
- čtení souboru, který Steam zapisuje a který nejde zpracovat ani se zavřeným koncem: počítá se (`bad` ve stavu adaptéru) a čte se znovu při další změně, kdy se vezmou jeho položky

**Velikost**: několik set položek po 100–300 bajtech za hodinu hraní: hluboko pod 1 MB za hodinu

## Ověřeno {#verified}

testováno na skutečných souborech časové osy z místní instalace: položky achievement, gamemode, error a vlastní položky her typu event, state_description a phase; samotný formát souboru není zdokumentován

## Zdroj {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte ho znovu, místo úprav této stránky. -->
