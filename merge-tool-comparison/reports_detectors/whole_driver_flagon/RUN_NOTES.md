# S-D8 run notes (session log)

## Paste-time patch to the kickoff prompt (Ali, 2026-07-22 — no §12 amendment)

The kickoff's env-gate wording ("flag OFF; must reproduce the post-flip 1779")
is replaced by a **derived-target gate**: the frozen suite `732d8ff` includes
the #29 post-fix commits (`5ed92a2`, `f964354`), so a correct environment must
reproduce 1779 shifted by exactly the five known, adjudicated verdict changes
(the 4 unblocked control merges — aerospike b77316ac92, cloudfoundry
0d588aa1e7 + f994a25985, mtedone 1075ffea79 — plus the retired tcurdt
77d052996a positive; all five route to Mergiraf under auto, so the
postfix2 known answers apply directly).

**Pre-registered derived target (committed before any run):
pooled flag-OFF cost = 1779 + 9 − 4 = 1784** (pos 1768 / ctl 16), with
per-file accept/reject agreement against the P3 post-flip table everywhere
except those five files, allowing only the documented borderline
textual↔semantic nondeterminism class (P3 saw 2 such reject-reason flips:
datastax 725b790a79, graphity 2a8e8c75e9 — cost-identical either way).
Full per-file table: `predicted_flagoff.csv` (`tools/sd8_predict_flagoff.py`,
derivation machinery cross-validated by reproducing the P3 1779 to the digit).
The one git-routed semantic flag (progether e28401af85, outside the postfix2
known-answer domain) was verified locally at HEAD pre-launch: unchanged.

Both arms stay on the frozen suite at HEAD; the flag-OFF arm is NOT pinned to
`9e25b4e` (pinning would smuggle the post-fix changes into the flag-ON delta
and break the freeze). Arms differ ONLY by
`SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS`.

## Image-provisioning deviation-within-intent (Ali, 2026-07-22)

Reasoned deviation from the build-on-instance standing rule, split by
reproducibility: drift-risk images shipped, pinned images built — all pinned
images (mergiraf 0.17.0, RM2 2.4.0, spork 0.5.0 dual-tagged as legacy
`merge-tools/spork`, weave 0.3.2, gjf 1.22.0, git-merge-file) are built
on-instance; only the unpinned jdime:latest + mastery:latest (Dockerfiles
clone upstream HEAD — ISSUES #10 retro-pinning TODO) are docker-saved from
the local amd64 images that produced the committed canonical table
(arch-verified before saving; transferred via `cat|ssh` with sha256
verification). Every image is live-probed on-instance and the committed
canonical six-tool table must reproduce exactly (count columns) before any
scoring.

## Operational decisions (this session)

- New harness `tools/whole_driver_flagon.py` imports `whole_driver_eval.py`
  unmodified (S-D7 precedent: the committed P2 instrument stays untouched).
- Arms run SEQUENTIALLY, flag-OFF first; the reconciliation gate
  (`--check-gate`) runs between arms and aborts the battery before the
  flag-ON arm burns if the environment is wrong. `_JAVA_OPTIONS` left unset
  to match P2/P3 single-worker latency conditions (latency is a first-class
  deliverable).
- `DRIVER_COMMIT` = the manifest's `detector_suite_commit` (`732d8ff`),
  the S-D7 convention — driver code at HEAD is byte-identical to the freeze.
- Parallel-run hygiene (S-D7 concurrent): S-D8 launched in **eu-north-1**
  (Ali, 2026-07-22 — asked to run in parallel without waiting for S-D7's
  teardown; the 8-vCPU cap is per-region, so a second region runs truly
  concurrently with ZERO shared resources — different region, own key name,
  own SG). First-launch `PendingVerification` in the new region cleared after
  one ~10-min retry (the documented CLI-DEPLOY gotcha).
- **Cycle resources (teardown record):** region `eu-north-1`, instance
  `i-0006f73fee2019c40` (`sd8-flagon`, c7i.2xlarge, launched 2026-07-22
  11:08 UTC), SG `sg-02be4b932de464e8f` (`sd8-sg`), key `p2key-sd8`
  (imported public half of `~/.ssh/p2key.pem`). Bundle @ repo `50d2754`;
  transfer via `cat|ssh`, all three sha256s verified identical. Teardown =
  terminate instance + delete SG + delete key `p2key-sd8` (eu-north-1 only —
  S-D7's eu-central-1 resources are NOT ours to touch).

## Cycle completion (2026-07-23)

Battery ran 2026-07-22 11:19 → 2026-07-23 10:08 UTC, every step first-try:
smoke → canonical gate PASS (36/36, Spork 32/11) → flag-OFF (10.7 h) →
**reconciliation gate PASS: measured 1784 = pre-registered 1784 to the
digit** (5/5 post-fix movements, 2 borderline margin flips only) → flag-ON
(11.8 h) → report. Headline: pooled cost 1784 → 1579 (−205), latency price
+8.3 s/file median; both control blocks = the S-D7-ruled incidental-but-true
flags (Mergiraf-routed → rulings transfer 1:1). Artifacts pulled as one tar
(sha256 `e3a7863c…`, verified), instance + SG + key torn down, region
verified empty (instances and volumes). Mid-cycle incident: local IP
rotation broke the SG /32 (instance was healthy; rule updated) — recorded in
CLI-DEPLOY seventh-cycle gotchas. Results: FINDINGS §11, manifest S-D8
block, ISSUES #31 S-D8 summary. Default-enabling decision: Ali, post-S-D8.
