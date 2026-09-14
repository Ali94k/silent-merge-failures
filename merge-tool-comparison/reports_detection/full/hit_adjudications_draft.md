# Stage-C Hit Adjudications — plan §4.6 (DRAFT for Ali; 15 flags + 1 fail-closed)

Protocol: (i) pattern present in merged output? (ii) merge-induced (absent both parents)? (iii) plausibly linked to the test failure? Labels: CAUSAL / REAL-BUT-INCIDENTAL / DETECTOR-FP. Evidence: `summary.txt` flag list + `raw_results.json` (cached merged content + per-issue lines). The differential construction gives (ii) by design for every Joern id-lane hit and every per-branch RM2 hit; (i) is recorded per issue; (iii) is the judgment call.

## Positives (11) — proposed labels

| merge | lanes | proposed | rationale sketch |
|---|---|---|---|
| ahome-it_lienzo-core | both | **CAUSAL** | field rename `innerLayoutContainer→m_…` half-applied; unresolved id = compile error |
| atam4j | RM2 ×4 | **CAUSAL** | method rename, 4 stale callers of `getTestRunResultFromServer` = compile error |
| comatoes_ftl-profile-editor | both | **CAUSAL (verify rename pairing)** | unresolved `gameState` is solid; RM2's `setReservePowerCapacity→setSectorNumber` pairing looks like RM2 matching dissimilar methods — check before citing the RM2 lane |
| datastax_java-driver | Joern | **CAUSAL** | unresolved `isShutdown` in `borrowConnection` |
| erudika_para | both | **CAUSAL** | pilot hit reconfirmed (adjudicated in pilot_v2) |
| jacquesberger | Joern ×2 | **CAUSAL** | pilot hit reconfirmed |
| jcabi RtGistITCase | RM2 | **CAUSAL** | stale caller `gist(` after rename to `github` |
| jcabi RtHooksITCase | RM2 ×4 | **CAUSAL** | stale callers `repo(` after rename to `repos` |
| jdupl_lancoder | Joern | **CAUSAL** | unresolved `ctxApi` in `run` |
| softinstigate_restheart | both | **CAUSAL** | `request→req`/`response→res` half-applied, 7 stale sites, dual-lane |
| tcurdt_jdeb | RM2 | **CAUSAL (verify)** | field rename `compression→options`; single site — confirm `compression` undeclared in merged |

Fail-closed positive (jadventure, RM2 crash): counts in R2's fail-closed row, not adjudicated as a detection.

## Controls (4) — proposed labels

| merge | proposed | root cause |
|---|---|---|
| aerospike GrpcStreamingCall | **DETECTOR-FP** | var-lane match on method `isSingleResponse()` — missing `(`-exclusion |
| cloudfoundry Operator ×2 | **DETECTOR-FP** | identical: var `request` vs method `request(...)` |
| mtedone_podam | **DETECTOR-FP** | comment-stripper newline bug: `mapType` IS declared (verified against raw merged content); guard blinded by corrupted stripped text |

## Post-fix run note

Both FP causes are one-line fixes in `rename_conflict.py` (skip var-lane matches followed by `(`; exclude `\n` from the char-literal class in `_strip_comments_and_strings`). Per G2: fixes go in AFTER adjudication, new commit, separately-labeled re-run (~9 h). Expected: R1 → 0/193 [0, 1.9]; R2 unchanged or +0 (no positive hit depends on either defect — verify during adjudication).
