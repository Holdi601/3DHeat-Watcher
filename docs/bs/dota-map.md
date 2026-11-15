---
title: "Mapa Dote 2"
nav_order: 6.5
lang: "bs"
source: dota-map.md
source_hash: "c9830d37ea89"
nav_exclude: true
search_exclude: true
---
# Mapa Dote 2 kao nivo (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

zapisuje mapu Dote 2 kao geometriju nivoa za preglednik 3DHeat: tlo, litice,
vodu, svako drvo i zgrade, u istom koordinatnom okviru i istim jedinicama u
kojima se crtaju [tabele snimaka Dote 2](game-dota-replays.md). Učitajte `.glb` u
panelu **Pozadina / nivo** preglednika (**3D model…**) ispod tabele Dote i
toplotna mapa heroja leži na stazama, a tornjevi na svojim tornjevima.
Preglednik prepoznaje datoteku po njenim dijelovima i čuva je u svojoj
biblioteci nivoa; od tada njegovo dugme **Mapa Dote 2** učitava ovu 3D mapu
umjesto OpenDotinog crteža. Kod:
[`heat3d_watch/decoders/dota_map.py`](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/decoders/dota_map.py).

Treba vam instalirana Dota 2 i komandna linija programa Source2Viewer. Ništa iz
igre nije u alatima niti ga oni preuzimaju: mapa dolazi iz vaše vlastite
instalacije, a datoteka koju alat zapiše je vaša da je čuvate, ne da je dijelite
- mapa pripada Valveu.

## Šta je potrebno {#what-it-needs}

- **Dota 2**, instalirana preko Steama. Bez `--game` traži se kao
  `steamapps\common\dota 2 beta\game\dota` u svakoj Steam biblioteci. `--game` prima
  folder `dota 2 beta` ili njegov folder `game\dota`.
- **Source2Viewer CLI** (ValveResourceFormat, MIT,
  [izdanja](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)):
  `--source2viewer`, zatim varijabla okruženja `HEAT3D_SOURCE2VIEWER`, zatim
  `Source2Viewer-CLI` / `Source2Viewer-CLI.exe` na `PATH` - isto kao komanda `map`
  alata 3DHeat za CS2, pa jedna kopija služi za oba.
- numpy (watcher ga već traži).

`<map>` je `dota` (zadano: normalna mapa) ili ime neke druge mape u
`game\dota\maps\`, ili putanja do `.vpk` datoteke mape.

## Kako nastaje {#how-it-is-made}

1. **Kolizijska mreža.** Source2Viewer izvozi
   `maps/<map>/world_physics.vmdl_c` iz `maps/<map>.vpk` kao glTF. Njegove grupe
   nose imena po površini. Grupe nazvane `clip` (nevidljivi zidovi) ili `sky`
   se odbacuju. Grupe nazvane `water`, `slime` ili `window` su **voda**: rijeka
   i bare su `water_slime`, uski potoci kroz džunglu su `window`; na snimku
   heroji stoje 10 do 16 jedinica ispod prve, a nekoliko jedinica ispod druge.
   Zadržavaju se samo njihove gornje strane. Sve ostalo je teren, podijeljen
   stranu po stranu: strana čija normala gleda naviše za najmanje 0,7 (nagibi do
   oko 45 stepeni) je **tlo**, ostatak - strane litica, zidovi mape - je
   **struktura**.
2. **Entiteti.** Source2Viewer dekompajlira entitetske blokove mape
   (`maps/<map>/entities/*.vents_c`) u tekst: blokovi s naslovom `====<n>====`,
   po jedan `key value` u liniji. Koriste se blokovi `default_ents` i svaki
   svjetski sloj koji tamo entitet `info_world_layer` prikazuje na početku
   (zastavica spawn 1) - slojevi dviju baza. Slojevi koji počinju skriveni
   sadrže ono što se pojavi kad baza padne i izostavljaju se.
3. **Šta se crta.** Drveće (`ent_dota_tree`) i zgrade: tornjevi, barake,
   ancienti (`npc_dota_fort`), punila (`npc_dota_building`), osmatračnice,
   fontane, svetišta mudrosti, lotos bazeni, blizanačka vrata, posmatrači
   (`npc_dota_lantern`) i neutralne skrivnice predmeta. Prodavnice (prodavač je
   lik), kuća slavnih, zastave, svjetla i čestice se ne crtaju.
4. **Modeli.** Svaki model koji ovi entiteti imenuju izvozi se iz
   `game\dota\pak01_dir.vpk` u jednom pokretanju programa Source2Viewer. Mreže
   modela koje su drugo stanje iste stvari - panj posječenog drveta, krupni plan
   prikazan u inspektoru, ruševine - izostavljaju se po imenu (`stump`,
   `inspector`, `destruction`).
5. **Zgrade** su vlastita mreža njihovog modela, prorijeđena **grupisanjem
   vrhova**: svaka tačka se pomjera na srednju vrijednost tačaka u njenoj kocki
   veličine `--detail` (zadano 8 jedinica, oko trećina širine heroja), a
   trouglovi koji se skupe ili ponove otpadaju. 0 zadržava svaki trougao.
6. **Drveće** je obris svakog modela kao nizak okrenuti čvrsti oblik: njegova
   visina u pet pojaseva, svaki šestostrani prsten širok koliko većina tačaka
   modela na toj visini (90. percentil njihove udaljenosti od ose debla), zatvoren
   pri dnu i šiljast na vrhu - 60 trouglova, prava visina i širina modela. Bor
   ispadne kupa, hrast kugla na stabljici. Prave mreže bi imale oko deset puta
   veću težinu na preko 2.000 stabala.
7. **Postavljeno** kako ga igra postavlja: skalirano pomoću `scales`, okrenuto
   pomoću `angles` (Sourceov pitch, yaw, roll u stepenima), pomjereno na
   `origin`.
8. **U okvir preglednika.** Source2Viewer piše glTF u metrima, Y gore: igrino
   (Y, Z, X) puta 0,0254. To se poništava i svaka tačka se zapisuje kao
   (X, Z, -Y) igre: Y gore, igrin Y negiran - okvir u kojem se crtaju tabele
   Dote preko svojih `heat3d` savjeta (`up: z`, `flipY: true`, skala 1).
   Rotacija, ne zrcaljenje.

## Datoteka {#the-file}

glTF 2.0 binarna datoteka kao kod alata 3DHeat za CS2 (vidite njegovu stranicu o
izvozu mape): jedan čvor i jedna mreža po dijelu u korijenu, bez transformacija,
sa ravnim sjenčenjem (jedan vrh po uglu trougla koji nosi normalu svog
trougla), `uint32` indeksi, bez materijala, tekstura ili UV-ova,
`asset.generator` `heat3d_watch`, jedinice igre.

| Dio | Šta |
|---|---|
| `ground:terrain` | tlo po kojem se može hodati |
| `structure:terrain` | strane litica i zidovi mape |
| `water:water_slime`, `water:window` | rijeka i bare; potoci u džungli |
| `structure:tree` | svako drvo koje stoji na početku |
| `structure:tower`, `structure:barracks`, `structure:ancient`, `structure:filler`, `structure:outpost`, `structure:fountain`, `structure:shrine`, `structure:lotus_pool`, `structure:twin_gate`, `structure:watcher`, `structure:neutral_stash` | zgrade, po vrsti |

Prefiks `ground:` / `structure:` / `water:` je način na koji svi izvoznici
nivoa za 3DHeat govore pregledniku šta je dio; on im vjeruje na riječ. Pošto su
jedinice igre (oko jedan inč svaka), drugi glTF preglednik prikazuje mapu oko 39
puta prevelikom; u 3DHeat leži tačno ispod tabele.

Šta ispisuje, na primjeru pokretanja (brojevi zavise od verzije mape):

```text
reading dota.vpk: collision mesh and entities
reading 30 models from pak01_dir.vpk
dota.glb: dota, 700,000 triangles (230,000 ground) in 16 parts; 2,400 trees, 70 buildings
```

Prve dvije linije idu na izlaz za greške, zadnja na izlaz. Model koji
Source2Viewer nije mogao naći izostavlja se i imenuje na kraju zadnje linije
(`; 1 model(s) not found, left out: ...`). Greške - Dota 2 nije nađena, mapa nije
nađena, Source2Viewer nije nađen ili ne radi - ispisuju `dota-map: <why>` i
izlaze s kodom 1.

## Kako je provjereno {#how-it-was-checked}

Na snimku javnog meča koji je watcher pretvorio (patch 7.40) i mapi
instalirane igre:

- svaki uzorak pozicije heroja koji gleda pravo dolje za najvišom stranom tla
  najviše 64 jedinice iznad njegovih stopala nalazi tlo, medijan visine iznad
  njega je 0 jedinica, a 99,5 % je unutar 16 jedinica; sa zrcaljenom mapom (Y
  nije negiran) samo oko pola nalazi tlo, a ostali lebde ili tonu za visinu
  litice;
- 22 tornja, 12 baraka, 2 ancienta, 14 punila, 2 osmatračnice, 2 fontane i 10
  posmatrača koje tabela jedinica snimka postavlja stoje na entitetima mape iste
  vrste s tačnošću od 0,02 jedinice, vodoravno i po visini;
- stopalo svakog drveta je na tlu.

Testovi (`tests/test_dota_map.py`) provjeravaju čitač blokova, okvire, podjelu
terena, obrise drveća i grupisanje, postavljanje i cijeli izvoz sa
Source2Viewerom kojeg glumi zamjena - samo na izmišljenim podacima.

## Šta ne radi {#what-it-does-not-do}

- Nema tekstura ni boja: preglednik nijansira nivo na svoj način.
- Nema drveća posječenog ni zgrada uništenih tokom meča: mapa kakva je na početku.
- Događajske i prilagođene mape nisu testirane; njihove klase entiteta se mogu razlikovati.
- Rekviziti koji samo ukrašavaju (kamenje, ograde, zastave) u njoj su samo ukoliko
  su dio kolizijske mreže.
