---
title: "Star Citizen (annálsskrár)"
nav_order: 41
lang: "is"
source: game-starcitizen.md
source_hash: "7b1ce51dc50a"
nav_exclude: true
search_exclude: true
---
# Star Citizen (annálsskrár) {#star-citizen-log-files}

Meðan þú spilar Star Citizen les watcher skrárnar sem leikurinn skrifar og vistar það sem gerðist, svo þú getir skoðað það síðar sem tölfræði og tímalínu.

*Tæknilegar upplýsingar: millistykki `starcitizen`, gerð [`log`](sources-and-rules.md); það keyrir meðan `StarCitizen.exe` er í gangi og leitar að nýjum gögnum á 0,5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- dauðsföll með fórnarlambi, banamanni, vopni, tegund skaða og svæði (leikmenn og NPC)
- farartæki sem eru óvirk og eytt, með ökumanni, orsök og svæði
- áfangastaðir skammtaferða (quantum travel), breytingar á sólkerfi, endurkoma (spawn), endurfæðing, ómeðvitund
- sérhver lína úr Game.log heil í heat.raw.parquet
- dráp (leikmanna og NPC), dauðsföll, sjálfsvíg, farartækjum eytt og glötuðum, skammtastökk

## Hvaðan það kemur {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (byggingarmappa StarCitizen.exe sem er í gangi), aðeins annálsskráin sem leikurinn skrifar - leikur með Easy Anti-Cheat: ekkert snertir ferli hans

## Hvernig kveikt er á því {#how-to-switch-it-on}

Ekki þarf að kveikja á neinu: watcher les heimildina eins og leikurinn eða vettvangurinn lætur hana í té.

## Hvernig það virkar {#how-it-works}

Star Citizen: eigin annáll biðlarans, `<install>\StarCitizen\LIVE\Game.log`.

Leikurinn skrifar Game.log upp á nýtt við hverja ræsingu (sú fyrri fer í
`logbackups\`). Aðeins sú skrá er lesin: Star Citizen keyrir Easy Anti-Cheat, og
ekkert hér kemur nálægt ferli leiksins. Línur byrja á UTC-tímastimpli og
stigi, svo merki í oddklofum:

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

(brotið hér; ein lína hver í skránni). Svæði dauðsfalls er yfirleitt
skipið sem fórnarlambið sat í, ekki staður. Sniðið er ekki skjalað af Cloud
Imperium og breytist milli plástra; mynstrin fylgja línunum sem samfélagsverkfæri
fyrir dráp lesa (t.d. <https://github.com/DimmaDont/all-slain>, MIT - aðeins
staðreyndir), og allt sem passar ekki er sleppt, ekki giskað á það. `pos` farartækis
er miðað við svæði og aðeins geymt sem texti: engin hnit eru teiknuð.

Sérhver lína er geymd heil í hráu hliðarskrá lotunnar (umbreytingarregla
3DHeat), hvort sem hún passar eða ekki: `type` er merki línunnar í oddklofum (`Actor
Death`, `Spawn Flow`, ...), annars fyrsta orðið í hornklofum (`Notice`,
`CSessionManager::OnClientSpawned`), annars `untagged`; lína án
tímastimpils er `untimed`.

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | nei |
| Upp-ás | `y` |
| Einingar | engar staðsetningar skráðar |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem „allowed (reads only what the game publishes)“.
- Gerð `log`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (skrár sem leikurinn skrifar meðan hann keyrir), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- `<Actor Death>`: fórnarlamb, banamaður, vopn og flokkur þess, tegund skaða, svæði; NPC eða leikmaður
- `<Vehicle Destruction>`: farartæki, svæði, staða miðað við svæði sem texti, ökumaður, orsök, hvernig, eyðingarstig
- `<Quantum Navtarget>` áfangastaðir, `<Changing Solar System>`, `OnClientSpawned`, endurfæðing á sjúkrahúsi, ómeðvitund með orsökum, `EndSession`
- auðkenni spilarans úr `<AccountLoginCharacterStatus_Character>` eða innskráningarlínunni

**Geymt hrátt**

- sérhver lína úr Game.log heil, `type` = merki hennar í oddklofum (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), annars fyrsta orðið í hornklofum (`Notice`, `CSessionManager::OnClientSpawned`, ...), annars `untagged`; línur án tímastimpils (haus annálsins, brotinn texti) sem `untimed`; `used` þar sem línan varð að röð

**Ekki fáanlegt**

- staðsetningar: annállinn gefur engar í ramma sem hægt er að teikna (`pos` eyðilagðs farartækis er miðað við svæði þar sem staðurinn er ekki skráður)
- nokkuð úr ferli leiksins eða netkerfi: Star Citizen keyrir Easy Anti-Cheat; aðeins annálsskráin er lesin
- annálar fyrri ræsinga (`logbackups`): Game.log hverrar ræsingar er geymd þegar hún er spiluð
- línur á sniði sem plástur breytir: geymdar hráar, afkóðaðar aftur þegar nýja formið er þekkt

**Stærð**: Game.log stækkar um 5-15 MB á klukkustund af spilun (meira á annasömum svæðum og með villum); zstd í heat.raw.parquet gerir þetta um tíunda hluta

## Staðfest {#verified}

prófað á tilbúnum línum úr Game.log á sniðinu sem samfélagsverkfæri skjala; óprófað á móti leiknum

## Heimild {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
