# S-D8 pre-registered flag-OFF prediction (env-gate reference)

Derived from the committed P3 post-flip run @ `9e25b4e` plus the
post-fix known answers @ `f964354` (reports_detection/postfix2/) — the
frozen-suite HEAD's default lanes. Committed BEFORE the S-D8 AWS cycle.

- files: 471 (pos 232 / ctl 239)
- P3 measured pooled cost @ 9e25b4e: **1779**
- predicted flag-OFF pooled cost @ HEAD: **1784**  (pos 1768 / ctl 16)
- predicted changes vs P3: 7

| arm | scenario | P3 → predicted | basis |
|---|---|---|---|
| pos | datastax_java-driver__725b790a79__driver-core_src_main_java_ | conflict/semantic/TN → conflict/textual/TN | unchanged | borderline-margin (textual<->semantic, cost-identical) |
| pos | tcurdt_jdeb__77d052996a__src_main_java_org_vafer_jdeb_DataBu | conflict/semantic/TN → clean//FP | postfix2-fix (5ed92a2+f964354) |
| ctl | aerospike_aerospike-client-java__b77316ac92__proxy_src_com_a | conflict/semantic/TN → clean//TP | postfix2-fix (5ed92a2+f964354) |
| ctl | cloudfoundry_cf-java-client__0d588aa1e7__cloudfoundry-client | conflict/semantic/TN → clean//TP | postfix2-fix (5ed92a2+f964354) |
| ctl | cloudfoundry_cf-java-client__f994a25985__cloudfoundry-client | conflict/semantic/TN → clean//TP | postfix2-fix (5ed92a2+f964354) |
| ctl | graphity_graphity-client__2a8e8c75e9__src_main_java_org_grap | conflict/semantic/TN → conflict/textual/TN | unchanged | borderline-margin (textual<->semantic, cost-identical) |
| ctl | mtedone_podam__1075ffea79__src_main_java_uk_co_jemos_podam_a | conflict/semantic/TN → clean//TP | postfix2-fix (5ed92a2+f964354) |

Gate at scoring time: every measured flag-OFF file must match
`predicted_outcome`/`predicted_reject_reason` (reject-reason flips inside
the borderline-margin rows are allowed — cost-identical); any other
difference fails the gate unless attributable to the fix commits with a
written per-file rationale.

Git-routed semantic flags needing local pre-launch verification @ HEAD:
- progether_jadventure__e28401af85__src_main_java_com_jadventure_game_prompts_CommandParser.java
  — VERIFIED locally 2026-07-22 (HEAD, flag unset): `conflict/semantic`,
  route NONE→git, rt 77 s — unchanged vs P3, as predicted.
