"""Language enum + file-extension-based detection.

Consumed by the R4b dispatch skeleton (planned) and by per-language router
arms (W5: any → Weave for MIGRATE_DECL; S2: Java-only → Spork for INTRA_BODY).
The classifier itself is language-agnostic; this module exists so routers can
make per-language decisions without re-parsing extensions inline.

UNKNOWN is returned for unrecognized extensions (including missing extension
or a leading dot like `.gitignore`). Callers treat UNKNOWN as "do not apply
language-specialised routing" — fall through to the language-agnostic default.
"""
from enum import Enum
from pathlib import Path
from typing import Union


class Language(str, Enum):
    JAVA = "java"
    KOTLIN = "kotlin"
    SCALA = "scala"
    PYTHON = "python"
    UNKNOWN = "unknown"


_EXTENSION_TO_LANGUAGE = {
    ".java": Language.JAVA,
    ".kt": Language.KOTLIN,
    ".kts": Language.KOTLIN,
    ".scala": Language.SCALA,
    ".sc": Language.SCALA,
    ".py": Language.PYTHON,
}


def language_of(path: Union[str, Path]) -> Language:
    """Map a file path to its Language enum by extension. UNKNOWN if unmapped."""
    return _EXTENSION_TO_LANGUAGE.get(Path(path).suffix.lower(), Language.UNKNOWN)
