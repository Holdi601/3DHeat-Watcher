---
title: "Star Citizen (lokitiedostot)"
nav_order: 41
lang: "fi"
source: game-starcitizen.md
source_hash: "7b1ce51dc50a"
nav_exclude: true
search_exclude: true
---
# Star Citizen (lokitiedostot) {#star-citizen-log-files}

Kun pelaat Star Citizeniä, watcher lukee pelin kirjoittamat tiedostot ja tallentaa, mitä tapahtui, jotta voit myöhemmin katsoa sen tilastoina ja aikajanana.

*Tekniset tiedot: sovitin `starcitizen`, tyyppi [`log`](sources-and-rules.md); se toimii, kun `StarCitizen.exe` on käynnissä, ja etsii uutta dataa 0,5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- kuolemat uhrin, tappajan, aseen, vahinkotyypin ja vyöhykkeen kanssa (pelaajat ja NPC:t)
- ajoneuvot, jotka poistettiin käytöstä ja tuhottiin, kuljettajan, syyn ja vyöhykkeen kanssa
- kvanttimatkan kohteet, aurinkokunnan vaihdot, ilmestymiset, uudelleensyntymiset, kyvyttömyydet
- jokainen Game.log-rivi sellaisenaan tiedostossa heat.raw.parquet
- tapot (pelaaja ja NPC), kuolemat, itsemurhat, tuhotut ja menetetyt ajoneuvot, kvanttihypyt

## Mistä data tulee {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (käynnissä olevan StarCitizen.exe:n buildikansio), vain pelin kirjoittama lokitiedosto. Peli käyttää Easy Anti-Cheatia: mikään ei koske sen prosessiin.

## Miten se kytketään päälle {#how-to-switch-it-on}

Mitään ei tarvitse kytkeä päälle: watcher lukee lähteen juuri sellaisena kuin peli tai alusta sen antaa.

## Miten se toimii {#how-it-works}

Star Citizen: asiakkaan oma loki, `<install>\StarCitizen\LIVE\Game.log`.

Peli kirjoittaa Game.log-tiedoston uudelleen jokaisella käynnistyksellä (edellinen menee kansioon `logbackups\`). Vain tämä tiedosto luetaan: Star Citizen käyttää Easy Anti-Cheatia, eikä tämä kosketa pelin prosessia. Rivit alkavat UTC-aikaleimalla ja tasolla, sitten tagilla kulmasulkeissa:

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

(Tässä rivitetty; tiedostossa jokainen on yhdellä rivillä.) Kuoleman vyöhyke on yleensä alus, jossa uhri istui, ei paikka. Muotoa ei ole dokumentoinut Cloud Imperium, ja se muuttuu korjauspäivitysten välillä. Kuviot seuraavat rivejä, joita yhteisön tappajaseurantatyökalut lukevat (esim. <https://github.com/DimmaDont/all-slain>, MIT, vain tosiasiat). Kaikki, mikä ei täsmää, ohitetaan eikä arvata. Aluksen `pos` on vyöhykkeeseen suhteutettu, ja se tallennetaan vain tekstinä: koordinaatteja ei piirretä.

Jokainen rivi tallennetaan sellaisenaan session raakatiedostoon (3DHeatin muunninsääntö), täsmäsi se tai ei: `type` on rivin tagi kulmasulkeissa (`Actor Death`, `Spawn Flow` ...), muuten sen ensimmäinen hakasulkeissa oleva sana (`Notice`, `CSessionManager::OnClientSpawned` ...), muuten `untagged`. Rivi ilman aikaleimaa on `untimed`.

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | ei |
| Ylösakseli | `y` |
| Yksiköt | sijainteja ei tallenneta |
| Peilattu katselinta varten | ei mitään |
| Yksikköskaala (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`:n kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`:n footeriin. Näin 3DHeat-katselin kääntää ja skaalaa rivit itse, katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "allowed (reads only what the game publishes)".
- Tyyppi `log`: se lukee vain sen, minkä peli tai alusta antaa ulos (pelin ajon aikana kirjoittamat tiedostot). Siksi se tallentaa myös verkkopelissä, aivan kuten offline-pelissä. Lippu ratkaisee vain sen, saako muistia koskaan lukea.
- Muisti: tämän sovittimen lukema **ei koskaan**. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty verkkopeliksi. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (session `stats` tiedostossa `meta.json` ja taulussa `stats` tiedostossa `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Aaltosulkeissa oleva avain täydentyy ajon aikana (`score.{team}` on yksi avain per joukkue). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä listassa. Kohdassa "Mitä tallennetaan" ne on nimetty.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunninsääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): se, mitä lähde sisältää, luetaan tai tallennetaan, eikä mitään pudoteta. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan sellaisenaan session tiedostoon `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja sen jälkeen nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon, ja `lost` on 0.

**Luettu**

- `<Actor Death>`: uhri, tappaja, ase ja sen luokka, vahinkotyyppi, vyöhyke; NPC tai pelaaja
- `<Vehicle Destruction>`: ajoneuvo, vyöhyke, vyöhykkeeseen suhteutettu sijainti tekstinä, kuljettaja, syy, tapa, tuhoamistaso
- `<Quantum Navtarget>` -kohteet, `<Changing Solar System>`, `OnClientSpawned`, sairaalasta uudelleensyntymiset, kyvyttömyydet syineen, `EndSession`
- pelaajan tunnus (handle) rivistä `<AccountLoginCharacterStatus_Character>` tai kirjautumisrivistä

**Tallennettu raakana**

- jokainen Game.log-rivi sellaisenaan, `type` on sen tagi kulmasulkeissa (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory` ...), muuten sen ensimmäinen hakasulkeissa oleva sana (`Notice`, `CSessionManager::OnClientSpawned` ...), muuten `untagged`; rivit ilman aikaleimaa (lokin otsikko, rivitetty teksti) tyypillä `untimed`; `used` siellä, missä rivistä tuli rivi

**Ei saatavilla**

- sijainnit: loki ei anna yhtään kehyksessä, joka voitaisiin piirtää (tuhoutuneen ajoneuvon `pos` on suhteessa vyöhykkeeseen, jonka paikkaa ei ole kirjattu)
- kaikki pelin prosessista tai verkosta: Star Citizen käyttää Easy Anti-Cheatia; luetaan vain lokitiedosto
- aiempien käynnistysten lokit (`logbackups`): jokaisen käynnistyksen Game.log tallennetaan, kun se pelataan
- rivit muodossa, jonka korjauspäivitys muuttaa: tallennetaan raakana ja dekoodataan uudelleen, kun uusi muoto tunnetaan

**Koko**: Game.log kasvaa noin 5–15 Mt pelattua tuntia kohden (enemmän vilkkailla alueilla ja virheiden kanssa); zstd tekee heat.raw.parquetista noin kymmenesosan

## Todennettu {#verified}

Testattu synteettisillä Game.log-riveillä muodossa, jonka yhteisön seurantatyökalut dokumentoivat. Peliä vastaan ei ole testattu.

## Lähdekoodi {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
