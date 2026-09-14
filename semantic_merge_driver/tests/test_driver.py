import pytest
import shutil
import os
from core.backends.git_merge_file_backend import GitMergeFileBackend
from core.driver import SemanticMergeDriver
from core.interfaces import AnalysisResult, Issue, MergeStrategy

# Paths to our test data
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
ANCESTOR = os.path.join(DATA_DIR, 'ancestor.py')
OURS = os.path.join(DATA_DIR, 'ours.py')
THEIRS = os.path.join(DATA_DIR, 'theirs.py')

# Temporary paths for execution (so we don't modify the originals)
TEMP_ANCESTOR = os.path.join(DATA_DIR, 'temp_ancestor.py')
TEMP_OURS = os.path.join(DATA_DIR, 'temp_ours.py')
TEMP_THEIRS = os.path.join(DATA_DIR, 'temp_theirs.py')

@pytest.fixture
def setup_files():
    """Copy test files to temp locations before each test."""
    shutil.copy(ANCESTOR, TEMP_ANCESTOR)
    shutil.copy(OURS, TEMP_OURS)
    shutil.copy(THEIRS, TEMP_THEIRS)
    yield
    # Cleanup
    for f in [TEMP_ANCESTOR, TEMP_OURS, TEMP_THEIRS]:
        if os.path.exists(f):
            os.remove(f)

# --- MOCK STRATEGIES ---
class MockCleanStrategy(MergeStrategy):
    """A mock strategy that always passes."""
    @property
    def name(self): return "MockClean"
    def analyze(self, file_path, base_content=None, ours_content=None, theirs_content=None):
        return AnalysisResult(is_clean=True, issues=[])

class MockBuggyStrategy(MergeStrategy):
    """A mock strategy that always finds a bug."""
    @property
    def name(self): return "MockBuggy"
    def analyze(self, file_path, base_content=None, ours_content=None, theirs_content=None):
        return AnalysisResult(is_clean=False, issues=[
            Issue(1, "CRITICAL", "Mock Bug Found", "MockBuggy")
        ])

# --- TESTS ---

def test_driver_clean_merge(setup_files, monkeypatch):
    """
    Test that the driver returns 0 (Success) when:
    1. Text merge is successful (No conflicts)
    2. Strategy finds no bugs
    """
    driver = SemanticMergeDriver(backend=GitMergeFileBackend())
    
    # FIX: Overwrite 'theirs' to match 'ours' so git merge-file returns 0 (Clean merge)
    shutil.copy(TEMP_OURS, TEMP_THEIRS)
    
    # Override loader to return our Clean Strategy
    monkeypatch.setattr(driver.loader, 'load_strategies', lambda: [MockCleanStrategy()])
    
    result = driver.run_merge(TEMP_ANCESTOR, TEMP_OURS, TEMP_THEIRS)
    assert result == 0

def test_driver_rejects_bug(setup_files, monkeypatch):
    """
    Test that the driver returns 1 (Fail) when a strategy finds a bug,
    even if the text merge itself was successful.
    """
    driver = SemanticMergeDriver(backend=GitMergeFileBackend())
    
    # Override loader to return our Buggy Strategy
    monkeypatch.setattr(driver.loader, 'load_strategies', lambda: [MockBuggyStrategy()])
    
    result = driver.run_merge(TEMP_ANCESTOR, TEMP_OURS, TEMP_THEIRS)
    assert result == 1

def test_real_git_merge_file_execution(setup_files):
    """
    Integration Test: Verify that 'git merge-file' is actually called 
    and modifies TEMP_OURS on disk.
    """
    # Use empty strategy list to isolate git plumbing
    driver = SemanticMergeDriver(backend=GitMergeFileBackend(), strategies=[])
    
    # Before merge, TEMP_OURS should look like ours.py
    with open(TEMP_OURS) as f: origin_content = f.read()
    
    driver.run_merge(TEMP_ANCESTOR, TEMP_OURS, TEMP_THEIRS)
    
    # After merge, TEMP_OURS should contain the merged code (likely from theirs.py)
    with open(TEMP_OURS) as f: new_content = f.read()
    
    assert origin_content != new_content
    # The merged file should contain the code from 'theirs.py' (the infinite loop)
    assert "while True:" in new_content