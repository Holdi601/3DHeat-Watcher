---
title: Dota 2 -kartta
nav_order: 6.5
lang: "fi"
source: dota-map.md
source_hash: "3dcde11c7784"
nav_exclude: true
search_exclude: true
---
# Dota 2 -kartta tasona (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

Dota 2 -kartan kolmiulotteisen version — maan, kallioiden, veden, jokaisen puun ja rakennukset siinä kehyksessä ja yksiköissä, joissa [Dota 2 -tallennetaulukot](game-dota-replays.md) piirretään — tekee oma työkalunsa, **3DHeat Dota** ([3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota), [dokumentaatio](https://holdi601.github.io/3DHeat-Ext-Dota/)). Se lukee Valven pelitiedostoja, joten se on pidetty vahdin ulkopuolella: jos se joskus pitää poistaa, vahti pysyy.

Asenna se kerran, kuten sen [Ennen aloitusta](https://holdi601.github.io/3DHeat-Ext-Dota/before-you-start.html)-sivu kertoo (Python-paketti sekä Source2Viewerin komentorivityökalu). Aja sen jälkeen jompikumpi:

```bash
heat3d-dota-maps level -o dota.glb
```

tai vahdin kautta:

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

Vahdin komento ajaa `heat3d-dota-maps level` -komennon samoilla asetuksilla ja välittää sen tulosteen ja poistumiskoodin eteenpäin. Vahti löytää työkalun `heat3d-dota-maps`-komentona PATH:lta, asennettuna `heat3d_ext_dota`-pakettina tai sen lähdekansiona muuttujassa `HEAT3D_DOTA_MAPS` tai vahdin vieressä (`exporters/ext/dota-maps` 3DHeat-kopiossa). Mitään siitä ei tuoda vahtiin; sitä vain ajetaan. Kun työkalua ei ole missään, `dota-map` kertoo, mistä sen saa, ja poistuu koodilla 2.

Lataa `.glb` katselimen **Tausta / kenttä** -paneelissa (**3D-malli…**) Dota-taulukon alla. Katselin tunnistaa tiedoston osiensa perusteella ja pitää sen kenttäkirjastossaan, ja sen **Dota 2 -kartta** -painike lataa sen siitä lähtien. Miten taso tehdään, mistä osista se koostuu ja miten se tarkistettiin: [Tason rakentaminen](https://holdi601.github.io/3DHeat-Ext-Dota/level.html).
