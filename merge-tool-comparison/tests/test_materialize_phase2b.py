"""tools/materialize_phase2b.py — spgroup mergedataset -> MergeScenario JSONs.

Builds a miniature fake dataset tree in tmp_path (CSV + source quadruples in
both layout variants) and checks unit dedup, "-" exclusion, label routing,
category stamping, and MergeScenario compatibility.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import materialize_phase2b as mp  # noqa: E402

from src.core.interfaces import MergeScenario  # noqa: E402

SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40

CSV_HEADER = ("Sample ,Locally Observable Interference ,Manually Analyzed ,"
              "Commit ,Project ,Class ,Declaration ,Build Manager ,"
              "Original Version ,Transformed Version ,"
              "Original Without Dependencies Version ,Additional Changes on Source Code")


def _quad(root: Path, *parts: str) -> None:
    d = root.joinpath(*parts)
    d.mkdir(parents=True)
    for f in mp.QUAD:
        (d / f"{f}.java").write_text(f"class {parts[-1]} {{ /* {f} */ }}\n")


@pytest.fixture()
def fake_dataset(tmp_path: Path) -> Path:
    ds = tmp_path / "mergedataset"
    rows = [
        # two declarations in the same class -> ONE unit, label any-Yes
        f"Leuson ,Yes ,Yes ,{SHA_A} ,https://github.com/x/projA ,com.example.Foo ,m1() ,Maven , , , ,No",
        f"Roberto ,No ,Yes ,{SHA_A} ,https://github.com/x/projA ,com.example.Foo ,m2() ,Maven , , , ,No",
        # control unit in the studies/ tree layout
        f"Roberto ,No ,Yes ,{SHA_B} ,https://github.com/x/projB ,org.demo.Bar ,run() ,Maven , , , ,No",
        # "-" (never analyzed) -> excluded
        f"Guilherme ,- ,No ,{SHA_C} ,https://github.com/x/projC ,org.demo.Baz ,z() ,Maven , , , ,No",
        # labeled but no quadruple on disk -> reported missing
        f"DeSouza ,No ,Yes ,{'d' * 40} ,https://github.com/x/projD ,org.demo.Gone ,g() ,Maven , , , ,No",
    ]
    csv_path = ds / mp.CSV_REL
    csv_path.parent.mkdir(parents=True)
    csv_path.write_text(CSV_HEADER + "\n" + "\n".join(rows) + "\n")
    _quad(ds, "projA", SHA_A, "source", "com", "example", "Foo")
    _quad(ds, "studies", "static-analysis-results", "x-without-dependencies",
          "files", "projB", SHA_B, "org", "demo", "Bar")
    _quad(ds, "projC", SHA_C, "source", "org", "demo", "Baz")
    return ds


def _run(ds: Path, out: Path, extra: list[str] | None = None, capsys=None):
    argv = ["materialize_phase2b.py", str(ds),
            "--out-pos", str(out / "pos"), "--out-ctl", str(out / "ctl")]
    old = sys.argv
    sys.argv = argv + (extra or [])
    try:
        mp.main()
    finally:
        sys.argv = old


def test_materialize_end_to_end(fake_dataset, tmp_path, capsys):
    _run(fake_dataset, tmp_path)
    out = capsys.readouterr().out
    pos = list((tmp_path / "pos").glob("*.json"))
    ctl = list((tmp_path / "ctl").glob("*.json"))
    assert len(pos) == 1 and len(ctl) == 1        # dedup + "-" excluded
    assert "excluded '-' rows (never analyzed): 1" in out
    assert "org.demo.Gone" in out                  # missing quadruple reported

    scn = json.loads(pos[0].read_text())
    assert scn["merge_commit"] == SHA_A
    assert scn["merge_id"] == scn["scenario_id"]   # per-unit aggregation
    assert scn["category"] == "unmapped"
    assert scn["ours_content"].strip() == "class Foo { /* left */ }"
    assert scn["theirs_content"].strip() == "class Foo { /* right */ }"
    assert scn["developer_resolution"].strip() == "class Foo { /* merge */ }"
    assert scn["file_path"] == "com/example/Foo.java"
    assert sorted(scn["phase2b"]["declarations"]) == ["m1()", "m2()"]
    assert scn["phase2b"]["label"] == "Yes"        # any-Yes wins over No

    # studies/ tree: repo name recovered from files/<project>, path after sha
    ctl_scn = json.loads(ctl[0].read_text())
    assert ctl_scn["repo_name"] == "projB"
    assert ctl_scn["file_path"] == "org/demo/Bar.java"
    assert ctl_scn["category"] == "none"

    # extra keys must not break the canonical loader
    ms = MergeScenario.from_dict(scn)
    assert ms.merge_commit == SHA_A


def test_category_map_stamps_positives(fake_dataset, tmp_path, capsys):
    cmap = tmp_path / "map.csv"
    cmap.write_text("commit,class,category\n"
                    f"{SHA_A},com.example.Foo,3-dfi-stale-read\n")
    _run(fake_dataset, tmp_path, ["--category-map", str(cmap)])
    scn = json.loads(next((tmp_path / "pos").glob("*.json")).read_text())
    assert scn["category"] == "3-dfi-stale-read"
    assert "still unmapped after --category-map: 0" in capsys.readouterr().out


def test_missing_dataset_aborts(tmp_path):
    with pytest.raises(SystemExit, match="not found"):
        _run(tmp_path / "nope", tmp_path)
