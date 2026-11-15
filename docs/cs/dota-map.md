---
title: "Mapa Dota 2"
nav_order: 6.5
lang: "cs"
source: dota-map.md
source_hash: "c9830d37ea89"
nav_exclude: true
search_exclude: true
---
# Mapa Dota 2 jako úroveň (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

zapíše mapu Dota 2 jako geometrii úrovně pro prohlížeč 3DHeat: zemi, útesy, vodu, každý strom a budovy, ve souřadnicích a jednotkách, v jakých se kreslí [tabulky replayů Dota 2](game-dota-replays.md). Načtěte soubor `.glb` v panelu **Pozadí / úroveň** prohlížeče (**3D model…**) pod tabulkou Dota a teplo hrdinů poleží na lanech, věže na svých věžích. Prohlížeč soubor pozná podle jeho částí a uloží ho do své knihovny úrovní; od té doby jeho tlačítko **Mapa Dota 2** načítá tuto 3D mapu místo kresby z OpenDota. Kód: [`heat3d_watch/decoders/dota_map.py`](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/decoders/dota_map.py).

K tomu je potřeba nainstalovaná Dota 2 a příkazová řádka Source2Viewer. Nástroje neobsahují nic z hry a nic nestahují: mapa pochází z vaší vlastní instalace a soubor, který zapíšou, je vaše si ponechat, ne sdílet – mapa patří společnosti Valve.

## Co je potřeba {#what-it-needs}

- **Dota 2**, nainstalovaná přes Steam. Bez `--game` se hledá jako `steamapps\common\dota 2 beta\game\dota` v každé knihovně Steamu. `--game` přijme složku `dota 2 beta`, nebo její složku `game\dota`.
- **Příkazová řádka Source2Viewer** (ValveResourceFormat, MIT, [vydání](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)): `--source2viewer`, pak proměnná prostředí `HEAT3D_SOURCE2VIEWER`, pak `Source2Viewer-CLI` / `Source2Viewer-CLI.exe` na `PATH` – stejně jako příkaz `map` nástroje 3DHeat CS2, takže jedna kopie slouží oběma.
- numpy (Watcher ho už potřebuje).

`<map>` je `dota` (výchozí: běžná mapa), nebo jméno jiné mapy ve složce `game\dota\maps\`, nebo cesta k `.vpk` mapy.

## Jak se vyrábí {#how-it-is-made}

1. **Kolizní síť.** Source2Viewer exportuje z `maps/<map>.vpk` soubor `maps/<map>/world_physics.vmdl_c` jako glTF. Jeho skupiny jsou pojmenované podle povrchu. Skupiny `clip` (neviditelné stěny) a `sky` se zahodí. Skupiny `water`, `slime` nebo `window` jsou **voda**: řeka a jezírka jsou `water_slime`, úzké potoky v džungli jsou `window`; na replayi hrdinové stojí 10 až 16 jednotek pod prvními a několik jednotek pod druhými. Ponechají se jen jejich horní plochy. Všechno ostatní je terén, rozdělený plochu po ploše: plocha, jejíž normála směřuje nahoru aspoň o 0,7 (svahy do zhruba 45 stupňů), je **země**; zbytek – stěny útesů, zdi mapy – je **stavba**.
2. **Entity.** Source2Viewer dekompiluje bloky entit mapy (`maps/<map>/entities/*.vents_c`) do textu: bloky označené `====<n>====`, na řádek jeden `klíč hodnota`. Použité bloky jsou `default_ents` a každá vrstva světa `info_world_layer` v nich, která se na začátku ukazuje (příznak spawnu 1) – vrstvy obou základen. Vrstvy, které začínají skryté a obsahují to, co se objeví, když padne základna, se vynechají.
3. **Co se kreslí.** Stromy (`ent_dota_tree`) a budovy: věže, kasárna, ancienti (`npc_dota_fort`), výplně (`npc_dota_building`), výhledy, fontány, svatyně moudrosti, lotosová jezírka, dvojitá brána, strážci (`npc_dota_lantern`) a neutrální sklady předmětů. Obchody (obchodník je postava), síň slávy, prapory, světla a částice se nekreslí.
4. **Modely.** Každý model, který tyto entity jmenují, se exportuje z `game\dota\pak01_dir.vpk` v jednom běhu Source2Viewer. Části modelu, které jsou jiným stavem téže věci – pařez po pokácení stromu, detailní pohled v inspektoru, suť –, se vynechají podle jména (`stump`, `inspector`, `destruction`).
5. **Budovy** jsou vlastní síť svého modelu, zjednodušená **shlukováním vrcholů**: každý bod se přesune na průměr bodů v krychli velikosti `--detail` (výchozí 8 jednotek, asi třetina šířky hrdiny), a trojúhelníky, které se scvrknou nebo se opakují, zmizí. 0 ponechá každý trojúhelník.
6. **Stromy** jsou obrys každého modelu jako nízké otočené těleso: jeho výška v pěti pásmech, každé šestiúhelníkové mezikruží tak široké, jak jsou široké většiny bodů modelu v dané výšce (90. percentil jejich vzdálenosti od osy kmene), na dně uzavřené a nahoře zašpičatělé – 60 trojúhelníků, skutečná výška a šířka modelu. Smrk vyjde jako kužel, dub jako koule na kmínku. Skutečné sítě by u více než 2 000 stromů vážily asi desetkrát víc.
7. **Umístění** tak, jak je hra umisťuje: zvětšeno podle `scales`, otočeno podle `angles` (sklon, natočení a naklonění v Source, ve stupních), přesunuto na `origin`.
8. **Do souřadnic prohlížeče.** Source2Viewer zapisuje glTF v metrech, osa Y nahoru: (Y, Z, X) hry krát 0,0254. To se vrátí zpět a každý bod se zapíše jako (X, Z, -Y) hry: Y nahoru, Y hry obrácená – soustava, ve které se kreslí tabulky Dota přes jejich nápovědy `heat3d` (`up: z`, `flipY: true`, měřítko 1). Je to otočení, ne zrcadlení.

## Soubor {#the-file}

Binární glTF 2.0 jako u exportu mapy nástroje 3DHeat CS2 (viz jeho stránka o exportu mapy): jeden uzel a jedna síť na každou část v kořeni, bez transformací, s plochým stínováním (vrchol na každém rohu trojúhelníku nese normálu svého trojúhelníku), indexy `uint32`, bez materiálů, textur a UV, `asset.generator` `heat3d_watch`, jednotky hry.

| Část | Co je to |
|---|---|
| `ground:terrain` | zem, po které se dá chodit |
| `structure:terrain` | stěny útesů a zdi mapy |
| `water:water_slime`, `water:window` | řeka a jezírka; potoky v džungli |
| `structure:tree` | každý strom stojící na začátku |
| `structure:tower`, `structure:barracks`, `structure:ancient`, `structure:filler`, `structure:outpost`, `structure:fountain`, `structure:shrine`, `structure:lotus_pool`, `structure:twin_gate`, `structure:watcher`, `structure:neutral_stash` | budovy, podle druhu |

Předpona `ground:` / `structure:` / `water:` je způsob, jakým všechny exportéry úrovní 3DHeat říkají prohlížeči, čím část je; prohlížeč jim věří na slovo. Protože jednotky jsou herní (zhruba palec každá), jiný prohlížeč glTF ukáže mapu asi 39krát větší; v 3DHeat leží přesně pod tabulkou.

Co vypíše na příkladovém běhu (čísla závisí na verzi mapy):

```text
reading dota.vpk: collision mesh and entities
reading 30 models from pak01_dir.vpk
dota.glb: dota, 700,000 triangles (230,000 ground) in 16 parts; 2,400 trees, 70 buildings
```

První dva řádky jdou do chybového proudu, poslední do výstupu. Model, který Source2Viewer nenašel, se vynechá a jmenuje se na konci posledního řádku (`; 1 model(s) not found, left out: ...`). Chyby – nenalezená Dota 2, mapa, Source2Viewer nebo jeho selhání – vypíšou `dota-map: <why>` a skončí s kódem 1.

## Jak se ověřila {#how-it-was-checked}

Na replayi veřejného zápasu, který převedl Watcher (patch 7.40), a na mapě nainstalované hry:

- každý vzorek pozice hrdiny, když se podíváme kolmo dolů na nejvyšší plochu země nejvýš 64 jednotek nad jeho nohama, najde zemi; medián výšky nad ní je 0 jednotek a 99,5 % je do 16 jednotek; se zrcadlenou mapou (Y neobrácená) ji najde jen asi polovina, a zbytek se vznáší nebo propadá o výšku útesu;
- 22 věží, 12 kasáren, 2 ancienti, 14 výplní, 2 výhledy, 2 fontány a 10 strážců, které tabulka jednotek replaye umisťuje, stojí na entitách mapy stejného druhu s odchylkou do 0,02 jednotky, vodorovně i ve výšce;
- noha každého stromu je na zemi.

Testy (`tests/test_dota_map.py`) ověřují čtečku bloků, souřadné soustavy, rozdělení terénu, obrysy a shlukování stromů, umístění a celý export se Source2Viewer nahrazeným zástupcem – jen na vymyšlených datech.

## Co nedělá {#what-it-does-not-do}

- Žádné textury ani barvy: prohlížeč úroveň stíní po svém.
- Žádné pokácené stromy ani zničené budovy během zápasu: mapa tak, jak začíná.
- Mapy událostí a vlastní mapy nejsou ověřené; jejich třídy entit se mohou lišit.
- Rekvizity, které jen zdobí (kameny, ploty, prapory), jsou v ní jen potud, pokud jsou součástí kolizní sítě.
