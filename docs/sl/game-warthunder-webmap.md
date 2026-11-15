---
title: "War Thunder (stanje igre)"
nav_order: 47
lang: "sl"
source: game-warthunder-webmap.md
source_hash: "d6026c277030"
nav_exclude: true
search_exclude: true
---
# War Thunder (stanje igre) {#war-thunder-game-state}

Medtem ko igrate War Thunder, watcher shrani, kaj igra sporoča programom na vašem računalniku, da lahko to pozneje pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `warthunder-webmap`, vrsta [`gsi`](sources-and-rules.md); teče, dokler je `aces.exe` zagnan, in novih podatkov išče vsakih 0,5 s.*

## Kaj se zapiše {#what-is-recorded}

- lastni položaj (zemljevid vzhod/sever v metrih; višina iz /state v letalu, sicer 0), smer in hitrost, dvakrat na sekundo
- pojavitve in odhod lastnega vozila z zemljevida (uničen, pristal, nazaj v hangar), en prelet za vsakega
- drugi letala in kopenske enote na mini zemljevidu kot položaji s sledenimi id-ji in stranjo (brez višine)
- letališča, zone zajema in baze enkrat, ter zone, ki menjajo stran
- vrstice napadov in škode (kdo, vozilo, glagol); igralčeva pobitja in smrti, kadar je vaše ime nastavljeno (`config --set player_names.warthunder-webmap=<name>`)
- pojavitve, razdalja, največja višina, največja prava zračna hitrost, vozilo; pobitja in smrti z nastavljenim vašim imenom
- vsak odgovor spletnega zemljevida, ohranjen v celoti v heat.raw.parquet - celoten /state in /indicators, klepet, cilji bitke in slika zemljevida vključeni; med bitkami v svoji seji

## Od kod prihaja {#where-it-comes-from}

lokalni spletni zemljevid igre, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Kako ga vklopiti {#how-to-switch-it-on}

Ničesar ni treba vklapljati: watcher bere vir, kakor ga da igra ali platforma.

## Kako deluje {#how-it-works}

War Thunder: lokalni spletni zemljevid igre na <http://127.0.0.1:8111>.

Igra streže stran, ki jo lahko prikaže drugi zaslon ali telefon ("spletni zemljevid"), in JSON za njo, medtem ko teče - v vsakem načinu, tudi igri z več igralci:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: obseg zemljevida v metrih; valid je false v hangarju
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 slike zemljevida, y navzdol), "dx", "dy" (smer),
                  airfields "sx", "sy", "ex", "ey"}]: kar prikazuje mini zemljevid, lastno vozilo igralca
                  z ikono "Player"; brez id-jev, brez višin
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: vrednosti leta,
                  veljavne samo v letalu
/indicators      {"valid", "army": air|tank|..., "type": vozilo}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} novejše od podanih id-jev, vsak
                  {"id", "msg", "sender", "enemy", "mode", "time"}; vrstice škode so kot
                  "Name (Vehicle) shot down Name (Vehicle)"
/gamechat?lastId=N  klepet, novejši od podanega id-ja, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    cilji bitke in njihovo stanje
/map.img         slika zemljevida, na katero stran riše predmete
```

Vsak odgovor je ohranjen v celoti v surovi spremljevalni datoteki seje pod svojo končno točko (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img); med bitkami gredo odgovori v svojo sejo.

Položaj na zemljevidu se pretvori v metre z obsegom: u = min_x + x \* (max_x - min_x) vzhodno, v = max_y - y \* (max_y - min_y) severno (y slike teče navzdol). Vrstice so x = u, y = višina (lastna "H, m" letala; 0 za vse drugo), z = v, tako da je Y navzgor; z je zrcaljen za pregledovalnik, da sever ni narisan na jug.

Barve povedo strani, kakor jo vidi igralec: lastna rumena (#faC81E privzeto), skupina zelena, zavezniki modra (#174DFF), sovražniki rdeča (#f40C00); palete za barvno slepe barve spremenijo, zato odloča odtenek, ne točna vrednost. Igra nikogar na zemljevidu ne imenuje in predmetom ne daje id-jev: drugim predmetom tu id-je dodelimo tako, da jih sledimo od ankete do ankete (najbližji istega tipa in ikone), kar lahko zamenja dve letali iste vrste, ki preletita blizu. Igralčevo lastno ime tudi ni v API-ju: vnesite ga v nastavitvah (`config --set player_names.warthunder-webmap=<your name>`) in vrstice napadov o igralcu postanejo pobitja in smrti; brez tega se zapišejo kot vrstice napadov.

Viri: lastna stran igre na <http://127.0.0.1:8111> in njen JSON; dejstva o poljih, kakor jih dokumentira projekt JoyPro 2 (docs/telemetry-recording.md; GPL, uporabljeno samo za dejstva).

## Osi položajev {#positions-and-axes}

| | |
|---|---|
| Zapisani položaji | da |
| Os navzgor | `y` |
| Enote | metri (zemljevid vzhod/sever; višina samo za lastno letalo) |
| Zrcaljeno za pregledovalnik | `z` |
| Merilo enot (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

Ti gredo v `meta.json` vsake seje (`axes`) in, kadar ima seja položaje, v nogo `heat.parquet`, tako pregledovalnik sam obrača in meri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igrano na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `gsi`: bere samo to, kar igra ali platforma objavi (game-state integration ali lokalni API, ki ga igra streže), zato zapisuje tudi pri igri na spletu, tako kot offline; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igrano na spletu - glej [Viri in pravila](sources-and-rules.md).

## Statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavi po imenu (`stats` vsake seje v `meta.json` in tabela `stats` v `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz lastnih imen statistik igre, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali ohrani, nikoli ne izpusti. Poleg vrstic je vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, ohranjen v celoti v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text`, nato vsako polje, ohranjeno po imenu; `used` označi, kar je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- /map_info.json: obseg in mreža zemljevida (metri, id zemljevida) v meta.json; neveljaven konča bitko
- /map_obj.json (dvakrat na sekundo): lastno vozilo, drugi letalniki in kopenske enote (sledeni id-ji, stran iz barve, ikona, smer, barva), letališča, cone in baze kot vrstice
- /state (dvakrat na sekundo, v letalu): višina, TAS, IAS, Mach in Vy na lastnih vrsticah
- /indicators (vsaki 2 s): vojska in tip vozila
- /hudmsg (enkrat na sekundo): vrstice napadov in škode kot pobitja, smrti, zadetki in vrstice napadov; drugi dogodki HUD kot vrstice

**Ohranjeno surovo**

- vsak odgovor v celoti, `text` je JSON, kakor ga je poslala igra, pod svojo končno točko: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` so bajti slike zemljevida kot `payload`, enkrat na bitko
- kar samo surova spremljevalna datoteka drži: vsako polje /state preko petih prebranih (AoA, AoS, Ny, Wx, plin, vrtljaji, gorivo, ...; eno letalo ima drugačen nabor kot drugo), vsako polje /indicators (inštrumenti v kabini letal, hitrost, prestava, posadka in stabilizator tankov), drugi ključi predmetov zemljevida (color[], blink, icon_bg, konci letališč), sender, enemy in mode v hudmsg, klepet (/gamechat, enkrat na sekundo), cilji bitke in njihovo stanje (/mission.json, na 10 s v bitki), vrstice, izrečene, preden se je watcher zagnal
- med bitkami (hangar, nalaganje) gredo odgovori v svojo sejo, označeno kot `between_battles` v meta.json, ki nima vrstic

**Ni na voljo**

- imena, id-ji in višine vozil drugih igralcev: spletni zemljevid jih nima (id-je tu dodelimo tako, da predmete sledimo od ankete do ankete); vrstice napadov igralce imenujejo brez položajev
- vse zunaj spletnega zemljevida: replaye bere pretvornik replayev War Thunder, pomnilnik igre pa se nikoli ne bere (igra na spletu)
- /map_obj.json hitreje kot dvakrat na sekundo: hitrost anketiranja je ohranjena nizka, da spletni strežnik igre ni preobremenjen

**Velikost**: okoli 50-120 MB na uro JSON pred zstd v bitki (map_obj 5-15 KB dvakrat na sekundo, state okoli 1,5 KB dvakrat na sekundo, indicators na 2 s, klepet in vrstice HUD majhni) plus slika zemljevida enkrat na bitko (pod 2 MB); 1-2 MB na uro med bitkami (pogled zemljevida dvakrat na sekundo, HUD in klepet enkrat, vsak kratek odgovor); zstd ponavljajoč se JSON zmanjša več kot desetkrat

## Preverjeno {#verified}

preizkušeno na lokalnem lažnem strežniku, ki streže odgovore v obliki spletnega zemljevida igre; nepreizkušeno na tekoči igri

## Vir {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
