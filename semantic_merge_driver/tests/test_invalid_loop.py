import pytest
import shutil
import os
import subprocess
from core.driver import SemanticMergeDriver
# Assuming the strategy is saved in this location
from strategies.joern_strategies.invalid_loop_bounds import JoernInvalidLoopBoundsStrategy

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'loop_bounds')
ANCESTOR = os.path.join(DATA_DIR, 'base.java')
OURS = os.path.join(DATA_DIR, 'ours.java')
THEIRS = os.path.join(DATA_DIR, 'theirs.java')

# Temp paths for test execution
TEMP_MERGED = os.path.join(DATA_DIR, 'temp_merged.java')

@pytest.fixture
def setup_files():
    # Create the data directory if it doesn't exist (for this example)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # In a real run, we would copy files here. 
    # For this test, we assume the Java files above exist in DATA_DIR.
    yield
    # Cleanup
    if os.path.exists(TEMP_MERGED):
        os.remove(TEMP_MERGED)
    if os.path.exists(TEMP_MERGED + ".cpg.bin"): # Clean up Joern artifact
        os.remove(TEMP_MERGED + ".cpg.bin")

def test_detect_invalid_loop_bounds(setup_files):
    """
    Integration Test:
    1. Simulates a git merge that results in a loop where start > end.
    2. Runs the JoernInvalidLoopBoundsStrategy.
    3. Expects a FAILURE (Issue Detected).
    """
    
    # 1. Simulate the Text Merge
    # We manually create the 'merged' state where start=15 and end=10
    # This simulates what happens if git merge-file successfully merges the lines.
    with open(TEMP_MERGED, 'w') as f:
        f.write("""
public class BatchProcessor {
    public void processItems() {
        for (int i = 15; i < 10; i++) { 
            System.out.println(i);
        }
    }
}
        """)

    # 2. Initialize Strategy
    strategy = JoernInvalidLoopBoundsStrategy()
    
    # 3. Run Analysis
    print(f"Analyzing {TEMP_MERGED}...")
    result = strategy.analyze(TEMP_MERGED)
    
    # 4. Assertions
    # The strategy should return is_clean=False because 15 > 10
    if not result.is_clean:
        print("\nSUCCESS: Strategy correctly detected the issue!")
        for issue in result.issues:
            print(f"  - {issue.message} at line {issue.line_number}")
            assert "Start > End" in issue.message
    else:
        pytest.fail("FAILURE: Strategy failed to detect the invalid loop bounds.")

def test_ignore_valid_loop(setup_files):
    """
    Control Test:
    Ensures the strategy does NOT flag a correct loop (start < end).
    """
    # Create a valid file
    with open(TEMP_MERGED, 'w') as f:
        f.write("""
public class BatchProcessor {
    public void processItems() {
        for (int i = 0; i < 10; i++) { 
            System.out.println(i);
        }
    }
}
        """)

    strategy = JoernInvalidLoopBoundsStrategy()
    result = strategy.analyze(TEMP_MERGED)
    
    assert result.is_clean is True, "Strategy falsely flagged a valid loop!"