---
title: Mapa Dota 2
nav_order: 6.5
lang: "pl"
source: dota-map.md
source_hash: "c9830d37ea89"
nav_exclude: true
search_exclude: true
---
# Mapa Dota 2 jako poziom (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

zapisuje mapę Dota 2 jako geometrię poziomu dla viewera 3DHeat: grunt, klify, wodę, każde drzewo i budynki, w układzie
i jednostkach, w jakich rysowane są [tabele powtórek Dota 2](game-dota-replays.md). Wczytaj plik `.glb` w panelu
**Tło / poziom** (**Model 3D…**) pod tabelą Dota, a ciepło bohaterów będzie leżeć na pasach, a wieże na swoich wieżach.
Viewer rozpoznaje plik po jego częściach i trzyma go w swojej bibliotece poziomów; od tej chwili jego przycisk
**Mapa Dota 2** wczytuje tę mapę 3D zamiast rysunku z OpenDota. Kod:
[`heat3d_watch/decoders/dota_map.py`](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/decoders/dota_map.py).

Potrzebna jest zainstalowana Dota 2 i wiersz poleceń Source2Viewer. Nic z gry nie znajduje się w narzędziach ani nie
jest przez nie pobierane: mapa pochodzi z twojej własnej instalacji, a zapisany plik jest twój do zachowania, nie do
udostępniania – mapa należy do Valve.

## Czego potrzeba {#what-it-needs}

- **Dota 2**, zainstalowana przez Steam. Bez `--game` szukana jest jako `steamapps\common\dota 2 beta\game\dota`
  we wszystkich bibliotekach Steam. `--game` przyjmuje folder `dota 2 beta` albo jego `game\dota`.
- **wiersz poleceń Source2Viewer** (ValveResourceFormat, MIT,
  [wydania](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)):
  `--source2viewer`, potem zmienna środowiskowa `HEAT3D_SOURCE2VIEWER`, potem `Source2Viewer-CLI` /
  `Source2Viewer-CLI.exe` w `PATH` – tak samo jak polecenie `map` narzędzia 3DHeat CS2, więc jedna kopia
  obsługuje oba.
- numpy (już potrzebny watcherowi).

`<map>` to `dota` (domyślnie: zwykła mapa), inna nazwa mapy w `game\dota\maps\` albo ścieżka do pliku `.vpk` mapy.

## Jak powstaje {#how-it-is-made}

1. **Siatka kolizji.** Source2Viewer eksportuje `maps/<map>/world_physics.vmdl_c` z `maps/<map>.vpk` jako glTF.
   Jej grupy są nazwane według powierzchni. Grupy `clip` (niewidzialne ściany) i `sky` są odrzucane. Grupy `water`,
   `slime` i `window` to **woda**: rzeka i stawy to `water_slime`, wąskie strumienie w dżungli to `window`; na
   powtórce bohaterowie stoją 10 do 16 jednostek pod pierwszymi i kilka jednostek pod drugimi. Zachowywane są tylko ich
   powierzchnie skierowane w górę. Wszystko inne to teren, dzielony ścianka po ściance: ścianka, której normalna
   wskazuje w górę co najmniej na 0,7 (zbocza do około 45 stopni), to **grunt**; reszta – ściany klifów, mury mapy –
   to **konstrukcja**.
2. **Byty.** Source2Viewer dekompiluje bloki bytów mapy (`maps/<map>/entities/*.vents_c`) do tekstu: bloki z nagłówkiem
   `====<n>====`, jeden `key value` w wierszu. Używane są bloki `default_ents` oraz każda warstwa świata
   (`info_world_layer`), która na starcie się pokazuje (flaga spawnu 1) – warstwy dwóch baz. Warstwy, które startują
   ukryte i zawierają to, co pojawia się po upadku bazy, są pomijane.
3. **Co jest rysowane.** Drzewa (`ent_dota_tree`) i budynki: wieże, koszary, starożytni (`npc_dota_fort`),
   wypełniacze (`npc_dota_building`), posterunki, fontanny, świątynie mądrości, lotosowe baseny, bramy bliźniacze,
   strażnicy (`npc_dota_lantern`) i neutralne skrytki przedmiotów. Sklepów (sprzedawca to postać), sali sław,
   sztandarów, świateł i cząsteczek nie ma.
4. **Modele.** Każdy model nazwany przez te byty jest eksportowany z `game\dota\pak01_dir.vpk` jednym przebiegiem
   Source2Viewer. Siatki modelu, które są innym stanem tej samej rzeczy – pień ściętego drzewa, zbliżenie pokazywane
   w inspektorze, gruz – są pomijane po nazwie (`stump`, `inspector`, `destruction`).
5. **Budynki** to własna siatka ich modelu, przerzedzona przez **grupowanie wierzchołków**: każdy punkt przesuwa się do
   średniej punktów w sześcianie o boku `--detail` (domyślnie 8 jednostek, około jednej trzeciej szerokości bohatera),
   a trójkąty, które się zwijają lub powtarzają, znikają. 0 zachowuje każdy trójkąt.
6. **Drzewa** to obrys każdego modelu jako niskie, obrócone bryły: wysokość w pięciu pasach, każdy to sześciokątny
   pierścień tak szeroki, jak większość punktów modelu na tej wysokości (90. percentyl ich odległości od osi pnia),
   zamknięty u dołu i zakończony szpicem u góry – 60 trójkątów, prawdziwa wysokość i szerokość modelu. Sosna wychodzi
   jako stożek, dąb jako kula na pniu. Prawdziwe siatki ważyłyby około dziesięć razy więcej przy ponad 2000 drzew.
7. **Ustawione** tak, jak gra je ustawia: skalowane przez `scales`, obracane przez `angles` (pitch, yaw, roll Source
   w stopniach), przesuwane do `origin`.
8. **W układzie viewera.** Source2Viewer zapisuje glTF w metrach, oś Y w górę: (Y, Z, X) gry razy 0,0254. To jest
   cofane, a każdy punkt zapisywany jako (X, Z, -Y) gry: Y w górę, Y gry zanegowane – układ, w którym tabele Dota są
   rysowane przez wskazówki `heat3d` (`up: z`, `flipY: true`, skala 1). Obrót, a nie odbicie lustrzane.

## Plik {#the-file}

Binarny glTF 2.0, jak w narzędziu 3DHeat CS2 (zob. jego stronę o eksporcie map): jeden węzeł i jedna siatka na część
w korzeniu, bez przekształceń, cieniowanie płaskie (wierzchołek na każdy róg trójkąta, niosący normalną tego trójkąta),
indeksy `uint32`, bez materiałów, tekstur i UV, `asset.generator` `heat3d_watch`, jednostki gry.

| Część | Co to jest |
|---|---|
| `ground:terrain` | grunt, po którym można chodzić |
| `structure:terrain` | ściany klifów i mury mapy |
| `water:water_slime`, `water:window` | rzeka i stawy; strumienie w dżungli |
| `structure:tree` | każde drzewo stojące na starcie |
| `structure:tower`, `structure:barracks`, `structure:ancient`, `structure:filler`, `structure:outpost`, `structure:fountain`, `structure:shrine`, `structure:lotus_pool`, `structure:twin_gate`, `structure:watcher`, `structure:neutral_stash` | budynki, według rodzaju |

Prefiks `ground:` / `structure:` / `water:` to sposób, w jaki wszystkie eksportery poziomów 3DHeat mówią viewerowi,
czym jest dana część; viewer przyjmuje to na słowo. Ponieważ jednostki są jednostkami gry (około cala każda), inny
podgląd glTF pokaże mapę około 39 razy za dużą; w 3DHeat leży ona dokładnie pod tabelą.

Co wypisuje, na przykładowym przebiegu (liczby zależą od wersji mapy):

```text
reading dota.vpk: collision mesh and entities
reading 30 models from pak01_dir.vpk
dota.glb: dota, 700,000 triangles (230,000 ground) in 16 parts; 2,400 trees, 70 buildings
```

Dwie pierwsze linie idą do strumienia błędów, ostatnia do wyjścia. Model, którego Source2Viewer nie znalazł, jest
pomijany i wymieniony na końcu ostatniej linii (`; 1 model(s) not found, left out: ...`). Błędy – nie znaleziono Dota 2,
mapy albo Source2Viewer, albo Source2Viewer zawiódł – wypisują `dota-map: <why>` i kończą się kodem 1.

## Jak sprawdzono {#how-it-was-checked}

Na publicznej powtórce meczu, przekonwertowanej przez watcher (łatka 7.40), i na mapie zainstalowanej gry:

- każdy punkt położenia bohatera, patrząc pionowo w dół, znajduje grunt dla najwyższej powierzchni nie wyżej niż 64
  jednostki nad jego stopami; mediana wysokości nad nią to 0 jednostek, a 99,5 % jest w odległości 16 jednostek; przy
  mapie odbitej lustrzanie (Y nie zanegowane) tylko około połowa znajduje grunt, a reszta unosi się lub zapada o wysokość
  klifu;
- 22 wieże, 12 koszar, 2 starożytnych, 14 wypełniaczy, 2 posterunki, 2 fontanny i 10 strażników, które tabela jednostek
  powtórki umieszcza, stoją na bytach mapy tego samego rodzaju z dokładnością do 0,02 jednostki, w poziomie i w wysokości;
- stopa każdego drzewa jest na gruncie.

Testy (`tests/test_dota_map.py`) sprawdzają czytnik bloków bytów, układy, podział terenu, obrysy i grupowanie drzew,
rozmieszczenie oraz cały eksport z Source2Viewer zastąpionym atrapą – wszystko na zmyślonych danych.

## Czego nie robi {#what-it-does-not-do}

- Bez tekstur i kolorów: viewer cieniuje poziom po swojemu.
- Bez ściętych drzew ani zniszczonych budynków w trakcie meczu: mapa taka, jaka jest na starcie.
- Mapy wydarzeń i mapy własne nie są sprawdzone; ich klasy bytów mogą być inne.
- Elementy, które tylko zdobią (skały, ogrodzenia, sztandary), są w pliku tylko o tyle, o ile są częścią siatki kolizji.
