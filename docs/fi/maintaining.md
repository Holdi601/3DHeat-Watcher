---
title: Sivujen ylläpito
nav_order: 15
lang: "fi"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Sivujen ylläpito {#maintaining-these-pages}

Tarkistuslista jokaista julkaisua varten. Sivujen on kerrottava, mitä koodi tekee, ne on luettava hyvin aloittelijalle, 8-vuotiaalle ja ammattilaiselle, ja ne on oltava olemassa jokaisella kielellä, jota 3DHeat-katselin tukee.

## Julkaisun tarkistuslista {#release-checklist}

1. **Luo generoidut sivut uudelleen koodista:**

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Ennen commitointia saman komennon kanssa `--check` on palautettava koodi 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Vertaa muutoksia edelliseen julkaisuun.** `VERSION` sisältää version; sen tagi on `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Jokainen uusi komento, valitsin, sarake, tuloste tai toiminta saa rivin sitä käsittelevälle sivulle, ja rivin `CHANGELOG.md`-tiedostoon kohtaan **Docs**, jossa mainitaan sivu.

3. **Riippumaton tarkistus.** Joku, joka ei kirjoittanut muutosta, lukee muutetut sivut kolmesti: aloittelijana (ei ole koskaan käyttänyt päätettä), 8-vuotiaana (sanooko ensimmäinen kappale, mitä se on ja miksi, selkein sanoin?) ja ammattilaisena (ovatko liput, oletukset ja sarakkeet täsmälleen sitä, mitä koodi tekee?). Kaaviot ja kuvat mukaan lukien.

4. **Korjaa, mitä tarkistus löysi.** Kuvat pysyvät noin 900 px leveinä, ja teksti on vähintään 12 px kuten näkyy. Kaaviot luodaan tiedostoista `tools/diagrams/*.json` työkalulla `tools/flow2svg.py`. Esimerkit käyttävät vain keksittyjä nimiä (`de_x`, "Demo Valley", `<map>`): ei koskaan oikeaa karttaa, pelaajaa, ottelun tunnusta tai hahmoa oikeista tiedostoista.

5. **Käännökset.** Jokainen käännetty sivu tallentaa sen englanninkielisen lähdesivun tiivisteen, josta se tehtiin. Käännä uudelleen ne sivut, joiden englanninkielisen lähteen tiiviste on muuttunut, ja anna jokaisen kielen tarkistaa samalla tavalla kolmella tavalla (selkeä, aloittelija, ammattilainen), kaavion nimiöt mukaan lukien.

6. **Työnnä vain omistajan luvalla.** Tee commit paikallisesti; omistaja päättää, milloin se julkistetaan.

## Käännökset: komennot {#translations-the-commands}

Sivusto on käännetty 3DHeat-katselimen 40 kielelle: englanti on kansiossa `docs/`, ja jokainen muu kieli kansiossa `docs/<lang>/` samoilla tiedostonimillä. `tools/docs_i18n.py` hoitaa kirjanpidon:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Käännä vain se, minkä `todo` listaa: säilytä Markdown, linkit, koodi sekä tiedosto- ja sarakenimet sellaisinaan. Käännä otsikot ja kuvien kuvaukset, ja käytä 3DHeat-katselimen omia sanoja sen painikkeista ja paneeleista (sen `src/i18n/locales/<lang>/`-kansiosta). Generoidut viitesivut ja pääteikkunakuvat pysyvät englanniksi. Sivustolla vanhentunut käännös sanoo niin ja linkittää englanninkieliseen sivuun. Puuttuva käännös palautuu englantiin. Kielivalikon ja etusivun selaimen kielen mukaisen uudelleenohjauksen ottavat osiot kansiosta `docs/_includes/`.
