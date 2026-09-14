"""language_of() — file-extension-based Language enum mapping.

Plan acceptance: language_of(Path("Foo.java")) == Language.JAVA.
"""
from pathlib import Path

import pytest

from core.language_detect import Language, language_of


@pytest.mark.parametrize("path,expected", [
    ("Foo.java", Language.JAVA),
    ("/abs/path/com/example/Bar.java", Language.JAVA),
    (Path("Foo.java"), Language.JAVA),
    ("Foo.JAVA", Language.JAVA),
    ("App.kt", Language.KOTLIN),
    ("Build.kts", Language.KOTLIN),
    ("Main.scala", Language.SCALA),
    ("Toy.sc", Language.SCALA),
    ("script.py", Language.PYTHON),
    ("README.md", Language.UNKNOWN),
    ("noext", Language.UNKNOWN),
    (".gitignore", Language.UNKNOWN),
    ("archive.tar.gz", Language.UNKNOWN),
])
def test_language_of(path, expected):
    assert language_of(path) is expected
