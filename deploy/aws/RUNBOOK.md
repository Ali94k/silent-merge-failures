# P2 Whole-Driver Run on AWS — Runbook

Run the ~20 h P2 evaluation **unattended on EC2** so it's off your laptop. The
job runs on the instance independent of your laptop being on/awake/online; you
SSH back later to collect results. The harness is **resumable**, so an
interruption (dropped SSH, reboot, spot reclaim) loses at most the in-flight file.

**What runs:** `tools/whole_driver_eval.py` (all 5 configs by default). The three
no-Docker configs (`bare-git`, `bare-mergiraf`, `driver-mergiraf`) score
instantly from the committed Stage-C cache; `driver-git` + `driver-auto` are the
~20 h of real compute. Native x86_64 → no Rosetta emulation → this also yields
the **honest native-amd64 latency** the thesis needs.

---

## ⚠️ First-timer safeguards (do these or regret it)

- **Set an AWS Budget alarm (~$20) before launching anything.** Billing →
  Budgets → Create budget → Cost budget → $20 → email alert at 80%/100%. This is
  the #1 protection against a forgotten-running-instance bill.
- **Terminate (not just stop) the instance when done** (Step 7). Stopped still
  bills EBS; terminated + volume-deleted = $0.
- **Use a paid compute instance, not free tier.** `t2.micro` cannot run Joern.
- Cost reality: `c7i.2xlarge` ≈ $0.36/hr → a ~20 h run ≈ **$7–8**. (Spot ~⅓.)

---

## Step 0 — prerequisites

- AWS account created (credit-card + phone verification).
- Budget alarm set (above).
- An SSH key pair you control (created at launch, Step 2).

## Step 1 — bundle artifacts (LOCAL, repo root)

```bash
bash deploy/aws/bundle.sh
# → deploy/dist/{repo,scenarios,images}.tar.gz  (+ sha256)
```
`images.tar.gz` is several GB (the 5 amd64 images). `repo`/`scenarios` are small.

## Step 2 — launch the instance (AWS console)

EC2 → Launch instance:
- **Name:** `p2-whole-driver`
- **AMI:** Ubuntu Server 24.04 LTS (x86_64) — confirm **64-bit (x86)**, *not* Arm.
- **Instance type:** `c7i.2xlarge` (8 vCPU / 16 GB). *Not Graviton/arm64* — the
  images are amd64 and would re-emulate.
  - ⚠️ If launch is blocked by a vCPU quota on a new account: Service Quotas →
    EC2 → "Running On-Demand Standard instances" → request ≥ 8. Can take hours;
    do it early. (Or temporarily use a smaller type within quota.)
- **Key pair:** create new → download `p2key.pem` → `chmod 600 p2key.pem`.
- **Network / security group:** allow **SSH (22) from My IP** only.
- **Storage:** change root EBS to **80 GB gp3** (8 GB default is too small).
- Launch, then copy the instance's **Public IPv4 DNS** (the `HOST` below).

## Step 3 — transfer artifacts

```bash
KEY=p2key.pem; HOST=<public-dns>
scp -i $KEY deploy/dist/repo.tar.gz deploy/dist/scenarios.tar.gz \
            deploy/aws/provision.sh ubuntu@$HOST:~
# images.tar.gz is the big one — if scp is slow/flaky, use S3 instead:
#   aws s3 cp deploy/dist/images.tar.gz s3://YOUR-BUCKET/   (from laptop)
#   then on the instance:  aws s3 cp s3://YOUR-BUCKET/images.tar.gz ~
scp -i $KEY deploy/dist/images.tar.gz ubuntu@$HOST:~
```

## Step 4 — provision (ON the instance)

```bash
ssh -i $KEY ubuntu@$HOST
bash provision.sh            # ~15–25 min: apt, docker load, Joern, venv
exit                         # log out so the docker group takes effect
ssh -i $KEY ubuntu@$HOST     # back in — docker now works without sudo
# sanity:
docker images | grep merge-tools     # expect 5
joern --version | tail -1            # expect 4.0.436
```

## Step 5 — run unattended

Run inside **tmux** so it survives disconnect; then you can close your laptop.

```bash
tmux new -s p2
cd ~/thesis-projects/merge-tool-comparison
nohup .venv/bin/python tools/whole_driver_eval.py \
      > reports_whole_driver/full_run.log 2>&1 &
echo "PID $!"
tail -f reports_whole_driver/full_run.log    # watch a bit, then…
# detach tmux: press  Ctrl-b  then  d
```
Now disconnect / close the laptop. Re-attach anytime: `ssh …` then `tmux attach -t p2`.
Resumable: if it ever dies, re-run the same command — it continues from cache.

## Step 6 — collect results (from your laptop, when done)

The run finishing prints the report to `full_run.log` and writes
`reports_whole_driver/{summary.txt,scenarios.csv,raw_results.json}`.

```bash
scp -i $KEY \
  ubuntu@$HOST:~/thesis-projects/merge-tool-comparison/reports_whole_driver/{summary.txt,scenarios.csv,full_run.log} \
  merge-tool-comparison/reports_whole_driver/
# raw_results.json too if you want the full cache locally (large):
scp -i $KEY ubuntu@$HOST:~/.../reports_whole_driver/raw_results.json merge-tool-comparison/reports_whole_driver/
```
Then I'll write `FINDINGS.md`, update STATUS/THREATS/ISSUES, and commit.

## Step 7 — teardown (don't skip)

EC2 → Instances → select → **Instance state → Terminate**. Confirm it's
`terminated`, and that its EBS volume is gone (Volumes → none `available`).
Budget alarm stays as a safety net.

---

## Troubleshooting

- **`docker` permission denied** → you didn't re-login after provision; run
  `newgrp docker` or log out/in.
- **Joern errors / `joern-parse: not found`** → `source ~/.bashrc`; confirm
  `~/bin/joern/joern-cli/joern-parse` exists and JDK 21 is installed.
- **Cross-check mismatch** (`driver-mergiraf` R2 ≠ 12/164) → the Stage-C
  `raw_results.json` didn't ship; re-extract `repo.tar.gz` (it's committed, so
  it must be in the archive).
- **gjf/normalization differences** → ensure `merge-tools/google-java-format:1.22.0`
  loaded and Docker is up; the scoring oracle needs it.
- **Run slower than ~82 s/file** → you're on Arm/Graviton (emulating) or a
  too-small instance; verify x86_64 + `c7i`-class.
- **SSH drops kill the job** → you didn't use tmux/nohup; always both.
