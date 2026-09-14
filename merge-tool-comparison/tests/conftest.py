import os

# Comparator unit tests assert behavior under the cheap whitespace-only
# normalization path. Disable both the google-java-format Docker roundtrip
# (Tier 2) and the tree-sitter AST normalize (Tier 3) by default so the suite
# stays Docker-free and parser-fast. Tests that exercise either tier opt in
# by setting the env var or monkeypatching.
os.environ.setdefault("MERGE_COMPARATOR_FORMATTER", "off")
os.environ.setdefault("MERGE_COMPARATOR_AST_NORMALIZE", "off")
