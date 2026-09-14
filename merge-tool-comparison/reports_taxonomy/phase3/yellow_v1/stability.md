# G3 Condition 1 — Phase-3 Stability (pass a vs pass b)

**Generated over all 275 scored census units** (protocol §7 G3.1 / §8). Primary label, escape hatches counted as labels. NEW labeled evaluation — never blended with Stage-C R1/R2 or Phase-2b.

- Exact primary-label agreement: **217/275 = 78.9%** (Wilson 95% CI [73.7, 83.3])
- Cohen's κ: **0.741**
- Disagreements: **58** (cap 60)
- Mean secondary-label Jaccard (descriptive): 0.909

## Gate

| criterion | threshold | value | pass |
|---|---|---|---|
| agreement | ≥ 80% | 78.9% | ❌ |
| Cohen's κ | ≥ 0.70 | 0.741 | ✅ |
| disagreements | ≤ 60 | 58 | ✅ |

**Verdict: YELLOW**  (60–80% or κ 0.50–0.70, or cap-only miss → STOP: one sanctioned codebook-clarification amendment, then rerun BOTH passes — propose + wait for Ali)

## Primary-label distributions

| category | pass a | pass b |
|---|--:|--:|
| `stale-usage-of-pruned-import` | 33 | 33 |
| `stale-reference-to-removed-declaration` | 7 | 7 |
| `stale-reference-to-renamed-or-relocated-declaration` | 19 | 17 |
| `stale-caller-of-changed-signature` | 29 | 29 |
| `stale-expectation-of-changed-behavior` | 7 | 10 |
| `overlapping-edit-interleaving` | 16 | 21 |
| `insertion-anchored-to-relocated-code` | 3 | 3 |
| `duplicate-concurrent-addition` | 6 | 6 |
| `residual-other` | 0 | 0 |
| `none-identified` | 81 | 76 |
| `indeterminate` | 73 | 70 |
| `flaky-suspect` | 1 | 3 |

## Disagreements (pass a → pass b)

58 of 275. Contents of held-out units are NOT quoted here (labels only, §4 firewall).

| merge_id | split | stratum | pass a | pass b | a conf | b conf |
|---|---|---|---|---|---|---|
| `javaparser_javaparser__e6063bb10d` | heldout | B | `duplicate-concurrent-addition` | `overlapping-edit-interleaving` | medium | medium |
| `mashape_unirest-java__b43fb95f4a` | derivation | A | `indeterminate` | `flaky-suspect` | medium | medium |
| `apache_commons-collections__f0c2e97529` | derivation | B | `indeterminate` | `none-identified` | medium | medium |
| `cloudfoundry_cf-java-client__a69078adc8` | derivation | A | `indeterminate` | `none-identified` | medium | medium |
| `cloudfoundry_cf-java-client__be097d5860` | derivation | A | `indeterminate` | `none-identified` | medium | medium |
| `fasterxml_jackson-datatype-joda__4e6c266339` | heldout | A | `indeterminate` | `none-identified` | medium | medium |
| `google_compile-testing__608e1cb92a` | heldout | A | `indeterminate` | `none-identified` | medium | high |
| `iryndin_jdbf__9853124d73` | derivation | A | `indeterminate` | `none-identified` | medium | high |
| `jenkinsci_coverity-plugin__2fb8690816` | heldout | A | `indeterminate` | `none-identified` | medium | medium |
| `jenkinsci_docker-build-publish-plugin__59faa9673c` | derivation | A | `indeterminate` | `none-identified` | medium | high |
| `joel-costigliola_assertj-core__d3dab0d22c` | heldout | B | `indeterminate` | `none-identified` | medium | medium |
| `mercadopago_sdk-java__b7498c6f9d` | derivation | A | `indeterminate` | `none-identified` | high | high |
| `onebusaway_onebusaway-application-modules__915e2f3ffe` | derivation | A | `indeterminate` | `none-identified` | medium | medium |
| `oxo42_stateless4j__4c7880ec0e` | derivation | B | `indeterminate` | `none-identified` | medium | medium |
| `prism_prism-bukkit__6dfb9ef0cf` | heldout | A | `indeterminate` | `none-identified` | medium | medium |
| `projectblueshift_blueshiftapi__004679e5bb` | derivation | A | `indeterminate` | `none-identified` | medium | high |
| `relayrides_pushy__6badde9538` | derivation | A | `indeterminate` | `none-identified` | medium | medium |
| `spigotmc_bungeecord__96db0c71b8` | heldout | B | `indeterminate` | `none-identified` | medium | medium |
| `zxing_zxing__26d5d13836` | heldout | B | `indeterminate` | `none-identified` | medium | medium |
| `jenkinsci_junit-plugin__cfcac8f0c9` | heldout | B | `indeterminate` | `overlapping-edit-interleaving` | medium | medium |
| `jwtk_jjwt__fd52e0ffc2` | heldout | B | `indeterminate` | `overlapping-edit-interleaving` | medium | medium |
| `datastax_java-driver__7ff4958746` | heldout | A | `indeterminate` | `stale-caller-of-changed-signature` | medium | medium |
| `apache_shiro__13806fc623` | heldout | A | `indeterminate` | `stale-expectation-of-changed-behavior` | medium | low |
| `danielnorberg_auto-matter__3d46ebaf5a` | derivation | B | `indeterminate` | `stale-expectation-of-changed-behavior` | medium | medium |
| `frankbille_scoreboard__890ecd0bdb` | heldout | A | `indeterminate` | `stale-expectation-of-changed-behavior` | medium | medium |
| `javaparser_javaparser__ff91564b7f` | derivation | A | `indeterminate` | `stale-expectation-of-changed-behavior` | medium | medium |
| `mbosecke_pebble__bb807558a3` | heldout | B | `indeterminate` | `stale-usage-of-pruned-import` | medium | medium |
| `jline_jline2__348cb9dada` | derivation | A | `none-identified` | `duplicate-concurrent-addition` | medium | high |
| `swagger-api_swagger-parser__41ccee4da3` | derivation | A | `none-identified` | `flaky-suspect` | medium | medium |
| `apache_olingo-odata4__820b462f49` | derivation | A | `none-identified` | `indeterminate` | medium | medium |
| `apache_roller__1628c3a3c4` | heldout | B | `none-identified` | `indeterminate` | medium | medium |
| `buddycloud_buddycloud-server-java__33ec3ec7cd` | heldout | A | `none-identified` | `indeterminate` | medium | medium |
| `cloudslang_score__ded24a7b98` | derivation | B | `none-identified` | `indeterminate` | medium | medium |
| `dabsquared_gitlab-plugin__d555b8773d` | heldout | A | `none-identified` | `indeterminate` | medium | medium |
| `fasterxml_jackson-core__2572819ed9` | heldout | A | `none-identified` | `indeterminate` | high | high |
| `jenkinsci_jira-plugin__6ad78581c9` | heldout | A | `none-identified` | `indeterminate` | medium | medium |
| `joel-costigliola_assertj-core__d04568906e` | heldout | B | `none-identified` | `indeterminate` | high | high |
| `jparsec_jparsec__ef02642abd` | heldout | A | `none-identified` | `indeterminate` | medium | medium |
| `jwtk_jjwt__ff932e9838` | derivation | A | `none-identified` | `indeterminate` | high | medium |
| `masterthought_cucumber-reporting__d1ecdc4a98` | derivation | B | `none-identified` | `indeterminate` | medium | medium |
| `ninjaframework_ninja__663883c228` | derivation | A | `none-identified` | `indeterminate` | high | medium |
| `openpnp_openpnp__fb30708fe0` | heldout | A | `none-identified` | `indeterminate` | medium | medium |
| `sonarcommunity_sonar-scm-activity__e078d44db1` | derivation | B | `none-identified` | `indeterminate` | medium | medium |
| `steveice10_mcprotocollib__5c8a435832` | derivation | A | `none-identified` | `indeterminate` | medium | medium |
| `structr_structr__6738b144bb` | derivation | B | `none-identified` | `indeterminate` | medium | medium |
| `tridentsdk_tridentsdk__004679e5bb` | heldout | A | `none-identified` | `indeterminate` | high | medium |
| `vijay2win_flume-cassandra-sink__38cdbeced7` | derivation | B | `none-identified` | `indeterminate` | medium | medium |
| `spigotmc_bungeecord__8943fe2bd2` | derivation | B | `none-identified` | `overlapping-edit-interleaving` | medium | medium |
| `urbanairship_datacube__b8bef94f4d` | derivation | A | `none-identified` | `overlapping-edit-interleaving` | medium | medium |
| `jenkinsci_credentials-plugin__e9cf377a17` | derivation | B | `none-identified` | `stale-usage-of-pruned-import` | medium | high |
| `apache_opennlp__8240a2c660` | derivation | B | `overlapping-edit-interleaving` | `none-identified` | medium | medium |
| `javaparser_javaparser__6a08db8f51` | derivation | B | `stale-caller-of-changed-signature` | `indeterminate` | low | low |
| `apache_cayenne__f10ba77a97` | derivation | B | `stale-expectation-of-changed-behavior` | `indeterminate` | medium | medium |
| `vkostyukov_la4j__d216aa8928` | derivation | A | `stale-expectation-of-changed-behavior` | `indeterminate` | medium | medium |
| `jsprit_jsprit__c60ab8afd0` | heldout | B | `stale-reference-to-renamed-or-relocated-declaration` | `indeterminate` | medium | medium |
| `urbanairship_datacube__641b92c0fc` | heldout | B | `stale-reference-to-renamed-or-relocated-declaration` | `overlapping-edit-interleaving` | medium | high |
| `jmrozanec_cron-utils__a77c0476c3` | derivation | B | `stale-usage-of-pruned-import` | `indeterminate` | high | medium |
| `sander2798_enderstone__9d0d7b7ba8` | derivation | B | `stale-usage-of-pruned-import` | `stale-expectation-of-changed-behavior` | high | medium |

## Off-diagonal confusion (pass a row → pass b col; nonzero only)

- `stale-usage-of-pruned-import` → `indeterminate`×1, `stale-expectation-of-changed-behavior`×1
- `stale-reference-to-renamed-or-relocated-declaration` → `indeterminate`×1, `overlapping-edit-interleaving`×1
- `stale-caller-of-changed-signature` → `indeterminate`×1
- `stale-expectation-of-changed-behavior` → `indeterminate`×2
- `overlapping-edit-interleaving` → `none-identified`×1
- `duplicate-concurrent-addition` → `overlapping-edit-interleaving`×1
- `none-identified` → `indeterminate`×18, `overlapping-edit-interleaving`×2, `stale-usage-of-pruned-import`×1, `duplicate-concurrent-addition`×1, `flaky-suspect`×1
- `indeterminate` → `none-identified`×17, `stale-expectation-of-changed-behavior`×4, `overlapping-edit-interleaving`×2, `stale-caller-of-changed-signature`×1, `flaky-suspect`×1, `stale-usage-of-pruned-import`×1
