import glob
import os
import pytest
from strategies.joern_strategies.taint_check import JoernDataFlowInterferenceStrategy

# Category #3 — Data Flow Interference (Stale Read).
# The base/ours/theirs.java fixtures in data/dfi_stale_read/ document the
# scenario (one side clears `pendingTasks`, the other iterates it). The
# single-file tests analyze the merged state directly; the 3-way tests exercise
# the Phase-2 differential (merge-induced) refinement.

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "dfi_stale_read")
TEMP_MERGED = os.path.join(DATA_DIR, "temp_merged.java")

# Merged result of base + ours (clear) + theirs (iterate): the collection is
# cleared and then iterated with nothing added back -> iterates an empty list.
STALE_MERGE = """public class TaskManager {
    private java.util.List<String> pendingTasks = new java.util.ArrayList<>();

    public void run() {
        pendingTasks.add("init");
        pendingTasks.clear();
        for (String task : pendingTasks) {
            System.out.println("Processing " + task);
        }
    }
}
"""

# Same shape but repopulated after the clear -> the read is no longer stale.
CLEAN_MERGE = """public class TaskManager {
    private java.util.List<String> pendingTasks = new java.util.ArrayList<>();

    public void run() {
        pendingTasks.add("init");
        pendingTasks.clear();
        pendingTasks.add("task1");
        for (String task : pendingTasks) {
            System.out.println("Processing " + task);
        }
    }
}
"""

# 3-way: ours adds the reset, theirs adds the read; neither parent alone is stale.
OURS_CLEAR_ONLY = """public class TaskManager {
    private java.util.List<String> pendingTasks = new java.util.ArrayList<>();

    public void run() {
        pendingTasks.add("init");
        pendingTasks.clear();
    }
}
"""

THEIRS_READ_ONLY = """public class TaskManager {
    private java.util.List<String> pendingTasks = new java.util.ArrayList<>();

    public void run() {
        pendingTasks.add("init");
        for (String task : pendingTasks) {
            System.out.println("Processing " + task);
        }
    }
}
"""

# 3-way: the stale read already exists in ours; theirs only adds an unrelated
# method. The merge did not introduce the stale read, so it must NOT be flagged.
OURS_ALREADY_STALE = STALE_MERGE

THEIRS_UNRELATED = """public class TaskManager {
    private java.util.List<String> pendingTasks = new java.util.ArrayList<>();

    public void run() {
        pendingTasks.add("init");
    }

    public int count() {
        return pendingTasks.size();
    }
}
"""

MERGED_PREEXISTING = """public class TaskManager {
    private java.util.List<String> pendingTasks = new java.util.ArrayList<>();

    public void run() {
        pendingTasks.add("init");
        pendingTasks.clear();
        for (String task : pendingTasks) {
            System.out.println("Processing " + task);
        }
    }

    public int count() {
        return pendingTasks.size();
    }
}
"""


@pytest.fixture
def cleanup():
    os.makedirs(DATA_DIR, exist_ok=True)
    yield
    for p in glob.glob(TEMP_MERGED + "*"):
        os.remove(p)


def _analyze(merged, **kwargs):
    with open(TEMP_MERGED, "w") as f:
        f.write(merged)
    return JoernDataFlowInterferenceStrategy().analyze(TEMP_MERGED, **kwargs)


def test_detects_stale_read(cleanup):
    """Single-file: a cleared-then-iterated collection must be flagged."""
    result = _analyze(STALE_MERGE)
    assert not result.is_clean, "Strategy failed to detect the stale read."
    assert any("stale read" in issue.message.lower() for issue in result.issues)


def test_ignores_repopulated_collection(cleanup):
    """Single-file: a clear followed by repopulation before the read is clean."""
    result = _analyze(CLEAN_MERGE)
    assert result.is_clean is True, "Strategy falsely flagged a repopulated collection."


def test_flags_merge_induced_stale_read(cleanup):
    """3-way: reset from ours + read from theirs -> merge introduced it -> flag."""
    result = _analyze(STALE_MERGE,
                      ours_content=OURS_CLEAR_ONLY,
                      theirs_content=THEIRS_READ_ONLY)
    assert not result.is_clean, "Strategy failed to flag the merge-induced stale read."
    assert any("stale read" in issue.message.lower() for issue in result.issues)


def test_ignores_preexisting_stale_read(cleanup):
    """3-way: the stale read already existed in ours -> not merge-induced -> clean."""
    result = _analyze(MERGED_PREEXISTING,
                      ours_content=OURS_ALREADY_STALE,
                      theirs_content=THEIRS_UNRELATED)
    assert result.is_clean is True, "Strategy flagged a pre-existing (not merge-induced) stale read."
