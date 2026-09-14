# P2 AWS Deployment — actual CLI record + teardown

What was actually run to stand up the P2 whole-driver run on EC2 (the
**CLI path** — `RUNBOOK.md` documents the console alternative). Real commands,
real resource IDs, and the **teardown** so nothing is left billing.

First deployed **2026-06-25** (region `eu-central-1`). Driver `843e5f5`.

## Identity / region

- IAM user **`claude-p2`** — `AmazonEC2FullAccess` only (no billing/IAM). Used
  for all CLI calls; creds in `~/.aws/credentials` (never committed).
- Region **`eu-central-1`**. Billing alarm: AWS Budgets (console, root login).

## Resources created

| Resource | ID / value |
|---|---|
| Key pair | `p2key` → private key `~/.ssh/p2key.pem` (chmod 600) |
| Security group | `sg-052531d61c0cfb520` (name `p2-sg`, VPC `vpc-03b124d1d7c1b9bc2`) |
| SG ingress | SSH 22 from your-Mac-IP/32 **and** EC2 Instance Connect prefix list `pl-03384955215625250` |
| AMI | `ami-042dc8681de073ac4` (Ubuntu 24.04 LTS, x86_64, gp3) |
| Instance | `i-0424514e6763b3c52` · `c7i.2xlarge` · 80 GB gp3 (DeleteOnTermination) |
| Public DNS | `ec2-63-177-64-178.eu-central-1.compute.amazonaws.com` |

## Launch (what we ran)

```bash
REGION=eu-central-1
# 0. discover (read-only)
MYIP=$(curl -s https://checkip.amazonaws.com)
AMI=$(aws ec2 describe-images --region $REGION --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd*/ubuntu-noble-24.04-amd64-server-*" "Name=state,Values=available" \
  --query 'sort_by(Images,&CreationDate)[-1].ImageId' --output text)
VPC=$(aws ec2 describe-vpcs --region $REGION --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)
PL=$(aws ec2 describe-managed-prefix-lists --region $REGION \
  --filters Name=prefix-list-name,Values=com.amazonaws.$REGION.ec2-instance-connect \
  --query 'PrefixLists[0].PrefixListId' --output text)

# 1. key pair
aws ec2 create-key-pair --region $REGION --key-name p2key \
  --query KeyMaterial --output text > ~/.ssh/p2key.pem && chmod 600 ~/.ssh/p2key.pem

# 2. security group + ingress
SG=$(aws ec2 create-security-group --region $REGION --group-name p2-sg \
  --description "P2 whole-driver SSH" --vpc-id $VPC --query GroupId --output text)
aws ec2 authorize-security-group-ingress --region $REGION --group-id $SG \
  --protocol tcp --port 22 --cidr $MYIP/32
aws ec2 authorize-security-group-ingress --region $REGION --group-id $SG \
  --ip-permissions "IpProtocol=tcp,FromPort=22,ToPort=22,PrefixListIds=[{PrefixListId=$PL}]"

# 3. launch (this starts billing)
IID=$(aws ec2 run-instances --region $REGION --image-id $AMI \
  --instance-type c7i.2xlarge --key-name p2key --security-group-ids $SG \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":80,"VolumeType":"gp3","DeleteOnTermination":true}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=p2-whole-driver}]' \
  --query 'Instances[0].InstanceId' --output text)
aws ec2 wait instance-running --region $REGION --instance-ids $IID
DNS=$(aws ec2 describe-instances --region $REGION --instance-ids $IID \
  --query 'Reservations[0].Instances[0].PublicDnsName' --output text)
```

> ⚠️ **New-account gotcha:** the first `run-instances` may return
> `PendingVerification` — AWS validates new accounts before the first launch in
> a region (minutes–4 h). Just retry; key pair + SG persist.

## Bundle → transfer → provision → run

```bash
# LOCAL (repo root) — needs Docker Desktop up for `docker save`
bash deploy/aws/bundle.sh                       # → deploy/dist/{repo,scenarios,images}.tar.gz (611 MB)
scp -i ~/.ssh/p2key.pem deploy/dist/*.tar.gz deploy/aws/provision.sh ubuntu@$DNS:~

# ON INSTANCE
ssh -i ~/.ssh/p2key.pem ubuntu@$DNS 'bash provision.sh'   # Docker, JDK21, Joern 4.0.436, venv, docker load
# re-login (docker group), then run detached:
ssh -i ~/.ssh/p2key.pem ubuntu@$DNS \
 'cd ~/thesis-projects/merge-tool-comparison && export PATH=$HOME/bin/joern/joern-cli:$PATH && \
  nohup .venv/bin/python tools/whole_driver_eval.py > reports_whole_driver/full_run.log 2>&1 < /dev/null &'
```

Non-interactive SSH skips `.bashrc`, so **Joern must be put on PATH explicitly**
(`export PATH=$HOME/bin/joern/joern-cli:$PATH`) in every harness invocation.

## Collect results (when full_run.log reaches 2355/2355)

```bash
scp -i ~/.ssh/p2key.pem \
  ubuntu@$DNS:~/thesis-projects/merge-tool-comparison/reports_whole_driver/{summary.txt,scenarios.csv,raw_results.json,full_run.log} \
  merge-tool-comparison/reports_whole_driver/
```

## TEARDOWN (do this when done — stops all billing)

```bash
REGION=eu-central-1
IID=i-0424514e6763b3c52
SG=sg-052531d61c0cfb520
aws ec2 terminate-instances --region $REGION --instance-ids $IID
aws ec2 wait instance-terminated --region $REGION --instance-ids $IID   # SG can't be deleted while in use
aws ec2 delete-security-group --region $REGION --group-id $SG
aws ec2 delete-key-pair --region $REGION --key-name p2key
# EBS volume is DeleteOnTermination=true → removed with the instance.
# verify nothing remains:
aws ec2 describe-instances --region $REGION \
  --filters Name=instance-state-name,Values=running,pending,stopped \
  --query 'Reservations[].Instances[].InstanceId' --output text
rm -f ~/.ssh/p2key.pem; rm -rf deploy/dist   # optional local cleanup
```

## Lesson: an arm64 image dies SILENTLY on x86 — platform-pin and probe

The P2 bundle shipped `merge-tools/google-java-format:1.22.0` built natively on
Apple Silicon (arm64) — the one Dockerfile invocation without
`--platform linux/amd64`. On the x86 instance every call failed with
`exec format error`, and the comparator's `contents_match` **silently degraded**
to whitespace-only normalization (its formatter tier treats failure as
"unavailable" by design), producing pre-M3.5-looking numbers (Spork 1/42
instead of 32/11) until diagnosed on 2026-07-02. Fixes + rules:

- **Build/pull every image with `--platform linux/amd64`** if it will ever run
  on x86 — or rebuild on the target: `docker build -t
  merge-tools/google-java-format:1.22.0 docker/google-java-format/` (fast, jar
  download only).
- **Probe, don't assume:** after provisioning, run a real formatter call and a
  `contents_match` known-answer test (paren-strip must match). A loaded image
  is not a working image; the failure mode is silent by design.
- Validation bar for a scoring environment: it must **reproduce the committed
  canonical six-tool table exactly** (Spork 32/11 exercises all 21 transforms).

## Second cycle record (P3/P4, 2026-07-02/03)

Same launch pattern; resources: key `p2key` (recreated), SG
`sg-0b071b0f414031af1`, instance `i-0a586e6828512ea9f` (`p3p4-cycle`).
Ran: six-tool canonical run (n=50) + post-flip `driver-auto` re-run
(471 files, ~13 h) with `DRIVER_COMMIT=9e25b4e`. Extra transfer: canonical
`data/scenarios` tarball (gitignored). **Gotcha:** macOS `tar` ships AppleDouble
`._*` files that break JSON loaders on Linux — `find data -name "._*" -delete`
after extraction (or set `COPYFILE_DISABLE=1` when creating). Torn down +
verified empty 2026-07-03 (~$6.5).

## Third cycle record (#29 post-fix, 2026-07-03)

Instance `i-03faae732c0fad85f` (`postfix-29`), ~1.5 h, ~$1. Two labeled
RM2-lane-only rounds (`5ed92a2`, `f964354`): untouched detector lanes carried
at frozen Stage-C verdicts via cache-key migration; fresh G1 sanity each round;
→ R1 0/193, R2 11/164. Torn down + verified empty. **Gotcha:** bare `scp` in
the session sandbox can silently degrade to a mangled local `cp` — ship files
with `cat file | ssh host 'cat > path'` (or scp inside a script), and **verify
the remote file by checksum before running anything that depends on it** (an
unverified failed copy mislabeled ~130 results here before being caught).

## Unnumbered cycle record (RM2 recall delta / classifier blind-spot run, 2026-07-03; backfilled 2026-08-04)

Instance `rm2-recall-delta`, ~1 h, <$1. Ran the RM2 file-level-vs-project-level
recall delta at n=50 and closed ISSUES #26: pooled file-level recall 98/108
type occurrences = 90.7% [83.8, 94.9]; false-NONE 1/50, fails safe post-flip.
Followed this runbook's pattern (own bundle, probe, run, teardown) but its
record was written only into ISSUES #26; this entry backfills the gap
(session: "RM2 file-level vs project-level recall delta", 2026-07-03).
**Ordinal note (ruled 2026-08-04):** this runbook's cycle ordinals are
authoritative. ISSUES #26's self-label "4th CLI-DEPLOY cycle" predates the
Fourth cycle record below and is superseded wording. Eight runs total: seven
numbered cycles plus this one.

## Fourth cycle record (Phase-2b detection oracle, 2026-07-04/05)

Instance `i-06e7962b22298f12a` (`phase2b-detect`), key `p2key` (recreated), SG
`sg-0d8569b3ed88570c0`. Repo `0b28c6c`, `DRIVER_COMMIT=f964354`. Shipped
`repo.tar.gz` + `scenarios_phase2b.tar.gz` (COPYFILE_DISABLE=1, zero
AppleDouble) + reused P4 `images.tar.gz`; all `cat|ssh` with checksum
verification. Live probes (mergiraf/RM2/joern) before scoring. G1 10/10 in
both arms; dev arm 83 files ≈ 42 min, remerge arm ≈ 1.7 h (~80–83 s/merge,
5 detectors). Results → `reports_detection/phase2b/{dev,remerge}/`. Torn down
2026-07-05 + verified empty (instances and volumes both blank). **Cost ~$10,
of which ~$8 was overnight idle — a lesson, see below.** Compute itself ≈ $2
as estimated.

**Gotcha (the overnight idle):** a long-lived `ssh 'while pgrep …; do sleep;
done'` watcher dies silently with a broken pipe (`exit 255`) when sshd drops
the connection — the "run finished" notification never fires and the instance
idles until someone looks. Fixes for next cycle: (1) `-o ServerAliveInterval=30
-o ServerAliveCountMax=4` on every long-poll ssh; (2) never rely on a single
watcher — schedule a fallback same-day check; (3) `pgrep -f <pattern>` matches
its *own* command line when the pattern appears in it (false "STILL_RUNNING") —
use `pgrep -f` patterns that don't occur in the checking command, or
`pgrep -x`.

## Fifth cycle record (S-D5 detector evaluation, 2026-07-16..18)

Instance `i-0a3193cadee961264` (`sd5-detector-eval`), SG `sg-0abb309205f914c40`,
key `p2key` (recreated). Repo `0e4b35b` (+`027ec4c` fix mid-cycle),
`DRIVER_COMMIT=732d8ff`. New scripts: `bundle_sd5.sh` / `provision_sd5.sh` /
`run_sd5.sh`. **Images built on-instance** (standing rule; mergiraf compiles
from source ~10 min) + live probes; env validated by per-process smoke gates
AND a known-answer re-score of 3 tune merges against the committed GD2(iii)
cache (42/42 verdicts) — the detector-cycle analogue of the canonical-table
rule. Ran the full S-D5 two-arm battery (heldout/derivation/evalctl/spgroup,
1,751 files, 8 lane-execs/file). Torn down + verified empty 2026-07-18.
**~40.3 h ≈ $17–18 — over the ~$5–10 planning figure for structural reasons**
(the composition is 8 lane executions × 1,751 files, about 6× the Stage-C lane executions, and Joern-bound; 4
shards saturate the 8 vCPUs, so parallelism could not be widened). No idle
loss (STATUS-file + 3-min local poller instead of a long-lived remote watcher).

**Gotchas added:** (1) static sharding by merge-index balances counts, not
work — one evalctl shard drew 41% of the files; fix mid-run by *seeded
half-shard surgery* ({i≡K mod N} = {i≡K mod 2N} ∪ {i≡K+N mod 2N}, caches
seeded from the parent shard so nothing recomputes) — or use a work-queue
from the start. (2) zsh: `$VAR` does NOT word-split (a transfer loop
silently no-ops) but `$(...)` does. (3) Per-file `cat|ssh` of ~50 MB of
artifacts times out — tar the directory remotely, pull ONE stream, compare
ONE sha256. (4) A local re-score that can't see a population's scenario dir
can silently overwrite pulled artifacts with a smaller denominator — treat
the instance-produced score as authoritative and guard the scorer.

## Seventh cycle record (S-D8 whole-driver flag-pair, 2026-07-22..23)

(The sixth cycle — S-D7 Stage-C rerun, `i-01b7db6337b2bd523`, eu-central-1,
~9.5 h ≈ $4 — is recorded in ISSUES #31's S-D7 summary.)

**First cross-region cycle:** launched in **eu-north-1** to run truly parallel
with S-D7 (the 8-vCPU On-Demand Standard quota is **per region** — a second
region gives concurrency with zero shared resources; also c7i is slightly
cheaper there). Resources: instance `i-0006f73fee2019c40` (`sd8-flagon`,
c7i.2xlarge, 80 GB gp3), SG `sg-02be4b932de464e8f` (`sd8-sg`), key
`p2key-sd8` (public half of `~/.ssh/p2key.pem` imported via
`aws ec2 import-key-pair` — key pairs are per-region). Scripts
`bundle_sd8.sh` / `provision_sd8.sh` / `run_sd8.sh`; repo `50d2754`,
`DRIVER_COMMIT=732d8ff`. Image split per Ali's ruling: pinned images built
on-instance, unpinned jdime/mastery docker-saved (arch-verified amd64) and
shipped `cat|ssh` + sha256. Env validated by the canonical six-tool table
(36/36 exact, Spork 32/11) AND a pre-registered derived-target
reconciliation of the flag-OFF arm (1784 = predicted, to the digit).
~23.5 h ≈ $8.5, teardown verified empty (instances + volumes).

**Gotchas added:** (1) first `run-instances` in a fresh region returns
`PendingVerification` even on a verified account — cleared in ~10 min on a
10-min retry loop; key + SG persist, so just retry. (2) A residential
public IP can ROTATE mid-cycle — the SG's `/32` ingress then hard-blocks
every poll (looks exactly like a dead instance). Check
`describe-instance-status` out-of-band FIRST (ours was `ok/ok`), then
re-authorize the new IP and revoke the old rule; the detached `nohup`
battery is unaffected. Add "my IP still matches the SG?" to the long-poll
debugging checklist before suspecting the instance.

## Finding: native x86_64 did NOT speed up the run

Per-file time on `c7i.2xlarge` (native amd64) was **~87 s/file — the same as
local Apple Silicon (~80 s)**. The driver is **Joern-bound** (JVM CPG
construction per file), which was already native on the Mac; the `linux/amd64`
Docker emulation we set out to escape is a small fraction of each merge, not the
dominant cost. So the full run is **~20–22 h regardless of arch**.

Implication: **AWS's value here is "off the laptop, unattended" — not speed.**
To actually shorten wall-clock, parallelism (`--shard`/process pool across
vCPUs) is the lever, not a faster/native instance. Sequential was chosen for
this run (no harness change).
