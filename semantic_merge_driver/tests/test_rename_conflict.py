"""RM2RenameConflictStrategy — unit + image-gated integration tests.

Unit tests mock the subprocess.run call so no Docker is required. They cover:
- detection (stale caller of the renamed identifier),
- multi-rename and multi-caller cases,
- no-renames → clean,
- rename detected but no stale callers → clean,
- new-name callers don't false-positive,
- regex-boundary behaviour (qualified `obj.foo()` flagged; method-reference
  `Foo::foo` not flagged because it has no `(`),
- identifier extraction for Rename Method and Rename Class shapes,
- fail-closed paths: missing base_content, missing docker (FileNotFoundError),
  non-zero rc, malformed JSON, timeout, OSError on merged-file read.

The integration test invokes real Docker against
`merge-tools/refactoring-miner:2.4.0` on a toy Rename Method fixture; it
skips cleanly if Docker or the image isn't available.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from strategies.rm2_strategies import rename_conflict
from strategies.rm2_strategies.rename_conflict import (
    RM2_IMAGE,
    RM2RenameConflictStrategy,
    _extract_identifier,
)


# --- Helpers ---

def _rm2_payload(renames):
    """Build a fake RM2 JSON payload from a list of (rtype, old_sig, new_sig)."""
    refactorings = []
    for rtype, old_sig, new_sig in renames:
        refactorings.append({
            "type": rtype,
            "description": f"{rtype} {old_sig} renamed to {new_sig}",
            "leftSideLocations": [{
                "filePath": "Foo.java",
                "startLine": 1, "endLine": 1, "startColumn": 1, "endColumn": 1,
                "codeElementType": "METHOD_DECLARATION",
                "description": "original",
                "codeElement": old_sig,
            }],
            "rightSideLocations": [{
                "filePath": "Foo.java",
                "startLine": 1, "endLine": 1, "startColumn": 1, "endColumn": 1,
                "codeElementType": "METHOD_DECLARATION",
                "description": "renamed",
                "codeElement": new_sig,
            }],
        })
    return {"directories": {"left": "/data/left", "right": "/data/right"},
            "refactorings": refactorings}


def _ok_proc(stdout: str):
    return SimpleNamespace(returncode=0, stdout=stdout, stderr="")


def _bad_proc(rc: int, stderr: str = "boom"):
    return SimpleNamespace(returncode=rc, stdout="", stderr=stderr)


def _patch_subprocess(monkeypatch, factory):
    """Patch rename_conflict.subprocess.run with a callable returning a CompletedProcess-shaped object."""
    monkeypatch.setattr(rename_conflict.subprocess, "run", lambda *a, **k: factory())


def _write_merged(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "Foo.java"
    p.write_text(content, encoding="utf-8")
    return p


# --- Identifier extraction (no subprocess) ---

@pytest.mark.parametrize("rtype, code_element, expected", [
    # Verified shapes against merge-tools/refactoring-miner:2.4.0 (see
    # test_integration_rename_class_shape_probe below).
    ("Rename Method", "public oldName(a int, b int) : int", "oldName"),
    ("Rename Method", "private static foo() : void", "foo"),
    ("Rename Method", "doStuff(x int) : void", "doStuff"),
    # Rename Class real RM2 output is the FQN as one token:
    ("Rename Class", "com.example.OldName", "OldName"),
    ("Rename Class", "a.b.c.d.DeepClass", "DeepClass"),
    ("Rename Class", "OldName", "OldName"),  # unqualified, no package
])
def test_extract_identifier_well_formed(rtype, code_element, expected):
    refactoring = {
        "type": rtype,
        "leftSideLocations": [{"codeElement": code_element}],
    }
    assert _extract_identifier(refactoring, "leftSideLocations") == expected


def test_extract_identifier_missing_locations():
    assert _extract_identifier({"type": "Rename Method"}, "leftSideLocations") is None
    assert _extract_identifier({"leftSideLocations": []}, "leftSideLocations") is None
    assert _extract_identifier({"leftSideLocations": [{}]}, "leftSideLocations") is None


# --- Detection happy paths ---

def test_detects_stale_caller_of_renamed_method(tmp_path, monkeypatch):
    merged = _write_merged(tmp_path, """\
public class Foo {
    public int newName(int a, int b) { return a + b; }
    public int caller() { return oldName(1, 2); }
}
""")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([
        ("Rename Method", "public oldName(a int, b int) : int", "public newName(a int, b int) : int"),
    ]))))

    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base placeholder\n")

    assert not result.is_clean
    assert len(result.issues) == 1
    assert "oldName" in result.issues[0].message
    assert "newName" in result.issues[0].message
    assert result.issues[0].line_number == 3
    assert result.issues[0].severity == "CRITICAL"
    assert result.issues[0].strategy_name == "RM2RenameConflict"


def test_qualified_caller_is_flagged(tmp_path, monkeypatch):
    """`this.foo()` / `obj.foo()` should be caught by `\\bfoo\\s*\\(`."""
    merged = _write_merged(tmp_path, """\
class Foo {
    void bar() { this.oldName(1); other.oldName(2); }
}
""")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([
        ("Rename Method", "public oldName(a int) : void", "public newName(a int) : void"),
    ]))))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert not result.is_clean
    assert len(result.issues) == 1  # one line, both calls on it


def test_method_reference_is_not_flagged(tmp_path, monkeypatch):
    """`Foo::oldName` has no `(` and should not match."""
    merged = _write_merged(tmp_path, """\
class Foo {
    Runnable r = Foo::oldName;
}
""")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([
        ("Rename Method", "public oldName() : void", "public newName() : void"),
    ]))))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert result.is_clean


def test_multiple_callers_yield_multiple_issues(tmp_path, monkeypatch):
    merged = _write_merged(tmp_path, """\
class Foo {
    void a() { oldName(1); }
    void b() { oldName(2); }
    void c() { oldName(3); }
}
""")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([
        ("Rename Method", "public oldName(a int) : void", "public newName(a int) : void"),
    ]))))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert not result.is_clean
    assert len(result.issues) == 3
    assert [i.line_number for i in result.issues] == [2, 3, 4]


def test_multiple_renames_each_scanned(tmp_path, monkeypatch):
    merged = _write_merged(tmp_path, """\
class Foo {
    void a() { firstOld(); secondOld(); }
}
""")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([
        ("Rename Method", "public firstOld() : void", "public firstNew() : void"),
        ("Rename Method", "public secondOld() : void", "public secondNew() : void"),
    ]))))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert not result.is_clean
    assert len(result.issues) == 2


def test_no_renames_returns_clean(tmp_path, monkeypatch):
    merged = _write_merged(tmp_path, "class Foo { void m() { oldName(); } }\n")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([]))))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert result.is_clean
    assert result.issues == []


def test_rename_with_no_callers_returns_clean(tmp_path, monkeypatch):
    merged = _write_merged(tmp_path, """\
class Foo {
    public void newName() {}
    public void other() { newName(); }
}
""")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([
        ("Rename Method", "public oldName() : void", "public newName() : void"),
    ]))))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert result.is_clean


def test_non_rename_refactorings_ignored(tmp_path, monkeypatch):
    """Extract Method / Move Class etc. are not relevant to this strategy."""
    payload = {
        "refactorings": [
            {"type": "Extract Method",
             "leftSideLocations": [{"codeElement": "public extractedFrom() : void"}],
             "rightSideLocations": [{"codeElement": "public extractedTo() : void"}]},
        ],
    }
    merged = _write_merged(tmp_path, "class Foo { void m() { extractedFrom(); } }\n")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(payload)))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert result.is_clean


# --- Fail-closed paths ---

def test_missing_base_content_fails_closed(tmp_path):
    merged = _write_merged(tmp_path, "class Foo {}\n")
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content=None)
    assert not result.is_clean
    assert "inconclusive" in result.issues[0].message.lower()
    assert "base_content" in result.issues[0].message


def test_missing_merged_file_fails_closed(tmp_path):
    nonexistent = tmp_path / "does_not_exist.java"
    result = RM2RenameConflictStrategy().analyze(str(nonexistent), base_content="// base\n")
    assert not result.is_clean
    assert "inconclusive" in result.issues[0].message.lower()


def test_filenotfound_on_docker_fails_closed(tmp_path, monkeypatch):
    merged = _write_merged(tmp_path, "class Foo {}\n")

    def boom(*a, **k):
        raise FileNotFoundError("docker not on PATH")

    monkeypatch.setattr(rename_conflict.subprocess, "run", boom)
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert not result.is_clean
    assert "inconclusive" in result.issues[0].message.lower()


def test_nonzero_returncode_fails_closed(tmp_path, monkeypatch):
    merged = _write_merged(tmp_path, "class Foo {}\n")
    _patch_subprocess(monkeypatch, lambda: _bad_proc(rc=42, stderr="rm2 exploded"))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert not result.is_clean
    assert "inconclusive" in result.issues[0].message.lower()


def test_malformed_json_fails_closed(tmp_path, monkeypatch):
    merged = _write_merged(tmp_path, "class Foo {}\n")
    _patch_subprocess(monkeypatch, lambda: _ok_proc("not json at all"))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert not result.is_clean
    assert "inconclusive" in result.issues[0].message.lower()


def test_timeout_fails_closed(tmp_path, monkeypatch):
    merged = _write_merged(tmp_path, "class Foo {}\n")

    def timeout(*a, **k):
        raise subprocess.TimeoutExpired(cmd="docker run …", timeout=1)

    monkeypatch.setattr(rename_conflict.subprocess, "run", timeout)
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert not result.is_clean
    assert "inconclusive" in result.issues[0].message.lower()


# --- Image-gated integration ---

def _image_available() -> bool:
    try:
        proc = subprocess.run(
            ["docker", "image", "inspect", RM2_IMAGE],
            capture_output=True,
            timeout=10,
        )
        return proc.returncode == 0
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return False


@pytest.mark.skipif(
    not _image_available(),
    reason=f"Docker or {RM2_IMAGE} not available",
)
def test_integration_rename_method_with_stale_caller(tmp_path):
    base = """\
package com.example;
public class Foo {
    public int oldName(int a, int b) { return a + b; }
    public int caller() { return oldName(1, 2); }
}
"""
    merged = """\
package com.example;
public class Foo {
    public int newName(int a, int b) { return a + b; }
    public int caller() { return oldName(1, 2); }
}
"""
    merged_path = tmp_path / "Foo.java"
    merged_path.write_text(merged, encoding="utf-8")

    result = RM2RenameConflictStrategy().analyze(str(merged_path), base_content=base)

    assert not result.is_clean
    assert any("oldName" in i.message for i in result.issues)


# --- Image-gated Rename Class probe + end-to-end ---

@pytest.mark.skipif(
    not _image_available(),
    reason=f"Docker or {RM2_IMAGE} not available",
)
def test_integration_rename_class_shape_probe(tmp_path):
    """Verify RM2's actual codeElement shape for Rename Class.

    Originally the strategy assumed codeElement was the declaration string
    (`"public class OldName"`); the real RM2 2.4.0 output is the FQN as a
    single token (`"com.example.OldName"`). This probe pins that contract
    so a future RM2 upgrade that changes the shape doesn't go unnoticed.
    """
    import json
    import subprocess as sp

    base = """\
package com.example;
public class OldName {
    public int value() { return 42; }
}
"""
    merged_text = """\
package com.example;
public class NewName {
    public int value() { return 42; }
}
"""
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    left_dir.mkdir()
    right_dir.mkdir()
    (left_dir / "OldName.java").write_text(base, encoding="utf-8")
    (right_dir / "OldName.java").write_text(merged_text, encoding="utf-8")

    proc = sp.run(
        [
            "docker", "run", "--rm", "--platform", "linux/amd64",
            "-v", f"{left_dir}:/data/left:ro",
            "-v", f"{right_dir}:/data/right:ro",
            RM2_IMAGE,
            "/data/left", "/data/right",
        ],
        capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, f"RM2 rc={proc.returncode}: {proc.stderr}"
    payload = json.loads(proc.stdout)
    rename_classes = [r for r in payload.get("refactorings", []) if r.get("type") == "Rename Class"]
    assert rename_classes, "Expected at least one Rename Class"
    left_code = rename_classes[0]["leftSideLocations"][0]["codeElement"]
    right_code = rename_classes[0]["rightSideLocations"][0]["codeElement"]
    # Contract: FQN form (one token, dot-separated).
    assert "." in left_code, f"Expected FQN shape, got {left_code!r}"
    assert " " not in left_code, f"Expected single-token shape, got {left_code!r}"
    # Extractor must yield bare class name on whatever shape RM2 emits.
    assert _extract_identifier(rename_classes[0], "leftSideLocations") == "OldName"
    assert _extract_identifier(rename_classes[0], "rightSideLocations") == "NewName"


@pytest.mark.skipif(
    not _image_available(),
    reason=f"Docker or {RM2_IMAGE} not available",
)
def test_integration_rename_class_with_stale_constructor(tmp_path):
    """End-to-end: Rename Class + stale `new OldName()` survives in merged → flagged.

    Only constructor calls are caught by the regex `\\bOldName\\s*\\(` — see
    the module docstring's regex-caveat block. Type declarations, static-member
    access, and `extends`/`implements` are out of scope for the MVP.
    """
    base = """\
package com.example;
public class OldName {
    public int value() { return 42; }
    public static OldName factory() { return new OldName(); }
}
"""
    merged_text = """\
package com.example;
public class NewName {
    public int value() { return 42; }
    public static NewName factory() { return new OldName(); }
}
"""
    merged_path = tmp_path / "OldName.java"
    merged_path.write_text(merged_text, encoding="utf-8")

    result = RM2RenameConflictStrategy().analyze(str(merged_path), base_content=base)

    assert not result.is_clean, (
        f"Expected stale `new OldName()` to be flagged. is_clean={result.is_clean}, "
        f"issues={[(i.line_number, i.message) for i in result.issues]}"
    )
    assert any("OldName" in i.message for i in result.issues)


# --- v2 (Stage B): var-lane renames + per-branch differential mode ---

ERUDIKA_SHAPE_MERGED = """\
public class Aspect {
    public Object invoke(Invocation mi) {
        Method method = mi.getMethod();
        detectNestedInvocations(m);
        return invokeDAO(method, mi);
    }
}
"""


def test_extract_identifier_var_shape():
    ref = _rm2_payload([("Rename Variable", "count : int", "total : int")])["refactorings"][0]
    assert _extract_identifier(ref, "leftSideLocations") == "count"
    assert _extract_identifier(ref, "rightSideLocations") == "total"


def test_var_rename_with_stale_use_is_flagged(tmp_path, monkeypatch):
    """Erudika shape: local renamed m->method, stale `m` use survives."""
    merged = _write_merged(tmp_path, ERUDIKA_SHAPE_MERGED)
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([
        ("Rename Variable", "m : Method", "method : Method"),
    ]))))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert not result.is_clean
    assert any("variable/field" in i.message and "'m'" in i.message for i in result.issues)


def test_var_rename_suppressed_when_old_still_declared(tmp_path, monkeypatch):
    """Surviving declaration of the old name -> scope analysis needed -> not
    this strategy's call (JoernUnresolvedReference territory)."""
    merged = _write_merged(tmp_path, """\
public class J {
    void saveToFiles() {
        JSONArray outputList = initializeBookList();
        saveAsRawJsonFile(bookTitleList);
    }
    JSONArray initializeBookList() {
        JSONArray bookTitleList = new JSONArray();
        return bookTitleList;
    }
}
""")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([
        ("Rename Variable", "bookTitleList : JSONArray", "outputList : JSONArray"),
    ]))))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert result.is_clean is True


def test_var_rename_ignores_comment_and_string_mentions(tmp_path, monkeypatch):
    merged = _write_merged(tmp_path, """\
public class K {
    void run() {
        Method method = getMethod();
        // legacy variable m was renamed
        log("m");
        use(method);
    }
}
""")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([
        ("Rename Variable", "m : Method", "method : Method"),
    ]))))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert result.is_clean is True


def test_var_rename_ignores_same_named_method_call_sites(tmp_path, monkeypatch):
    """Post-fix defect 1 (Stage C R1 — aerospike/cloudfoundry shape): a renamed
    VARIABLE sharing its name with a METHOD must not flag that method's call
    sites — variables are never callable in Java."""
    merged = _write_merged(tmp_path, """\
public class A {
    private int timeoutMillis = defaults();
    int timeout() { return timeoutMillis; }
    void configure() {
        apply(timeout());
        apply(timeout ());
    }
}
""")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([
        ("Rename Variable", "timeout : int", "timeoutMillis : int"),
    ]))))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert result.is_clean is True, [i.message for i in result.issues]


def test_var_rename_javadoc_apostrophe_does_not_blind_decl_guard(tmp_path, monkeypatch):
    """Post-fix defect 2 (Stage C R1 — podam shape): apostrophes in Javadoc
    must not pair across lines as a bogus char literal that swallows the
    surviving declaration (which would blind the guard and misattribute
    lines). Pre-fix this flagged; post-fix the declaration survives stripping
    and the guard suppresses."""
    merged = _write_merged(tmp_path, """\
public class P {
    /** it's the type mapper */
    private Map mapType = init();
    /** don't remove */
    void use() {
        call(mapType);
    }
}
""")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([
        ("Rename Attribute", "mapType : Map", "typeMap : Map"),
    ]))))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert result.is_clean is True, [i.message for i in result.issues]


def test_var_rename_generics_wildcard_declaration_guards(tmp_path, monkeypatch):
    """Post-fix round 2 (podam shape): a declaration typed with generics
    wildcards — `Class<? extends Map<?, ?>> mapType = ...` — must trigger the
    declaration guard (`?` was missing from the type charclass)."""
    merged = _write_merged(tmp_path, """\
public class Q {
    void fill() {
        Class<? extends Map<?, ?>> mapType = resolve();
        use(mapType);
        if (SortedMap.class.isAssignableFrom(mapType)) { grow(mapType); }
    }
}
""")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([
        ("Rename Variable", "mapType : Class", "map : Class"),
    ]))))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert result.is_clean is True, [i.message for i in result.issues]


def test_var_rename_lambda_parameter_guards(tmp_path, monkeypatch):
    """Post-fix round 2 (cloudfoundry shape): a lambda parameter named like
    the renamed variable is a declaration — `(request, connection) -> ...`
    and `request -> ...` must suppress the var-lane scan."""
    merged = _write_merged(tmp_path, """\
public class R {
    HttpClient attach(HttpClient c, RequestLogger requestLogger) {
        return c.doAfterRequest((request, connection) -> requestLogger.request(request))
                .doOnEach(request -> requestLogger.request(request));
    }
}
""")
    _patch_subprocess(monkeypatch, lambda: _ok_proc(json.dumps(_rm2_payload([
        ("Rename Variable", "request : HttpClientRequest", "response : HttpClientRequest"),
    ]))))
    result = RM2RenameConflictStrategy().analyze(str(merged), base_content="// base\n")
    assert result.is_clean is True, [i.message for i in result.issues]


def _patch_rm2_renames(monkeypatch, by_right_text):
    """Patch _rm2_renames keyed on the right-side text; record calls."""
    calls = []

    def fake(self, left_content, right_text, basename):
        calls.append(right_text)
        return by_right_text.get(right_text, [])

    monkeypatch.setattr(RM2RenameConflictStrategy, "_rm2_renames", fake)
    return calls


def test_per_branch_rename_visible_only_in_parent_is_flagged(tmp_path, monkeypatch):
    """Rename intended by ours, half-applied by the merge: invisible to
    (base, merged) RM2 (mock returns nothing for it) but caught per-branch."""
    merged = _write_merged(tmp_path, ERUDIKA_SHAPE_MERGED)
    ours = "// ours: renamed m->method everywhere\n"
    theirs = "// theirs: added detectNestedInvocations(m)\n"
    calls = _patch_rm2_renames(monkeypatch, {ours: [("m", "method", "var")]})
    result = RM2RenameConflictStrategy().analyze(
        str(merged), base_content="// base\n", ours_content=ours, theirs_content=theirs)
    assert len(calls) == 3, "expected (base,merged) + (base,ours) + (base,theirs)"
    assert not result.is_clean
    assert any("'m'" in i.message for i in result.issues)


def test_per_branch_rename_wholly_dropped_by_merge_is_clean(tmp_path, monkeypatch):
    """Merge kept the other branch wholesale: old name only, name-consistent."""
    merged = _write_merged(tmp_path, """\
public class L {
    void run() {
        Method m = getMethod();
        use(m);
    }
}
""")
    ours = "// ours renamed m->method\n"
    _patch_rm2_renames(monkeypatch, {ours: [("m", "method", "var")]})
    result = RM2RenameConflictStrategy().analyze(
        str(merged), base_content="// base\n", ours_content=ours, theirs_content="// theirs\n")
    assert result.is_clean is True


def test_per_branch_rm2_failure_fails_closed(tmp_path, monkeypatch):
    merged = _write_merged(tmp_path, "class M {}\n")

    def fake(self, left_content, right_text, basename):
        return None if right_text == "// ours\n" else []

    monkeypatch.setattr(RM2RenameConflictStrategy, "_rm2_renames", fake)
    result = RM2RenameConflictStrategy().analyze(
        str(merged), base_content="// base\n", ours_content="// ours\n", theirs_content="// theirs\n")
    assert result.is_clean is False
    assert any("inconclusive" in i.message for i in result.issues)
