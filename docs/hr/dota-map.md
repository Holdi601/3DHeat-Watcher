---
title: "Karta Dote 2"
nav_order: 6.5
lang: "hr"
source: dota-map.md
source_hash: "c9830d37ea89"
nav_exclude: true
search_exclude: true
---
# Karta Dote 2 kao razina (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

zapisuje kartu Dote 2 kao geometriju razine za 3DHeat preglednik: tlo, litice,
vodu, svako drvo i zgrade, u okviru i jedinicama u kojima se crtaju
[tablice replaya Dote 2](game-dota-replays.md). Učitajte `.glb` datoteku u
panelu **Pozadina / razina** preglednika (**3D model…**) pod Dota tablicom, pa
toplina heroja leži na stazama, a tornjevi na svojim tornjevima. Preglednik
datoteku prepoznaje po dijelovima i čuva je u svojoj biblioteci razina. Od tada
njegov gumb **Karta Dote 2** učitava ovu 3D kartu umjesto OpenDotina crteža. Kod:
[`heat3d_watch/decoders/dota_map.py`](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/decoders/dota_map.py).

Potrebna je instalirana Dota 2 i naredbeni redak programa Source2Viewer. Ništa
od igre nije u alatima niti se preuzima: karta dolazi iz vaše vlastite
instalacije, a datoteka koju zapiše je vaša da je čuvate, a ne da je dijelite -
karta je Valveova.

## Što je potrebno {#what-it-needs}

- **Dota 2**, instalirana preko Steama. Bez `--game` traži se kao
  `steamapps\common\dota 2 beta\game\dota` u svakoj Steam biblioteci. `--game`
  prima mapu `dota 2 beta` ili njezinu mapu `game\dota`.
- **Source2Viewerov CLI** (ValveResourceFormat, MIT,
  [izdanja](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)):
  `--source2viewer`, zatim varijabla okruženja `HEAT3D_SOURCE2VIEWER`, zatim
  `Source2Viewer-CLI` / `Source2Viewer-CLI.exe` na `PATH`-u - isto kao naredba
  `map` u 3DHeat CS2 alatu, pa jedna kopija služi za oba.
- numpy (već je potreban watcheru).

`<map>` je `dota` (zadano: obična karta) ili naziv druge karte u mapi
`game\dota\maps\`, ili putanja do `.vpk` datoteke karte.

## Kako nastaje {#how-it-is-made}

1. **Mreža sudara.** Source2Viewer izvozi `maps/<map>/world_physics.vmdl_c` iz
   `maps/<map>.vpk` kao glTF. Njegove grupe nose imena prema površini. Grupe
   zvane `clip` (nevidljivi zidovi) i `sky` se odbacuju. Grupe `water`, `slime`
   ili `window` su **voda**: rijeka i bare su `water_slime`, a uski potoci kroz
   džunglu su `window`; na replayu heroji stoje 10 do 16 jedinica ispod prve,
   a nekoliko jedinica ispod druge. Zadržavaju se samo njihove gornje strane.
   Sve ostalo je teren, podijeljen plohu po plohu: ploha čija normala pokazuje
   prema gore barem 0,7 (nagibi do otprilike 45 stupnjeva) je **tlo**, a ostale -
   stijene litica, zidovi karte - su **konstrukcija**.
2. **Entiteti.** Source2Viewer pretvara entitetne blokove karte
   (`maps/<map>/entities/*.vents_c`) u tekst: blokovi s zaglavljem `====<n>====`,
   jedan `ključ vrijednost` po retku. Koriste se `default_ents` i svaki sloj
   svijeta (`info_world_layer`) koji je na početku prikazan (oznaka pokretanja 1)
   - slojevi dviju baza. Slojevi koji na početku su skriveni drže ono što se
   pojavi kad baza padne, i izostavljeni su.
3. **Što se crta.** Drveće (`ent_dota_tree`) i zgrade: tornjevi, vojarne,
   drevni (`npc_dota_fort`), ispuna (`npc_dota_building`), izvidnice, fontane,
   svetišta mudrosti, lotosovi bazeni, dvostruka vrata, promatrači
   (`npc_dota_lantern`) i neutralna skladišta predmeta. Trgovine (trgovac je lik),
   Dvorana slavnih, zastave, svjetla i čestice nisu uključeni.
4. **Modeli.** Svaki model koji ti entiteti imenuju izvozi se iz
   `game\dota\pak01_dir.vpk` u jednom pokretanju Source2Viewera. Mreže modela
   koje su drugo stanje iste stvari - panj posječenog drveta, krupni plan prikazan
   u inspektoru, ruševine - izostavljaju se prema imenu (`stump`, `inspector`,
   `destruction`).
5. **Zgrade** su mreža vlastitog modela, prorijeđena **grupiranjem vrhova**: svaka
   točka prelazi u srednju vrijednost točaka u kocki veličine `--detail` (zadano
   8 jedinica, otprilike trećina širine heroja), a trokuti koji se stisnu ili
   ponavljaju nestaju. 0 zadržava svaki trokut.
6. **Drveće** je obris svakog modela kao niska okrenuta punina: njegova visina u
   pet pojaseva, svaki šesterokutni prsten koliko je širok većina točaka modela
   na toj visini (90. percentil njihove udaljenosti od osi debla), zatvoren na dnu
   i šiljast na vrhu - 60 trokuta, prava visina i širina modela. Bor postane stožac,
   hrast kugla na stabljici. Prave mreže bile bi otprilike deset puta teže za
   preko 2000 stabala.
7. **Postavljeno** kako ih igra postavlja: skalirano po `scales`, okrenuto po
   `angles` (Sourceov nagib, skretanje i valjanje u stupnjevima), pomaknuto na
   `origin`.
8. **U okvir preglednika.** Source2Viewer piše glTF u metrima, s Y prema gore:
   (Y, Z, X) igre puta 0,0254. To se poništava, a svaka točka se zapisuje kao
   (X, Z, -Y) igre: Y prema gore, Y igre negiran - okvir u kojem se Dota tablice
   crtaju kroz njihove `heat3d` naznake (`up: z`, `flipY: true`, mjerilo 1).
   Riječ je o rotaciji, a ne o zrcaljenju.

## Datoteka {#the-file}

Binarni glTF 2.0 kao i kod 3DHeat CS2 alata (vidi njegovu stranicu o izvozu
karte): jedan čvor i jedna mreža po dijelu u korijenu, bez transformacija, s
ravnim sjenčanjem (vrh po kutu trokuta koji nosi normalu tog trokuta), indeksi
`uint32`, bez materijala, tekstura ili UV-a, `asset.generator` `heat3d_watch`,
jedinice igre.

| Dio | Što je |
|---|---|
| `ground:terrain` | tlo po kojem se hoda |
| `structure:terrain` | stijene litica i zidovi karte |
| `water:water_slime`, `water:window` | rijeka i bare; potoci u džungli |
| `structure:tree` | svako drvo koje stoji na početku |
| `structure:tower`, `structure:barracks`, `structure:ancient`, `structure:filler`, `structure:outpost`, `structure:fountain`, `structure:shrine`, `structure:lotus_pool`, `structure:twin_gate`, `structure:watcher`, `structure:neutral_stash` | zgrade, po vrsti |

Prefiks `ground:` / `structure:` / `water:` je način na koji svi 3DHeat izvoznici
razina govore pregledniku što je koji dio; preglednik im vjeruje na riječ. Budući
da su jedinice igrine (otprilike jedan inč svaka), drugi glTF preglednik prikazuje
kartu oko 39 puta većom; u 3DHeatu ona leži točno pod tablicom.

Ispis jednog primjera pokretanja (brojevi ovise o verziji karte):

```text
reading dota.vpk: collision mesh and entities
reading 30 models from pak01_dir.vpk
dota.glb: dota, 700,000 triangles (230,000 ground) in 16 parts; 2,400 trees, 70 buildings
```

Prva dva retka idu u tok grešaka, posljednji u izlaz. Model koji Source2Viewer
nije mogao naći izostavlja se i imenuje se na kraju zadnjeg retka
(`; 1 model(s) not found, left out: ...`). Greške - Dota 2 nije nađena, karta nije
nađena, Source2Viewer nije nađen ili ne radi - ispisuju `dota-map: <why>` i
završavaju s kodom 1.

## Kako je provjerena {#how-it-was-checked}

Na javnom replayu utakmice pretvorenom watcherom (zakrpa 7.40) i na karti
instalirane igre:

- svaki uzorak položaja heroja, gledan okomito prema dolje, pronalazi tlo za
  najvišu plohu tla na najviše 64 jedinice iznad njegovih stopala; medijan
  visine iznad nje je 0 jedinica, a 99,5 % je unutar 16 jedinica; s kartom
  zrcaljenom (Y nije negiran) samo oko polovice pronalazi tlo, a ostali lebde ili
  tonu za visinu litice;
- 22 tornja, 12 vojarni, 2 drevna, 14 ispuna, 2 izvidnice, 2 fontane i 10
  promatrača koje tablica jedinica replaya postavlja stoje na entitetima karte iste
  vrste, na 0,02 jedinice, vodoravno i po visini;
- stopalo svakog drveta je na tlu.

Testovi (`tests/test_dota_map.py`) provjeravaju čitač entitetnih blokova,
okvire, podjelu terena, obrise i grupiranje drveća, postavljanje te cijeli izvoz
sa Source2Viewerom zamijenjenim lažnim programom - samo na izmišljenim podacima.

## Što ne radi {#what-it-does-not-do}

- Nema tekstura ni boja: preglednik sjenča razinu na svoj način.
- Nema posječenih stabala ni srušenih zgrada tijekom utakmice: karta kakva
  počinje.
- Događajne i prilagođene karte nisu provjerene; njihove klase entiteta mogu biti
  drugačije.
- Rekviziti koji samo ukrašavaju (kamenje, ograde, zastave) su u njoj samo u mjeri
  u kojoj su dio mreže sudara.
