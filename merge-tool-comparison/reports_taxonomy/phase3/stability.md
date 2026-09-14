# G3 Condition 1 — Phase-3 Stability (pass a vs pass b)

**Generated over all 275 scored census units** (protocol §7 G3.1 / §8). Primary label, escape hatches counted as labels. NEW labeled evaluation — never blended with Stage-C R1/R2 or Phase-2b.

- Exact primary-label agreement: **228/275 = 82.9%** (Wilson 95% CI [78.0, 86.9])
- Cohen's κ: **0.788**
- Disagreements: **47** (cap 60)
- Mean secondary-label Jaccard (descriptive): 0.942

## Gate

| criterion | threshold | value | pass |
|---|---|---|---|
| agreement | ≥ 80% | 82.9% | ✅ |
| Cohen's κ | ≥ 0.70 | 0.788 | ✅ |
| disagreements | ≤ 60 | 47 | ✅ |

**Verdict: PASS**  (→ proceed to G3 condition 2, Ali reliability adjudication)

## Primary-label distributions

| category | pass a | pass b |
|---|--:|--:|
| `stale-usage-of-pruned-import` | 29 | 33 |
| `stale-reference-to-removed-declaration` | 5 | 6 |
| `stale-reference-to-renamed-or-relocated-declaration` | 16 | 17 |
| `stale-caller-of-changed-signature` | 27 | 28 |
| `stale-expectation-of-changed-behavior` | 7 | 9 |
| `overlapping-edit-interleaving` | 21 | 18 |
| `insertion-anchored-to-relocated-code` | 3 | 3 |
| `duplicate-concurrent-addition` | 6 | 6 |
| `residual-other` | 0 | 0 |
| `none-identified` | 89 | 84 |
| `indeterminate` | 69 | 68 |
| `flaky-suspect` | 3 | 3 |

## Disagreements (pass a → pass b)

47 of 275. Contents of held-out units are NOT quoted here (labels only, §4 firewall).

| merge_id | split | stratum | pass a | pass b | a conf | b conf |
|---|---|---|---|---|---|---|
| `fasterxml_jackson-datatype-joda__4e6c266339` | heldout | A | `flaky-suspect` | `none-identified` | medium | high |
| `apache_directory-kerby__798f1b4348` | derivation | B | `indeterminate` | `none-identified` | medium | medium |
| `apache_roller__1628c3a3c4` | heldout | B | `indeterminate` | `none-identified` | medium | medium |
| `flaxsearch_luwak__7956093330` | heldout | B | `indeterminate` | `none-identified` | medium | high |
| `mbosecke_pebble__4466be45d7` | heldout | B | `indeterminate` | `none-identified` | medium | medium |
| `spigotmc_bungeecord__96db0c71b8` | heldout | B | `indeterminate` | `none-identified` | medium | medium |
| `steveice10_mcprotocollib__5c8a435832` | derivation | A | `indeterminate` | `none-identified` | medium | medium |
| `structr_structr__6738b144bb` | derivation | B | `indeterminate` | `none-identified` | medium | medium |
| `wordnik_swagger-codegen__dbadd9a831` | heldout | B | `indeterminate` | `none-identified` | medium | high |
| `flaxsearch_luwak__666bdd192e` | heldout | B | `indeterminate` | `stale-caller-of-changed-signature` | medium | high |
| `apache_shiro__13806fc623` | heldout | A | `indeterminate` | `stale-expectation-of-changed-behavior` | medium | medium |
| `vkostyukov_la4j__d216aa8928` | derivation | A | `indeterminate` | `stale-expectation-of-changed-behavior` | medium | medium |
| `clojure_clojure__77342d2e35` | heldout | A | `indeterminate` | `stale-reference-to-renamed-or-relocated-declaration` | medium | medium |
| `jsprit_jsprit__c60ab8afd0` | heldout | B | `indeterminate` | `stale-reference-to-renamed-or-relocated-declaration` | medium | medium |
| `xebia_xebium__a82603c978` | derivation | A | `indeterminate` | `stale-reference-to-renamed-or-relocated-declaration` | medium | medium |
| `jenkinsci_build-timeout-plugin__daeab4a1ee` | derivation | B | `indeterminate` | `stale-usage-of-pruned-import` | low | medium |
| `jenkinsci_credentials-plugin__e9cf377a17` | derivation | B | `indeterminate` | `stale-usage-of-pruned-import` | medium | high |
| `mbosecke_pebble__bb807558a3` | heldout | B | `indeterminate` | `stale-usage-of-pruned-import` | medium | medium |
| `steveice10_mcprotocollib__8a7d7b196b` | heldout | B | `indeterminate` | `stale-usage-of-pruned-import` | medium | high |
| `swagger-api_swagger-parser__41ccee4da3` | derivation | A | `none-identified` | `flaky-suspect` | high | medium |
| `apache_olingo-odata4__820b462f49` | derivation | A | `none-identified` | `indeterminate` | high | medium |
| `buschmais_extended-objects__46ec306cf6` | heldout | A | `none-identified` | `indeterminate` | medium | medium |
| `glowroot_glowroot__5edc6961f8` | derivation | B | `none-identified` | `indeterminate` | medium | medium |
| `imixs_imixs-workflow__d370e1aa34` | derivation | B | `none-identified` | `indeterminate` | medium | low |
| `jcabi_jcabi-github__fccaac2ed7` | heldout | B | `none-identified` | `indeterminate` | medium | medium |
| `jenkinsci_docker-build-publish-plugin__59faa9673c` | derivation | A | `none-identified` | `indeterminate` | medium | medium |
| `jenkinsci_junit-plugin__cfcac8f0c9` | heldout | B | `none-identified` | `indeterminate` | medium | medium |
| `jparsec_jparsec__ef02642abd` | heldout | A | `none-identified` | `indeterminate` | medium | low |
| `mbosecke_pebble__e1d07bf277` | derivation | B | `none-identified` | `indeterminate` | medium | medium |
| `ninjaframework_ninja__663883c228` | derivation | A | `none-identified` | `indeterminate` | medium | medium |
| `skyscreamer_nevado__cdc23cde46` | heldout | A | `none-identified` | `indeterminate` | medium | medium |
| `vkostyukov_la4j__843d8ff9de` | derivation | B | `none-identified` | `indeterminate` | medium | medium |
| `zxing_zxing__26d5d13836` | heldout | B | `none-identified` | `indeterminate` | medium | medium |
| `apache_opennlp__8240a2c660` | derivation | B | `none-identified` | `overlapping-edit-interleaving` | medium | high |
| `softinstigate_restheart__dc14776b02` | derivation | B | `none-identified` | `stale-usage-of-pruned-import` | medium | high |
| `frankbille_scoreboard__890ecd0bdb` | heldout | A | `overlapping-edit-interleaving` | `indeterminate` | medium | medium |
| `spigotmc_bungeecord__8943fe2bd2` | derivation | B | `overlapping-edit-interleaving` | `none-identified` | medium | medium |
| `cloudfoundry_cf-java-client__b0add1ef2a` | derivation | A | `overlapping-edit-interleaving` | `stale-caller-of-changed-signature` | high | high |
| `jdeparser_jdeparser2__868afefbb4` | derivation | B | `overlapping-edit-interleaving` | `stale-reference-to-removed-declaration` | medium | medium |
| `ardesco_selenium-standalone-server-plugin__957d978135` | derivation | B | `stale-caller-of-changed-signature` | `stale-usage-of-pruned-import` | high | high |
| `sandergielisse_enderstone__9d0d7b7ba8` | heldout | B | `stale-expectation-of-changed-behavior` | `stale-usage-of-pruned-import` | high | medium |
| `bguerout_jongo__3aaaf0e4c7` | derivation | A | `stale-reference-to-removed-declaration` | `indeterminate` | medium | low |
| `qcadoo_mes__c6cb8180e5` | derivation | B | `stale-reference-to-renamed-or-relocated-declaration` | `indeterminate` | medium | medium |
| `gwtbootstrap3_gwtbootstrap3__5c0d1eab79` | derivation | A | `stale-reference-to-renamed-or-relocated-declaration` | `stale-reference-to-removed-declaration` | medium | high |
| `cternes_openkeepass__bb53512ab2` | derivation | A | `stale-usage-of-pruned-import` | `indeterminate` | medium | medium |
| `square_javapoet__d019b6f624` | derivation | A | `stale-usage-of-pruned-import` | `none-identified` | medium | medium |
| `sander2798_enderstone__9d0d7b7ba8` | derivation | B | `stale-usage-of-pruned-import` | `stale-expectation-of-changed-behavior` | high | medium |

## Off-diagonal confusion (pass a row → pass b col; nonzero only)

- `stale-usage-of-pruned-import` → `indeterminate`×1, `stale-expectation-of-changed-behavior`×1, `none-identified`×1
- `stale-reference-to-removed-declaration` → `indeterminate`×1
- `stale-reference-to-renamed-or-relocated-declaration` → `stale-reference-to-removed-declaration`×1, `indeterminate`×1
- `stale-caller-of-changed-signature` → `stale-usage-of-pruned-import`×1
- `stale-expectation-of-changed-behavior` → `stale-usage-of-pruned-import`×1
- `overlapping-edit-interleaving` → `stale-caller-of-changed-signature`×1, `indeterminate`×1, `stale-reference-to-removed-declaration`×1, `none-identified`×1
- `none-identified` → `indeterminate`×13, `overlapping-edit-interleaving`×1, `stale-usage-of-pruned-import`×1, `flaky-suspect`×1
- `indeterminate` → `none-identified`×8, `stale-usage-of-pruned-import`×4, `stale-reference-to-renamed-or-relocated-declaration`×3, `stale-expectation-of-changed-behavior`×2, `stale-caller-of-changed-signature`×1
- `flaky-suspect` → `none-identified`×1
