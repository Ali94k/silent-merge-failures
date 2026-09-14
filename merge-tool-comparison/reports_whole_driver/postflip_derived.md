# Post-flip driver-auto — DERIVED prediction (from committed P2 data)

Basis: P2 `raw_results.json` (pre-flip run @ driver `843e5f5`); 471 files; clusters {'SYMBOL_CASCADE': 76, 'NONE': 229, 'INTRA_BODY': 79, 'MIGRATE_DECL': 47, 'LOCAL_DECL_EDIT': 40}.
Identity: NONE→driver-git rows; else→driver-mergiraf rows. The flip commit
touches only `auto_backend._route`, so per-file results carry over exactly.
**The measured post-flip AWS re-run must match this file-for-file on**
**`outcome` + `reject_reason`** (environment-independent). The cost/`cls`
columns here are scored in the *local* environment — divergent outputs are
dev-match-scored, which is normalization-sensitive (FINDINGS §7a): e.g. the
pre-flip control-FP count re-scores locally as 21 vs 33 on AWS. Citable
post-flip cost tables come from the AWS-scored measured run; the
before/after below is internally consistent (both sides local-scored).

## derived post-flip driver-auto
  arm       n   TP   FP   TN   FN  CR    cost  cost/n
  pos     232    3  170   54    5   0    1759    7.58
  ctl     239  219    0   17    3   0      20    0.08
  ALL     471  222  170   71    8   0    1779    3.78
  three-outcome pos: {'semantic': 11, 'textual': 46, 'accept': 123}
  three-outcome ctl: {'accept': 175, 'semantic': 4, 'textual': 16}

## measured PRE-flip driver-auto (P2)
  arm       n   TP   FP   TN   FN  CR    cost  cost/n
  pos     232    5  163   59    5   0    1694    7.30
  ctl     239  197   21   18    3   0     231    0.97
  ALL     471  202  184   77    8   0    1925    4.09
  three-outcome pos: {'semantic': 14, 'textual': 48, 'accept': 118}
  three-outcome ctl: {'accept': 175, 'semantic': 6, 'textual': 14}

## Before/after (the flip's predicted effect)
  control FPs from routing: 21 → 0
  pooled weighted cost improvement (pre − post): 146

