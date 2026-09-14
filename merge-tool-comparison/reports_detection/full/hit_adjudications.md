# Stage-C Hit Adjudications — plan §4.6 (FINAL — AMENDED 2026-09-04)

**AMENDMENT 2026-09-04 (Ali, on the audit in `audit_2026-09-04.md`).** Two of the
eleven positive rulings change from CAUSAL to DETECTOR-FP: **atam4j** (the flagged
file compiles; the merge-induced break is in an unflagged sibling file) and
**tcurdt_jdeb** (the flagged site is a method call; the flag was already retired by
the post-fix runs). Three site counts are corrected. The sentence "no positive hit
depends on either defect" is withdrawn. The control root-cause decomposition is
corrected against the post-fix runs. Headline: **9 CAUSAL of 164 = 5.5% [2.9, 10.1]**
(was 11 = 6.7%). Text from 2026-06-20 is kept where it still holds; changed cells
are marked *(amended)*.

**ADJUDICATED 2026-06-20 (Ali, via `adjudication_ui.html`).** All 15 Stage-C
flags ruled; 15/15 reviewed. Promoted `hit_adjudications_draft.md`; at that time
every draft label was accepted, zero overrides. Detectors frozen at `843e5f5`; no
re-runs. The post-fix run and the §4.7 miss list are separate deliverables.

Protocol (per flag): (i) is the flagged pattern actually present in the merged
output? (ii) is it merge-induced — in the merged file but in **neither** parent?
(iii) does it plausibly explain the test failure (positives)? Labels: **CAUSAL**
/ **REAL-BUT-INCIDENTAL** / **DETECTOR-FP**. Evidence per flag was rendered in
the adjudication UI: detector output verbatim, merged-coordinate flagged sites
(re-located because RM2 var-lane line numbers are stripped-text coordinates),
the old→new parent-presence table, the dev-vs-Mergiraf diff, and the full source
viewer. Tool note: RM2 detects the underlying renames in most rows; the four
control FPs and the two amended positives are downstream scan defects or
mispairings, not hallucinated code.

**Limits of the 2026-06-20 procedure (added 2026-09-04).** One rater, who also
wrote the detectors. Not blind: the arm (positive/control) and the test outcome were
shown on every item. The draft label and its rationale were shown before ruling,
with a one-key accept. The committed rationales are the draft rationales expanded
with merged line numbers; only the comatoes row carries a note written by the rater. CAUSAL was
inferred from reading merged source, not from a build log. Rulings were kept in
browser storage; no export of them was committed, so the counts in this file are
the only trace. The 2026-07-03 post-fix analysis had already shown the tcurdt site
to be a method call without amending this record. The 2026-09-04 audit was the
first full re-check of all eleven rulings against the merged source; it overturned
atam4j and formalized tcurdt.

## Counts *(amended)*

| | n | CAUSAL | REAL-BUT-INCIDENTAL | DETECTOR-FP |
|---|---|---|---|---|
| **positives** (detector FLAG, `Tests_failed`) | 11 | **9** | 0 | **2** |
| **controls** (detector FLAG, `Tests_passed`) | 4 | 0 | 0 | **4** |

Flag precision on the positives: **9/11 = 82%**. Flag precision over all 15 ruled
flags: **9/15 = 60% [35.7, 80.2]**. The 12th blocked positive (jadventure) is a
fail-closed RM2 crash — a defensive block, **not** adjudicated as a detection.

## Positives (11) — 9 CAUSAL, 2 DETECTOR-FP *(amended)*

| merge | lanes | ruling | rationale |
|---|---|---|---|
| ahome-it_lienzo-core | both | **CAUSAL** | field rename `innerLayoutContainer→m_innerLayoutContainer` half-applied; the bare reference at merged L248 is unresolved = compile error. Joern + RM2 var-lane agree on the same site (RM2 reported it at stripped-L78). |
| atam4j | RM2 ×4 records | **DETECTOR-FP** *(amended)* | Merged L27 is the **declaration** `public Response getTestRunResultFromServer(String testsURI)`; L34 declares the new name; L46/51/59 pass a `String` and bind to L27. Nothing is stale; the file compiles. The call lane has no declaration guard and counted the declaration as a caller. The rename pair is an RM2 artifact: `theirs` keeps the old method and adds the new one. The merge did fail for a merge-induced reason, in the **unflagged** sibling `PassingTestAcceptanceTest.java`: merged L38 uses `PassingTest.class` with no import (ours' import block, theirs' test). That file was scored CLEAN by all five detectors — a measured cross-file false negative. |
| comatoes_ftl-profile-editor | Joern ×1 (+ RM2 ×2 artifacts) | **CAUSAL** | unresolved `gameState` at merged L147 in `readShip` (declared only at L35, inside a different method) carries the merge on its own. *Ali's note (2026-06-20):* the RM2 `setReservePowerCapacity→setSectorNumber` pairing is ambiguous — the two methods' implementations are very similar and the naming gives no hint whether they are the same method. `setReservePowerCapacity` persists in every parent and in the developer resolution, so the RM2 lane is not load-bearing (its two records are a qualified call at L105 and the declaration at L468). Ruling **CAUSAL** via Joern; the rater recorded that this mostly agrees with the draft. |
| datastax_java-driver | Joern | **CAUSAL** | merged L134 `isShutdown.get()` uses a field that no longer exists; only the method `isShutdown()` survives (L372). The field `AtomicBoolean isShutdown` was declared in base and theirs and resolved there; the merge dropped it. *(wording amended: the detector fires on names that resolved in the parents and do not resolve in merged.)* |
| erudika_para | both | **CAUSAL** | variable rename `m→method` half-applied; bare `m` unresolved at L109 (`detectNestedInvocations(m)`, dual-lane). Pilot hit reconfirmed (in-sample: the pilot is a subset of this population). |
| jacquesberger | Joern ×2 | **CAUSAL** | unresolved `bookTitleList` (L34) and `outputList` (L43) — both dangling halves. Pilot hit reconfirmed (in-sample). |
| jcabi RtGistITCase | RM2 | **CAUSAL** | stale caller `RtGistITCase.gist()` at L82 after rename to `github` (only `github()` is declared, L96) = compile error. |
| jcabi RtHooksITCase | RM2 ×4 records | **CAUSAL** *(count amended)* | one stale caller: L60 `repo().hooks()` — zero-arg, and no zero-arg `repo()` exists = compile error. L154 is the declaration `private static Repo repo(final Repos repos)`; L99/L122 call it with a `Repos` and resolve. 1 of the 4 records is stale. |
| jdupl_lancoder | Joern | **CAUSAL** | unresolved `ctxApi` in `run` (L49): declared and resolved in every parent, undeclared in merged. *(wording amended as for datastax.)* |
| softinstigate_restheart | both | **CAUSAL** *(count amended)* | `request→req` / `response→res` half-applied; **3 stale sites** (L138/L141 `request`, L143 `response`), dual-lane on L138 and L143. The RM2 records at L255/L260 are the method declarations `request()`/`response()` — the `(`-defect; dropped by the post-fix run. |
| tcurdt_jdeb | RM2 | **DETECTOR-FP** *(amended)* | Merged L95 is `options.compression().toCompressedOutputStream(...)`: `compression` is a method invoked on the parameter `TarOptions options` declared at L87. Not a bare use; no compile error. This is the `(`-defect. The line is identical in `theirs` and in the developer resolution. Retired by both post-fix runs (`../postfix/`, `../postfix2/`). |

**Verify cases (2) — status after amendment:** comatoes resolved as stated on
2026-06-20 (Joern carries the ruling). tcurdt: the 2026-06-20 check confirmed
"`compression` undeclared in this file", which is true but irrelevant for a
qualified method call; the CAUSAL ruling is withdrawn.

Fail-closed positive (jadventure, RM2 crash): counts in R2's fail-closed row;
not a detection, not adjudicated here.

## Controls (4) — all DETECTOR-FP (rulings unchanged; root causes *amended*)

| merge | ruling | root cause |
|---|---|---|
| aerospike GrpcStreamingCall | **DETECTOR-FP** | RM2 correctly detected the *field* rename `isSingleResponse→numExpectedResponses`, but the var-lane scan then matched the surviving **method** `isSingleResponse()` (declared & live at merged L210, and in the developer resolution) — a different program element. Missing `(`-exclusion. Cleared by post-fix round 1. |
| cloudfoundry Operator (0d588aa1e7) | **DETECTOR-FP** | the RM2 pair `request→response` is a mispairing (`request` occurs 10× in every version; nothing named `request` disappeared). The var-lane matched the **method** `request(HttpMethod)` and a lambda parameter `request`. Round 1's `(`-exclusion removed the method sites; the lambda-parameter site needed round 2's guard extension. |
| cloudfoundry Operator (f994a25985) | **DETECTOR-FP** | same mechanism as the other cf-java-client Operator FP; cleared in round 2. |
| mtedone_podam | **DETECTOR-FP** | `mapType` IS declared (merged L2459 `Class<? extends Map<?, ?>> mapType =`, param at L2746; 10 uses in merged). The reported lines (1538–1763) are stripped-text coordinates that land on Javadoc — the char-literal `\n` bug shifted them. The declaration guard was blinded by the wildcard `?` in the declared type, which its type class did not accept; the newline bug alone did not cause the flag. Cleared in round 2. |

All four controls pass tests. **Post-fix evidence (`../postfix/`, `../postfix2/`),
replacing the 2026-06-20 two-defect account:** round 1 (`5ed92a2`: the
`(`-exclusion and the char-literal `\n` fix) cleared **aerospike only**; 3/193
remained. Round 2 (`f964354`: declaration guard extended to generics wildcards and
lambda parameters) cleared cloudfoundry ×2 and podam; 0/193. One positive (tcurdt)
depended on the `(`-defect and was retired in round 1; softinstigate lost 2 of its 5
RM2 records to the same fix and stands on the Joern lane. No other verdict changed
in either direction (5 changes total across 471 files, all FLAG→CLEAN).

## Bottom line for the results chapter *(amended)*

- **R2: 9 CAUSAL of 164 = 5.5% [2.9, 10.1]** real silent failures caught by a
  detector flag. Frozen-run block rate 12/164 = 7.3% [4.2, 12.4] (11 flags + 1
  fail-closed). Post-fix block rate 11/164 = 6.7% [3.8, 11.6] (10 flags — 9 causal + the
  atam4j DETECTOR-FP — + 1 fail-closed; atam4j stays flagged post-fix because the
  call lane's missing declaration guard was never fixed). Cite the composition with the number.
- **R1: 4/193 = 2.1% [0.8, 5.2]** at the frozen suite, all four DETECTOR-FP;
  0/193 = 0.0% [0, 2.0] after two post-fix rounds.
- Flag precision 9/11 on the positives; 9/15 over all ruled flags.
- Detection mass is entirely the #6 rename/declaration-interference family;
  categories #3/#5 had zero occurrences (0 detections, 0 FPs) on 443 real files.
- One measured cross-file false negative: the atam4j sibling file.
