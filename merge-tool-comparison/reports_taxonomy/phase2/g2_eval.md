# G2 machine evaluation — Phase-2 codebook draft (ISSUES #30, §7 G2 i-iii)

Draft: `reports_taxonomy/phase2/codebook_draft.md`  |  categories defined: 9 (8 named + residual-other)
Ground truth: 165 derivation units, 60 attributed.

## Condition (i) — coverage + firewall + completeness
- coverage rows: 60  |  attributed: 60  |  missing: 0  |  extra-non-attributed: 0  |  duplicates: 0
- firewall (all coverage ids in derivation set): OK
- residual: 0/60 = 0.0%  (ceiling 10%)
- category sizes: {"import-pruning-vs-concurrent-usage": 15, "stale-reference-to-removed-declaration": 9, "overlapping-edit-interleaving": 5, "stale-caller-of-changed-signature": 14, "stale-reference-to-renamed-or-relocated-declaration": 7, "insertion-anchored-to-relocated-code": 2, "changed-behavior-vs-stale-expectation": 5, "duplicate-concurrent-addition": 3}
- **(i) verdict: PASS**

## Condition (ii) — granularity audit
- categories with all required fields: 9/9
- anchors all derivation-only (firewall): OK
- named categories missing an anchor: none
- symptom/domain-named ids (heuristic): none
- note: 'every category is a mechanism (not a symptom)' is a semantic judgment for Ali's (iv) ruling; this pass checks structure + the symptom-token heuristic only.
- **(ii) verdict: PASS**

## Condition (iii) — old->new mapping + four-family
- historical categories present in mapping: 7/7
- four-family assessment written: yes
- **(iii) verdict: PASS**

## Machine verdict (i-iii)
**PASS** — all three machine conditions met; hand to Ali for the (iv) ruling via mapping_ui.html.

### Problems: none
