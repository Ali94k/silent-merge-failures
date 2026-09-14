# Stage γ — Diagnostic FP inspection

**Status:** done (2026-05-14); Mastery extension (2026-05-14); M3.5 empirical follow-up (§8, 2026-05-14)
**Defined in:** [`execution-sequence.md §2.γ`](execution-sequence.md)
**Resolves:** open-question #1 in [`execution-sequence.md §5`](execution-sequence.md) (sample stratification); diagnostic input to [`mergiraf-integration.md §Phase 3`](mergiraf-integration.md) (M3 option choice); [`ISSUES.md` #2](../../merge-tool-comparison/ISSUES.md) status moves `open → decided`.

**Honesty note (2026-05-14, post-review):** the qualitative finding rests on 3 of 39 eyeballed `structural` cases — the remaining 36 are unsampled. Treat "all structural FPs are AST-equivalent reformatting" as a hypothesis backed by 3 confirmed instances, not a measured property of the full bucket. The 3e recommendation is *contingent on M3.5 empirically verifying that `google-java-format` actually normalises the differences observed in the sample*; it has not been run yet against these scenarios. See §7.

**M3.5 outcome (2026-05-14, post-implementation):** the hypothesis did not hold across the full bucket. Running the comparator with `google-java-format` 1.22.0 roundtrip on the n=50 dataset recovered **1** of 42 Spork FPs and **0** of 44 Mastery FPs. The 3 small-sample inspections were not representative — most unsampled residuals contain `else { if (X) }` ↔ `else if (X)` restructuring and comment-placement differences that the formatter preserves rather than normalises. See §8 for the empirical breakdown and follow-up direction.

---

## 1. Method

Programmatically classified every Spork-claims-CLEAN scenario whose normalized output differs from the developer resolution (i.e., every FP under the current comparator). For each FP, applied progressively-stricter normalizations to bucket the kind of difference:

1. **Baseline normalize** — current `normalize_content()`: rstrip lines, LF endings, drop trailing blanks.
2. **Aggressive whitespace** — collapse all runs of whitespace (incl. newlines) to a single space.
3. **Strip imports** — `re.sub(r"^\s*import\s+[^;]+;\s*$", "", content, flags=re.MULTILINE)`.
4. **Imports + whitespace** — both.

Bucketed each FP by the cheapest normalization that produced a match (or `structural` if none did). Then size-stratified (smallest / median / largest by merged-content length) and eyeballed the three diffs to interpret what the `structural` bucket actually contains.

Stratification choice resolves open-question #1: arbitrary 3-scenario selection would have over-weighted whatever the random sample caught. Size-stratification ensures the sample covers Spork's behavior across input sizes without manual selection bias.

## 2. Quantitative results

42 Spork FPs total. Distribution:

| Bucket | Count | What it means |
|---|---:|---|
| `whitespace_only` | 1 | Differs only in whitespace runs |
| `imports_plus_whitespace` | 2 | Imports reordered + whitespace |
| `structural` | 39 | Token-level differences that survive whitespace + import normalization |

## 3. Qualitative results — three eyeballed diffs

All three size-stratified inspections produced only AST-equivalent reformatting:

**Small** — `aerogear_aerogear-crypto-java__…AeroGearCrypto.java` (2.7 KB):
- Import group reorder.
- `(Provider) Class.forName(…).newInstance()` → `((Provider) (Class.forName(…).newInstance()))` (extra parens around cast).
- `InstantiationException` → `java.lang.InstantiationException` (FQN expansion for auto-imported `java.lang.*`).
- `else { if (X) { … } }` → `else if (X) { … }` (flattened nested if).
- Comment duplication: `//PBKDF2` appears twice; `//AES` appears twice.
- Blank lines inserted between field declarations.

**Medium** — `aerospike_aerospike-client-java__…PartitionTracker.java` (18 KB):
- Import group reordering (`java.*` moved after `com.aerospike.*`).
- `(Policy)policy` → `((Policy) (policy))` extra parens.
- Blank line inserted between every field declaration.

**Large** — `accla_d4m_api_java__…Graphulo.java` (150 KB):
- Imports reshuffled within groups.
- Multi-line method signatures collapsed onto a single line, with inline `// comment` interspersed.
- Bare-statement `if (X) throw Y;` → braced `if (X) { throw Y; }`.
- Redundant parens around boolean subexpressions: `(ATtable == null) || …` vs `ATtable == null || …`.

**None of the inspected diffs reflect a semantic disagreement.** Every change is something Spork's AST pretty-printer does that survives the current `normalize_content()` because that function handles only whitespace and line endings.

## 4. Interpretation

The `structural` bucket isn't "Spork is wrong" — it's "Spork's textual output differs from the developer's, in ways that are AST-equivalent." The current comparator can't distinguish those two cases. The 42 FP / 44 FP (Mastery) headline numbers are largely a comparator measurement artefact — exactly the failure mode [`ISSUES.md` #2](../../merge-tool-comparison/ISSUES.md) suspected.

**Caveat — possible residual real-FP cases:** the comment-duplication observed in `aerogear` (`//PBKDF2`, `//AES` each appearing twice) is *not* a pretty-printing artefact; it would survive a formatter roundtrip because formatters preserve content. That suggests a small fraction (0–5 of the 39 structural cases) may be genuine Spork pathologies (e.g., the AST merger duplicating sibling nodes from base+ours+theirs). The sample of 3 is too small to estimate the residual fraction; a stage-γ extension or stage-3j (manual labelling) would close that gap if needed.

## 5. M3 recommendation

Per the richer [mergiraf-integration.md §Phase 3](mergiraf-integration.md) option taxonomy (not just the 3a/3b binary in `execution-sequence.md §2.γ`):

**Primary:** option **3e** (formatter-based normalisation via `google-java-format` roundtrip). Mapping to the 3 inspected diffs:

| Observed difference | 3e (`google-java-format`) handles it? |
|---|:---:|
| Import reordering | ✅ |
| Whitespace / blank-line insertion | ✅ |
| Redundant parens around casts | ✅ |
| FQN expansion (`java.lang.X` ↔ `X`) | ⚠️ — formatter doesn't qualify/unqualify identifiers; would need a separate pass |
| Brace style (`if (X) Y;` ↔ `if (X) { Y; }`) | ✅ |
| Method-signature line breaks | ✅ |
| Boolean-expression parens | ✅ |
| Comment duplication | ❌ — genuine residual; likely real Spork pathology |

**Add on top:** option **3i** (cite upstream Mergiraf numbers — free credibility for the Mergiraf row, captured at M0); option **3h** (multi-criteria reporting — show FP rate under each criterion; reader picks). Both compatible with 3e as primary.

**Defer:** option **3a** (test-suite ground truth). The diagnostic does not justify the 1–5d build-infra investment when 3e likely recovers ≥90% of the FPs.

**Validation step:** option **3j** (manual labelling) on the residual after 3e is applied. If > ~10% of FPs remain unexplained, upgrade to 3b (AST normalize) or escalate to 3a; if not, the 3e + 3j combination is the deliverable.

## 6. Mastery extension (2026-05-14)

The original γ scope covered Spork only. Running the same bucketing on Mastery's 44 FPs reveals a **qualitatively different** failure mode — Mastery's FPs are largely not AST-formatter artefacts, they are content-loss tool bugs:

| Bucket | Spork | Mastery |
|---|---:|---:|
| `whitespace_only` | 1 | **0** |
| `imports_plus_whitespace` | 2 | **0** |
| `structural` | 39 | **44** |

Size-stratified eyeball of three Mastery `structural` cases:

| Label | Scenario | Merged size | Dev size | What's missing |
|---|---|---:|---:|---|
| SMALL | `adoptopenjdk_mjprof…BasePlugin.java` | 71 chars | 793 chars | The entire GPL **license header** comment (~720 chars). Mastery emitted just `package + public interface BasePlugin {}` with no comments. |
| MEDIUM | `ahmetaa_zemberek-nlp…PostProcessedNE.java` | 10743 chars | 15442 chars | The class-level **Javadoc** (`/** Post processes named entities… */`) and many inline blank lines / comments. ~4700 chars of comments + whitespace dropped. |
| LARGE | `accla_d4m_api_java…Graphulo.java` | 104656 chars | 150806 chars | Same pattern — comments and blank lines aggressively pruned. ~46KB of content dropped. |

**Interpretation:** Mastery (Murmur-tree AST merger) discards comments and blank-line structure during its AST roundtrip. This is the same characteristic Schesch et al. cite as the reason JDime is "unsuitable for practical use" ("discards comments, discards file headers, and arbitrarily reorders methods and fields"). Mastery and JDime share the family weakness.

**Consequence for the M3 plan:**
- 3e (`google-java-format`) is **not the right primary fix for Mastery's FPs.** A formatter roundtrip can normalise *both* sides, but if one side (Mastery's output) is *missing the content entirely*, no amount of canonical formatting will recover the textual equivalence. The dev-vs-mastery diffs are content diffs, not format diffs.
- The right framing is: **Mastery's FPs are partly intrinsic** (like JDime's crashes — a known tool characteristic, not a measurement bug). 3e will reduce the FP rate somewhat (any whitespace/format component drops out) but the bulk remains.
- This **narrows the universe** where 3e is the headline fix to Spork specifically. The pre-extension γ summary was too generous to Mastery.

**Recommendation update:**
- For **Spork**: 3e + 3j on residual + 3i + 3h additively (unchanged).
- For **Mastery**: report 3i-style "intrinsic limitation" caveat alongside Mastery's FP rate (parallels the JDime treatment). 3e still useful (reduces FP rate by the whitespace/format share — likely a few percent) but no longer the headline.
- For **JDime**: unchanged — crashes happen before the comparator runs; 3e doesn't apply.

## 8. M3.5 empirical outcome (2026-05-14)

Comparator now invokes a `google-java-format` 1.22.0 Docker roundtrip when whitespace-normalisation reports a mismatch (`src/evaluation/comparator.py::contents_match`). Re-ran `merge-compare report` against the n=50 results cache.

### Spork — bucketing of 43 CLEAN outcomes

| Bucket | Count | Meaning |
|---|---:|---|
| `base_match` | 1 | Already a TP under whitespace normalize (`spork.TP` pre-3e) |
| `format_match` | 1 | 3e recovered: formatter roundtrip produced equal text |
| `parse_fail` | 2 | Formatter rejected one or both inputs (rc!=0) |
| `still_differ` | 39 | Formatter ran on both but text still differs after roundtrip |

Headline shift: Spork TP 1→2, FP 42→41. Net 3e recovery: **1 FP**.

### Mastery — bucketing of 44 CLEAN outcomes

| Bucket | Count |
|---|---:|
| `still_differ` | 44 |

Headline shift: Mastery TP 0→0, FP 44→44. Net 3e recovery: **0 FPs**. Matches §6's prediction (intrinsic content loss — comments and headers dropped before formatter ever runs; no amount of canonical formatting can rebuild missing content).

### Why so few Spork FPs recovered — categorisation of residuals

Diff-line categorisation across all 39 `still_differ` residuals after formatter roundtrip:

| Residual line category | Count |
|---|---:|
| `other` (structural / comment-placement / etc.) | 48,280 |
| `blank_line` | 774 |
| `fqn_javalang` (`java.lang.X` ↔ `X`) | 20 |

The `other` bucket dominates by three orders of magnitude. Eyeballed diff on `47deg_firebrand…HectorPersistenceFactory.java` shows the dominant residual patterns the formatter preserves rather than normalises:

- **`} else { if (X) {…} }` ↔ `} else if (X) {…}` restructuring.** Token-different, AST-different (extra block scope on Spork's side), control-flow-equivalent only modulo absence of variable shadowing. The formatter cannot rewrite this — it is a Spork pretty-printer choice that produces a distinct (but semantically equivalent) AST.
- **Comment placement.** Standalone line comments above `if` statements ↔ trailing comments after the opening `{`. The formatter places comments where they are in the source; if Spork and the developer placed the same comment in different syntactic positions, both formatted outputs preserve the divergence.
- **Cast spelling.** `((Long) (value))` ↔ `(Long) value`. The formatter does NOT aggressively strip redundant parens, contrary to the §5 prediction. Spork's double-paren style survives both sides' roundtrip.

These patterns were unrepresented in the 3-sample stratified inspection of §3. The hypothesis "all 39 unsampled structural FPs follow the small-sample reformatting pattern" was wrong — the structural bucket is heterogeneous.

### What this means for the M3 plan

- **3e implementation is correct** — does what it advertises, formats both sides through `google-java-format`. The 1-FP recovery is genuine. No bug to fix.
- **The §5 recommendation was over-confident** — based on prior knowledge of `google-java-format`'s behavior, not the actual diffs. The contingency hedge in §5 ("if 3e doesn't recover the Spork FPs in practice, upgrade to 3b or 3d") has fired.
- **Next-step direction.** Per the §5 fallback ladder: token-level (3d) would recover even less than 3e for these residuals (else-if restructuring is also token-different). AST-aware normalize (3b — javalang/tree-sitter canonicalisation, optionally collapsing redundant blocks) is the next defensible step. Manual labelling (3j) of a stratified sample of the 39 `still_differ` Spork residuals would also re-test the AST-equivalence assumption directly — and if many turn out to be genuine Spork pathologies (not just formatter-erasable cosmetics), the framing shifts toward "Spork's FP rate is partly intrinsic" parallel to Mastery's §6 framing.
- **`ISSUES.md` #2 stays at `decided`** — not resolved. The headline FP rates remain `presentation-suspect`, with the new empirical breakdown alongside.

## 9. Option 3j — stratified manual labelling (2026-05-14)

Re-test the §3 "all 39 unsampled structural FPs are AST-equivalent reformatting" hypothesis at higher sample size, after §8 falsified the 3-sample naive generalisation. Goal: determine whether the 39 still-differ Spork residuals are dominantly AST-equivalent (→ 3b would recover them) or dominantly intrinsic tool pathology (→ reframe like Mastery §6 / JDime).

### Method

15-sample stratified eyeball across the 39 still-differ Spork CLEAN outputs. Size-binned (5 quintiles by merged-file size), 3 picks per quintile (low/mid/high index within bin). Range: 2.6KB → 161KB formatted. For each scenario: classify the post-format diff by dominant pattern, count hunks and `+`/`-` lines, eyeball largest hunk plus a sample of mid-file hunks for the heavy-diff cases.

### Per-scenario classification

| idx | scenario (truncated) | size (KB) | hunks | `+/-` | dominant pattern |
|---:|---|---:|---:|---:|---|
| 0 | `aerospike … proxy` | 2.6 | 7 | 12 | blank-line + comment placement |
| 3 | `zemberek-nlp … embedding` | 3.4 | 15 | 20 | blank-line dominant |
| 6 | `adangel pmd` | 4.9 | 3 | 23 | comment placement |
| 7 | `addthis stream-lib Murmur` | 5.4 | 2 | 29 | cast paren style + local structural |
| 11 | `ab0oo APRSPacket` | 7.1 | 17 | 33 | mixed: blank + else-block + paren |
| 14 | `addthis stream-lib (db2ede7429)` | 8.1 | 18 | 32 | blank-line + cast-paren |
| 15 | `adoptopenjdk mjprof SFN` | 8.3 | 4 | 5 | tiny: blank-line + minor structural |
| 19 | `zemberek-nlp ner` | 15.6 | 58 | 100 | mixed: blank + else-block + comment |
| 22 | `aerospike PartitionTracker` | 19.3 | 80 | 186 | blank-line between fields (every field) |
| 23 | `addthis meshy MeshyServer` | 20.5 | 18 | 30 | blank-line + FQN |
| 27 | `adamd z Z.java` | 29.7 | 37 | 130 | comment + structural |
| 30 | `accla d4m_api D4mDbInfo` | 46.6 | 65 | 112 | blank + comment + else-block |
| 31 | `aerospike AerospikeClient` | 147 | 20 | 40 | multi-line comment block + blank + redundant parens + FQN |
| 35 | `addthis stream-lib HyperLogLogPlus` | 152 | 33 | 9397 | long-array literal line-break (verified content-equivalent: 5670 vs 5669 numeric tokens, 19 vs 19 method decls; ~19KB size delta is whitespace) |
| 38 | `accla d4m Graphulo` | 161 | 138 | 562 | blank + comment + else-block + redundant parens |

### Pattern frequency (across the 15)

| Pattern | gjf normalises? | Scenarios where present |
|---|:---:|---|
| Blank-line placement (between fields / statements / class-body) | ❌ | 0, 3, 11, 14, 15, 19, 22, 23, 30, 38 |
| Comment placement (standalone-above ↔ trailing) | ❌ | 0, 6, 11, 19, 27, 30, 38 |
| Cast / redundant parens (`((Long) (value))` ↔ `(Long) value`) | ❌ | 7, 11, 14, 15, 31, 38 |
| FQN expansion (`java.lang.X` ↔ `X`) | ❌ | 22, 23, 31 |
| Block restructuring (`} else { if (X) }` ↔ `} else if (X)`) | ❌ | 11, 15, 19, 30, 38 |
| Long array-literal line-break | partial | 35 |
| Multi-line comment block formatting | partial | 31 |

Every observed pattern is a kind of source-given style that gjf preserves rather than canonicalises. **No scenario in the sample exhibits content loss, method reordering, or value disagreement.** The size deltas across the sample range from −310 to +428 chars on small/medium files, and +19042 on the [35] long-array case (verified pure reformatting, not duplication).

### Counter-evidence searched for, not found

- **Content loss** (Spork dropping comments / methods / lines): looked for, not present. This contrasts with Mastery (§6) where small-case is 71/793 chars — entire GPL header dropped.
- **Content duplication** (sibling-merger pathology, like the `//PBKDF2` `//AES` finding in §3): the [31] `// ---` separator-comment appears 3x in Spork vs 1x in dev was the closest candidate; on closer reading the dev output collapses three sibling comments into one in the same hunk, while Spork preserves all three. Borderline: arguable as "Spork preserved redundant base content" or "dev chose to deduplicate". Treating as AST-equivalent style for the purposes of this classification; flagged as the one residual where the call is non-trivial.
- **Method reordering**: confirmed equal counts on [35] (19 vs 19); not observed in eyeballs of others.
- **Different valid resolutions** (Spork picks a different merge than dev when both are plausible): not observed in the sample. All visible diff lines are paired one-to-one with formatter-preserved style differences.

### Conclusion

**15 of 15 sampled scenarios are AST-equivalent reformatting.** Scaling: the 39 still-differ Spork residuals are estimated at ≥90% AST-equivalent (Wilson 95% lower bound for 15/15 ≈ 78%; informal 90% point estimate given pattern uniformity). The §3 hypothesis ("structural FPs are AST-equivalent reformatting") **survives at higher sample size**; what failed in §8 was the prediction that gjf alone normalises these patterns. The patterns are AST-equivalent but *formatter-preserved* — gjf is deliberately minimally-opinionated about source-given style.

### Implications

- **Spork's FP rate is a comparator-ground-truth problem, not a Spork bug.** Under stronger ground truth (3b AST normalize, 3a test-suite execution), the ~93% of FPs that are AST-equivalent would clear. Under textual ground truth with gjf-only normalization (current state post-M3.5), they persist.
- **Spork ≠ Mastery on the failure axis.** Mastery (§6) drops actual content; no formatter/parser/test-suite can rebuild it. The Mastery 0-recovery in §8 is structural. Spork's 1-recovery is a consequence of gjf's minimal-opinion stance.
- **3b is the principled fix.** AST normalize via javalang or tree-sitter — parse both sides, walk the AST, emit a canonical form, then text-diff. Would collapse block-restructuring, paren-redundancy, FQN expansion, and blank-line placement. Deferred to a follow-up phase (Mergiraf integration plan TODO list) per user direction; not in scope for M3.5.
- **ISSUES.md #2 status:** stays at `decided — 3e implemented, partial`. 3j confirms the original §3 hypothesis at higher sample size, which lets the issue be re-framed as "comparator-gap" rather than "Spork bug" — but resolving it cleanly still requires 3b (which would recover the recoverable FPs and give a comparable measurement).

## 10. 3b Tier C empirical outcome (2026-05-14)

Tier 3 (AST normalize via tree-sitter-java 0.23.5) shipped per [`comparator-3b-ast-normalize.md`](comparator-3b-ast-normalize.md) §6 phases 3b.0–3b.4. Five transforms: `strip_comments`, `strip_blank_lines`, `flatten_else_if`, `strip_redundant_parens` (paren-wrapping-paren only), `strip_javalang_fqn`. Suite 41 → 58 passing.

### Result

| Tool | Pre-3b | Post-3b Tier C | Recovered |
|---|---|---|---:|
| Spork | TP 2 / FP 41 | TP 7 / FP 36 | **5 FPs** |
| Mastery | TP 0 / FP 44 | TP 0 / FP 44 | **0 FPs** |
| git-merge-file | TP 39 / FP 0 | unchanged | — |
| JDime | TP 0 / FP 2 | unchanged | — |

X=5 vs the plan §3 floor X≥30 and pause threshold X<25 (~65% recovery). **Plan §3 pause trigger fires.** Per plan §6 Phase 3b.4 + §10 acceptance, ISSUES.md #2 stays `decided`, not `resolved`.

### Per-scenario diagnosis

Three §9 scenarios re-examined under Tier 3:

| §9 idx | Scenario | §9 dominant pattern | Tier 3 match? | Residual diff |
|---:|---|---|:---:|---|
| 6 | `adangel pmd DOMLineNumbers` | comment placement | ✅ | — |
| 11 | `ab0oo APRSPacket` | mixed: blank + else-block + paren | ❌ | `((char) (body[0]))` vs `(char) body[0]`; `if (cond) { stmt; }` vs `if (cond) stmt;`; `(a \| b)` vs `a \| b`; `0xf0` vs `0xF0` |
| 22 | `aerospike PartitionTracker` | blank-line between fields | ❌ | `((Policy) (policy))` vs `(Policy) policy` (every constructor call) |

The pure-comment / pure-blank-line residuals close cleanly under Tier 3. The mixed-pattern residuals do not — and crucially, §22 (labelled "blank-line between fields" in §9's per-scenario table) actually has its post-gjf residual dominated by paren-wrapping-cast on every constructor call. §9's per-scenario label captured the most-visible pattern in the *raw* pre-gjf diff; gjf normalised the blank-line component leaving paren-wrapping-cast as the residual driver.

### Pattern frequency in the residual-after-gjf

Across the 36 still-FP Spork scenarios after Tier 3:

| Pattern | Tier C transform | In Tier C scope? |
|---|---|:---:|
| Paren-wrapping-cast (`((cast) (val))` ↔ `(cast) val`) | — | ❌ (rule matches paren-wrapping-paren only) |
| Single-stmt block unwrap (`if (c) { s; }` ↔ `if (c) s;`) | — | ❌ (distinct from `} else { if }` ↔ `} else if`) |
| Paren-around-binary-chain (`(a \| b \| c)` ↔ `a \| b \| c`) | — | ❌ (would need precedence reasoning) |
| Hex-literal case (`0xf0` ↔ `0xF0`) | — | ❌ (textual, not AST) |
| Long array-literal line-break | — | ❌ (Tier D per plan §2) |
| Comment-duplication (§3 `//PBKDF2` finding) | `strip_comments` | ✅ — Tier 3 makes both sides comment-free, so duplication is invisible (caveat: hides real pathology, per plan §7.1 threats-to-validity) |

### Reframing

The §9 conclusion — "15 of 15 sampled scenarios are AST-equivalent reformatting" — is empirically intact. What was wrong was the §3 + §6 estimate that Tier C's 5 specific transforms would recover ~90% of those AST-equivalent FPs. Tier C is a strict subset of "what a full AST normalizer would do"; the gap between "AST-equivalent" and "Tier-C-recoverable" turns out to be large on this dataset because the dominant residual-after-gjf patterns happen to fall outside the chosen 5 transforms.

The comparator-gap framing survives. ISSUES.md #2 stays at `decided`. Closing it cleanly requires either:

- **Tier D (broader transforms)**: cast-aware paren strip, single-stmt block unwrap, paren-around-binary-chain stripping with precedence guards. Each adds the same risk/scope discussion as the original Tier C transforms; collectively a separate cycle worth ~3–5 days.
- **3a (test-suite ground truth)**: bypasses textual ground truth entirely; expensive per `mergiraf-integration.md §3` cost analysis but principled.

Both remain deferred. The post-3b Tier C numbers are committed in `reports/results.csv` as the current honest interim state.

## 11. 3d Tier D empirical outcome (2026-05-15)

Six additional AST + token-canonical transforms shipped per [`comparator-3d-extended-ast-transforms.md`](comparator-3d-extended-ast-transforms.md) (prototype-grounded). Recovery measurement re-run on n=50:

| Tool | Pre-3d (post-3b) | Post-3d | Recovered |
|---|---|---|---:|
| Spork | TP 7 / FP 36 | TP 14 / FP 29 | **7** |
| Mastery | TP 0 / FP 44 | TP 10 / FP 34 | **10** |
| JDime | TP 0 / FP 2 | TP 1 / FP 1 | **1** |
| git-merge-file | TP 39 / FP 0 | unchanged | 0 |

### What closed

- **Single-stmt block unwrap (D.1)**: `if (c) { s; }` ↔ `if (c) s;` — common Spork bracketing pattern. Verified on §9 scenarios `accla d4m_api_java 0035` and `31dd135b67`.
- **Cast-paren strip in safe contexts (D.3)**: `((cast) val)` → `(cast) val` — the dominant pattern in §22 `aerospike PartitionTracker` (every constructor call); now closes when no postfix follows.
- **Precedence-aware binary paren strip (D.5)**: `(a == null) && b` strips. Common in defensive null-checks.
- **Token-canonical fold (D.6)**: gjf's line-wrap differences (when token counts differ between Spork output and dev) no longer cause spurious mismatches. Single-largest-contributor in the prototype (+3 of the +7 Spork recoveries).

### Mastery's surprise +10

§6 framed Mastery as "intrinsic content loss" parallel to JDime. Tier D's D.6 token-canonical fold revealed a finer-grained truth: in 10/44 Mastery scenarios the content loss is **exclusively comment-loss** (dev has 80+ comment tokens; Mastery's output has 0). Tier C `strip_comments` and Tier D `token_canonical_fold` together normalize both sides to byte-identical canonical text in these cases.

This is consistent with the [`comparator-3b-ast-normalize.md §7.1`](comparator-3b-ast-normalize.md) threats-to-validity entry: "Comparator treats all comments as equivalent. A diff in Javadoc / inline comments alone will not register as a tool disagreement."

The remaining 34 Mastery FPs involve genuine code-content loss — recoverable only via 3a test-suite ground truth, if at all. Mastery's family-weakness framing with JDime stands for those 34.

### What still doesn't close

The 29 remaining Spork FPs are dominated by:

- **Long-array-literal whitespace** (6 scenarios, including the §35 `addthis stream-lib HyperLogLogPlus` 161KB case). gjf wraps multi-megabyte numeric arrays differently depending on token count; D.6 token-fold can't normalize this without exponential time. Tier E candidate.
- **`+`/`*` same-op-strip** (~5-8 scenarios). Excluded from D.5 due to string-concat-vs-numeric type-promotion concerns (`c + (a + b)` where c is String and a, b numeric evaluates differently from `c + a + b`). Tier E with type-inference could address.
- **Long tail of mixed patterns** (~15 scenarios). Each scenario has multiple residual patterns; closing requires multiple transforms in concert. Diminishing returns.

### Implications

- **Tier D recovery (X = 12 cumulative over Tier C's 5) does NOT hit the original 3b §3 floor of X ≥ 30.** ISSUES.md #2 stays at `decided`.
- Tier D HITS its own (lower) acceptance floor (X_d ≥ 3) and stretch (X_d = 7).
- The comparator-gap framing remains intact: Spork's residuals are still AST-equivalent reformatting. Tier D has substantially closed the gap; full closure needs Tier E or 3a.

## 7. Reproducibility

```python
# scratch script — adapt paths and re-run for fresh results
import json, re
from pathlib import Path
from collections import Counter

R = Path("merge-tool-comparison/data/results")
S = Path("merge-tool-comparison/data/scenarios")

def n_base(c):
    ls = [l.rstrip() for l in c.replace("\r\n", "\n").split("\n")]
    while ls and not ls[-1]: ls.pop()
    return "\n".join(ls)
def n_ws(c): return re.sub(r"\s+", " ", c).strip()
def strip_imports(c): return re.sub(r"^\s*import\s+[^;]+;\s*$", "", c, flags=re.MULTILINE)

buckets = Counter()
for d in sorted(R.iterdir()):
    sp, sc = d / "spork.json", S / f"{d.name}.json"
    if not sp.exists() or not sc.exists(): continue
    s = json.loads(sp.read_text())
    if s.get("outcome") != "clean": continue
    dev = json.loads(sc.read_text())["developer_resolution"]
    merged = s.get("merged_content") or ""
    if n_base(merged) == n_base(dev): continue  # actually TP
    if n_ws(merged) == n_ws(dev): buckets["whitespace_only"] += 1
    elif n_ws(strip_imports(merged)) == n_ws(strip_imports(dev)): buckets["imports_plus_whitespace"] += 1
    else: buckets["structural"] += 1
print(buckets)
```

§8 formatter-bucketing reproduction (run from `merge-tool-comparison/` with `merge-tools/google-java-format:1.22.0` built):

```python
import json, os, sys; sys.path.insert(0, '.')
os.environ['MERGE_COMPARATOR_FORMATTER'] = 'on'
from src.evaluation.comparator import normalize_content, _format_java
from collections import Counter
from pathlib import Path

def classify(merged, dev):
    nm, nd = normalize_content(merged), normalize_content(dev)
    if nm == nd: return "base_match"
    fm, fd = _format_java(nm), _format_java(nd)
    if fm is None or fd is None: return "parse_fail"
    return "format_match" if normalize_content(fm) == normalize_content(fd) else "still_differ"

for tool in ("spork", "mastery"):
    b = Counter()
    for d in sorted(Path("data/results").iterdir()):
        rp, sc = d / f"{tool}.json", Path("data/scenarios") / f"{d.name}.json"
        if not rp.exists() or not sc.exists(): continue
        s = json.loads(rp.read_text())
        if s.get("outcome") != "clean": continue
        dev = json.loads(sc.read_text())["developer_resolution"]
        b[classify(s.get("merged_content") or "", dev)] += 1
    print(f"{tool}: {dict(b)}")
```
