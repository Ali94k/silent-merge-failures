"""Materialize the spgroup mergedataset labeled benchmark into MergeScenario JSONs.

Phase-2b of the detection validation (research/outputs/phase2b-recon.md): maps
`spgroup/mergedataset` (pinned clone, see recon doc) onto the comparator's
MergeScenario JSON shape so tools/detect_validate.py can score the driver's
detectors against externally labeled semantic conflicts.

Unit = unique (merge commit, class) from semantic-conflicts/
sample-semantic-conflicts.csv; label = any row Yes -> positive, else No ->
control; rows labeled "-" (never manually analyzed) are excluded. Source
quadruples ship in-dataset as {base,left,right,merge}.java under either
`<project>/<sha>/source/...` or `studies/.../files/...`; merge.java is the
developer's merge commit content and lands in `developer_resolution`.

merge_id is set to scenario_id ON PURPOSE: the benchmark's labels are
per-unit, so each unit must stay its own aggregation row in detect_validate
(no any-file-flag collapsing across a shared real merge commit).

Category starts as "unmapped" (positives) / "none" (controls); an optional
--category-map CSV (columns: commit,class,category) stamps the adjudicated
taxonomy category (draft frozen BEFORE any detector run — recon doc protocol).

Usage:
    .venv/bin/python tools/materialize_phase2b.py ../workspace/phase2b-mergedataset
    .venv/bin/python tools/materialize_phase2b.py ../workspace/phase2b-mergedataset \
        --category-map reports_detection/phase2b/category_mapping.csv
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # merge-tool-comparison/
CSV_REL = "semantic-conflicts/sample-semantic-conflicts.csv"
DEFAULT_POS = "data/scenarios_phase2b"
DEFAULT_CTL = "data/scenarios_phase2b_ctl"
QUAD = ("base", "left", "right", "merge")


def load_labels(dataset: Path) -> list[dict]:
    """CSV rows with whitespace-padded headers/values stripped."""
    with open(dataset / CSV_REL, newline="") as fh:
        rows = list(csv.DictReader(fh))
    return [{(k or "").strip(): (v.strip() if isinstance(v, str) else v)
             for k, v in r.items()} for r in rows]


def index_quadruples(dataset: Path) -> dict[tuple[str, str], Path]:
    """(merge_sha, class-leaf-dir-name) -> quadruple dir, for every complete
    {base,left,right,merge}.java directory anywhere in the dataset."""
    out: dict[tuple[str, str], Path] = {}
    for b in glob.glob(str(dataset / "**" / "base.java"), recursive=True):
        d = Path(b).parent
        if not all((d / f"{f}.java").exists() for f in QUAD):
            continue
        sha = next((p for p in d.parts if len(p) == 40), None)
        if sha:
            out.setdefault((sha, d.name), d)
    return out


def unit_file_path(quad_dir: Path) -> str:
    """Repo-relative java path for the unit: `<pkg dirs>/<Leaf>.java` after the
    source/ (main tree) or files/<project>/<sha>/ (studies tree) marker."""
    parts = quad_dir.parts
    for marker in ("source", "files"):
        if marker in parts:
            i = parts.index(marker)
            rel = parts[i + 1:] if marker == "source" else parts[i + 3:]
            if rel:
                return "/".join(rel) + ".java"
    return quad_dir.name + ".java"


def load_category_map(path: Path | None) -> dict[tuple[str, str], str]:
    if path is None:
        return {}
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    return {(r["commit"].strip(), r["class"].strip()): r["category"].strip()
            for r in rows}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dataset", help="path to the mergedataset clone")
    ap.add_argument("--out-pos", default=DEFAULT_POS)
    ap.add_argument("--out-ctl", default=DEFAULT_CTL)
    ap.add_argument("--category-map", default=None,
                    help="CSV commit,class,category stamping adjudicated categories")
    args = ap.parse_args()

    dataset = Path(args.dataset).resolve()
    if not (dataset / CSV_REL).exists():
        sys.exit(f"ABORT: {dataset / CSV_REL} not found — wrong --dataset path?")
    dataset_commit = "unknown"
    head = dataset / ".git" / "HEAD"
    if head.exists():
        ref = head.read_text().strip()
        if ref.startswith("ref: "):
            ref_file = dataset / ".git" / ref[5:]
            dataset_commit = ref_file.read_text().strip() if ref_file.exists() else ref
        else:
            dataset_commit = ref

    rows = load_labels(dataset)
    quads = index_quadruples(dataset)
    cat_map = load_category_map(Path(args.category_map) if args.category_map else None)

    # dedupe rows -> file-level units; keep declaration granularity as metadata
    units: dict[tuple[str, str], dict] = {}
    for r in rows:
        key = (r["Commit"], r["Class"])
        u = units.setdefault(key, {"labels": [], "declarations": [], "studies": []})
        u["labels"].append(r["Locally Observable Interference"])
        u["declarations"].append(r["Declaration"])
        u["studies"].append(r["Sample"])

    out_pos = ROOT / args.out_pos
    out_ctl = ROOT / args.out_ctl
    out_pos.mkdir(parents=True, exist_ok=True)
    out_ctl.mkdir(parents=True, exist_ok=True)

    stats = Counter()
    missing: list[str] = []
    for (sha, cls), u in sorted(units.items()):
        label = "Yes" if "Yes" in u["labels"] else ("No" if "No" in u["labels"] else "-")
        if label == "-":
            stats["excluded_unmarked"] += 1
            continue
        leaf = cls.split(".")[-1].split("$")[0]
        quad_dir = quads.get((sha, leaf))
        if quad_dir is None:
            stats[f"missing_{label}"] += 1
            missing.append(f"{label} {sha[:12]} {cls}")
            continue
        project = quad_dir.relative_to(dataset).parts[0]
        if project == "studies":  # studies/.../files/<project>/<sha>/...
            parts = quad_dir.parts
            project = parts[parts.index("files") + 1]
        scenario_id = f"{project}__{sha[:10]}__{cls}"
        contents = {f: (quad_dir / f"{f}.java").read_text(encoding="utf-8", errors="replace")
                    for f in QUAD}
        scn = {
            "scenario_id": scenario_id,
            "repo_name": project,
            "merge_commit": sha,
            "file_path": unit_file_path(quad_dir),
            "base_content": contents["base"],
            "ours_content": contents["left"],
            "theirs_content": contents["right"],
            "developer_resolution": contents["merge"],
            "category": cat_map.get((sha, cls),
                                    "unmapped" if label == "Yes" else "none"),
            "refactorings": {},
            "merge_id": scenario_id,  # per-unit aggregation, see module docstring
            "phase2b": {
                "label": label,
                "class": cls,
                "declarations": u["declarations"],
                "studies": sorted(set(u["studies"])),
                "dataset_commit": dataset_commit,
                "quad_dir": str(quad_dir.relative_to(dataset)),
            },
        }
        out_dir = out_pos if label == "Yes" else out_ctl
        (out_dir / f"{scenario_id.replace('/', '_')}.json").write_text(
            json.dumps(scn, indent=1))
        stats[f"written_{label}"] += 1

    print(f"dataset commit: {dataset_commit}")
    print(f"positives -> {out_pos}: {stats['written_Yes']}")
    print(f"controls  -> {out_ctl}: {stats['written_No']}")
    print(f"excluded '-' rows (never analyzed): {stats['excluded_unmarked']}")
    if missing:
        print(f"NOT materializable ({len(missing)}):")
        for m in missing:
            print(f"  {m}")
    if cat_map:
        unmapped = [f for f in glob.glob(str(out_pos / "*.json"))
                    if json.load(open(f))["category"] == "unmapped"]
        print(f"positives still unmapped after --category-map: {len(unmapped)}")


if __name__ == "__main__":
    main()
