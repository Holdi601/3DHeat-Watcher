---
title: "EVE Online (Logdateien)"
nav_order: 20
lang: "de"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (Logdateien) {#eve-online-log-files}

Während du EVE Online spielst, liest der Watcher die Dateien, die das Spiel schreibt, und speichert, was passiert ist. So kannst du es später als Statistik und Zeitleiste ansehen.

*Technische Details: Adapter `eve`, Art [`log`](sources-and-rules.md); er läuft, solange `exefile.exe` läuft, und sucht alle 0,5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Schaden, den du und der andere Schiffe ausgeteilt und eingesteckt habt, mit Pilot, Korporationskürzel, Waffe und Trefferqualität
- Fehlschüsse, die du ausgeteilt und eingesteckt hast
- ausgezahlte Kopfgelder (NPC-Abschüsse) mit ISK
- Sprünge zwischen Systemen
- jede Zeile des Gamelogs und des Chatlogs, vollständig in heat.raw.parquet
- Schaden ausgeteilt und eingesteckt, Treffer, Fehlschüsse, Kopfgeld-Abschüsse und ISK, Sprünge

## Woher die Daten kommen {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt und die Chatlogs\\\*.txt daneben (jede Datei, die seit dem Start des Clients geschrieben wurde)

## So schaltest du es ein {#how-to-switch-it-on}

Du musst nichts einschalten: Der Watcher liest die Quelle so, wie das Spiel oder die Plattform sie bereitstellt.

## So funktioniert es {#how-it-works}

EVE Online: die Spielprotokolle des Clients, `Documents\EVE\logs\Gamelogs\*.txt`.

Der Client schreibt pro Charakter und pro Anmeldung eine Datei, `<jjjjmmtt>_<hhmmss>[_<Charakter-ID>].txt`; das Protokollieren in Dateien ist standardmäßig eingeschaltet. Mehrere Clients, die nebeneinander laufen, schreiben jeweils ihre eigene Datei, deshalb wird jede Datei verfolgt, die seit dem Start des Spiels geschrieben wurde. Kopf und Zeilen (die EVE-Zeit ist UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(Die Combat-Zeile steht in der Datei in einer einzigen Zeile.) Formatierungs-Tags werden vor dem Abgleich entfernt. Die Datei war über die Jahre sowohl UTF-8 als auch UTF-16; beide werden gelesen. Das Format ist von CCP nicht dokumentiert; es ist das Klartext-Protokoll des Clients, so gelesen, wie es auch Kampflog-Werkzeuge der Community lesen (z. B. <https://docs.rs/crate/eve-log-parser>). Keine Positionen.

Daneben liegt `Documents\EVE\logs\Chatlogs\<Kanal>_<jjjjmmtt>_<hhmmss>[_<ID>].txt`: eine Datei pro Chatkanal und Anmeldung (wenn das Chatprotokoll eingeschaltet ist, was der Standard des Clients ist), UTF-16, ein Kopf mit dem Namen des Kanals und des Listeners, dann `[ jjjj.mm.tt hh:mm:ss ] Absender > Nachricht`.

Jede Zeile beider Arten wird vollständig in der Roh-Beilage der Session gespeichert (Konverterregel von 3DHeat): eine Gamelog-Zeile unter ihrem Kanal in Klammern (`combat`, `notify`, `bounty`, `None`, ...), eine Chatzeile als `chat` mit ihrem Kanal, die Kopfzeilen als `gamelog header` bzw. `chatlog header`.

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | nein |
| Oben-Achse | `y` |
| Einheiten | keine Positionen aufgezeichnet |
| Für den Viewer gespiegelt | keine |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als „allowed (reads only what the game publishes)“.
- Art `log`: Es liest nur, was das Spiel oder die Plattform herausgibt (Dateien, die das Spiel während des Laufs schreibt). Deshalb zeichnet es auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob Speicher überhaupt gelesen werden darf.
- Speicher: Dieser Adapter liest **nie** den Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters beim Namen setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; „Was aufgezeichnet wird“ oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder gespeichert, nie weggelassen. Außer den Zeilen wird jedes Paket, jede Seite, jede Zeile und jede Antwort, die der Adapter bekommt, vollständig in der `heat.raw.parquet` der Session gespeichert (Spalten `time`, `ms`, `type`, `used`, `payload`, `text` und alle Felder, die nach Namen behalten werden; `used` markiert, was auch zu Zeilen wurde). `selfCheck.completeness` in `meta.json` zählt jeden `type`; `lost` ist 0.

**Gelesen**

- Gamelog-`(combat)`-Treffer, die du ausgeteilt und eingesteckt hast (Menge, anderer Pilot, Korporationskürzel, Schiff, Waffe, Trefferqualität), und Fehlschüsse in beide Richtungen
- Kopfgeld-Auszahlungen (`(bounty)`) mit ISK und die Zeilen `Jumping from A to B`
- der Listener aus dem Kopf des Gamelogs: wessen Protokoll es ist

**Roh gespeichert**

- jede Gamelog-Zeile vollständig, `type` = ihr Kanal in Klammern (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), mit `file` und `listener`; `used`, wo sie zu einer Zeile wurde; die Kopfzeilen als `gamelog header`
- jede Chatlog-Zeile vollständig (Local, Korporation, Flotte, private Kanäle und die Hinweise `EVE System`, etwa ein Wechsel des Local-Kanals beim Sprung), `type` `chat`, mit `channel`, `listener` und `file`; die Kopfzeilen als `chatlog header`. Noch nicht zu Zeilen gemacht
- die Formatierungs-Tags (`<color>`, `<b>`, `<font>`) bleiben im Rohtext; die Zeilen haben sie entfernt

**Nicht verfügbar**

- Positionen: Der Client schreibt keine in seine Protokolle
- Kämpfe anderer Piloten: Ein Gamelog gehört immer dem Listener
- Protokolle früherer Anmeldungen: Jede Anmeldung schreibt neue Dateien; die älter als dieser Lauf des Clients sind, werden nicht noch einmal gelesen
- Chat, wenn der Spieler das Chatprotokoll in den Einstellungen des Clients ausgeschaltet hat
- der Cache und die Einstellungsdateien des Clients: keine Protokolle, und nicht dokumentiert

**Größe**: Ein Gamelog ist 0,1–2 MB pro Stunde (meist im Kampf); Chatlogs hängen von den offenen Kanälen ab – ein stark besuchter Local- oder Flottenkanal 0,5–3 MB pro Stunde; zstd macht in heat.raw.parquet etwa ein Zehntel daraus

## Geprüft {#verified}

getestet mit synthetischen Gamelog-Zeilen im Format, das Community-Parser veröffentlichen; noch nicht gegen das Spiel getestet

## Quelle {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Aus dem Adapter erzeugt von tools/gen_game_pages.py; ändere den Adapter und führe das Skript erneut aus, statt diese Seite zu bearbeiten. -->
