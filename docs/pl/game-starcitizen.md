---
title: "Star Citizen (pliki dziennika)"
nav_order: 42
lang: "pl"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (pliki dziennika) {#star-citizen-log-files}

Gdy grasz w Star Citizen, watcher odczytuje pliki, które zapisuje gra, i zachowuje to, co się wydarzyło, dzięki czemu później możesz to obejrzeć jako statystyki i oś czasu.

*Szczegóły techniczne: adapter `starcitizen`, rodzaj [`log`](sources-and-rules.md); działa, gdy uruchomiony jest `StarCitizen.exe`, i sprawdza nowe dane co 0,5 s.*

## Co jest zapisywane {#what-is-recorded}

- zgony z ofiarą, zabójcą, bronią, rodzajem obrażeń i strefą (gracze i NPC)
- wyłączone i zniszczone pojazdy, z kierowcą, przyczyną i strefą
- cele podróży kwantowej, zmiany układu słonecznego, odrodzenia, powroty do życia, unieruchomienia
- każda linia Game.log w całości w `heat.raw.parquet`
- zabójstwa (gracza i NPC), zgony, samobójstwa, zniszczone i utracone pojazdy, skoki kwantowe

## Skąd pochodzą dane {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (folder wersji uruchomionego StarCitizen.exe), tylko plik dziennika zapisywany przez grę – to gra z Easy Anti-Cheat: nic nie dotyka jej procesu

## Jak to włączyć {#how-to-switch-it-on}

Nic nie trzeba włączać: watcher odczytuje źródło tak, jak udostępnia je gra lub platforma.

## Jak to działa {#how-it-works}

Star Citizen: dziennik samego klienta, `<install>\StarCitizen\LIVE\Game.log`.

Gra zapisuje Game.log od nowa przy każdym uruchomieniu (poprzedni trafia do
`logbackups\`). Czytany jest tylko ten plik: Star Citizen działa z Easy Anti-Cheat,
a nic tutaj nie dotyka procesu gry. Linie zaczynają się od znacznika czasu UTC i
poziomu, potem tag w nawiasach kątowych:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(zawinięte tutaj; w pliku jedna linia na wpis). Strefa zgonu to zwykle
statek, w którym siedziała ofiara, a nie miejsce. Format nie jest udokumentowany przez Cloud
Imperium i zmienia się między łatkami; wzorce idą za liniami, które czytają społecznościowe
trackery zabójstw (np. <https://github.com/DimmaDont/all-slain>, MIT – tylko fakty),
a to, co nie pasuje, jest pomijane, nie zgadywane. `pos` pojazdu jest względne do strefy
i zachowane tylko jako tekst: żadne współrzędne nie są rysowane.

Każda linia jest zachowana w całości w surowym pliku pomocniczym sesji (zasada konwertera 3DHeat),
dopasowana albo nie: `type` to tag linii w nawiasach kątowych (`Actor
Death`, `Spawn Flow`, ...), a jeśli go nie ma – jej pierwsze słowo w nawiasach (`Notice`,
`CSessionManager::OnClientSpawned`), a jeśli i tego nie ma – `untagged`; linia bez
znacznika czasu to `untimed`.

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | nie |
| Oś pionowa | `y` |
| Jednostki | brak zapisanych pozycji |
| Odbicie dla przeglądarki | brak |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczone jako grane online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „dozwolone (odczytuje tylko to, co gra publikuje)”.
- Rodzaj `log`: odczytuje tylko to, co gra lub platforma udostępnia (pliki, które gra zapisuje podczas działania), więc nagrywa też w grze online; flaga decyduje tylko o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest odczytywana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako grana online – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry lub z jej własnych nazw statystyk, nie są na tej liście; sekcja „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): to, co źródło zawiera, jest odczytywane lub zachowywane, nigdy nie jest pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` wynosi 0.

**Odczytane**

- `<Actor Death>`: ofiara, zabójca, broń i jej klasa, rodzaj obrażeń, strefa; NPC czy gracz
- `<Vehicle Destruction>`: pojazd, strefa, pozycja względna do strefy jako tekst, kierowca, przyczyna, sposób, poziom zniszczenia
- cele `<Quantum Navtarget>`, `<Changing Solar System>`, `OnClientSpawned`, odrodzenia w szpitalu, unieruchomienia z ich przyczynami, `EndSession`
- uchwyt gracza z `<AccountLoginCharacterStatus_Character>` lub linii logowania

**Zachowane w surowej postaci**

- każda linia Game.log w całości, `type` = jej tag w nawiasach kątowych (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), a jeśli go nie ma – jej pierwsze słowo w nawiasach (`Notice`, `CSessionManager::OnClientSpawned`, ...), a jeśli i tego nie ma – `untagged`; linie bez znacznika czasu (nagłówek dziennika, zawinięty tekst) jako `untimed`; `used` tam, gdzie linia stała się wierszem

**Niedostępne**

- pozycje: dziennik nie podaje żadnej w ramce, którą da się narysować (`pos` zniszczonego pojazdu jest względne do strefy, której miejsce nie jest zapisywane)
- wszystko z procesu lub sieci gry: Star Citizen działa z Easy Anti-Cheat; czytany jest tylko plik dziennika
- logi wcześniejszych uruchomień (`logbackups`): Game.log każdego uruchomienia jest zachowywany, gdy jest grany
- linie w formacie, który łatka zmienia: zachowane w surowej postaci, dekodowane ponownie, gdy nowy format będzie znany

**Rozmiar**: Game.log rośnie o około 5-15 MB na godzinę gry (więcej w zajętych miejscach i przy błędach); zstd w `heat.raw.parquet` zmniejsza to mniej więcej dziesięciokrotnie

## Sprawdzone {#verified}

przetestowane na syntetycznych liniach Game.log w formacie udokumentowanym przez społecznościowe trackery; nie przetestowane w grze

## Źródło {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
