"""Scan project source files for credential-like strings that shouldn't be committed."""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# Extensions to scan
_SCAN_EXTS = {".py", ".toml", ".md", ".txt", ".cfg", ".ini", ".yaml", ".yml"}

# Patterns that indicate a real credential value (not a placeholder or variable name)
_CREDENTIAL_RE = re.compile(
    r'(?i)(password|secret|api[_\-]?key|access[_\-]?token|auth[_\-]?token)\s*=\s*["\'][^"\']{8,}["\']'
)

# Directories to skip
_SKIP_DIRS = {"__pycache__", ".venv", "venv", "env", ".git", "dist", "build"}


def _source_files():
    for path in REPO_ROOT.rglob("*"):
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if path.suffix in _SCAN_EXTS and path.is_file():
            yield path


def test_no_hardcoded_credentials():
    hits = []
    for path in _source_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if _CREDENTIAL_RE.search(line):
                hits.append(f"{path.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}")

    assert not hits, "Hardcoded credentials found:\n" + "\n".join(hits)


def test_no_session_json_in_repo():
    """session.json must not exist inside the repo — it lives in ~/.config/vidnotes/."""
    found = list(REPO_ROOT.rglob("session.json"))
    # Exclude anything under .venv / build dirs
    found = [p for p in found if not any(d in _SKIP_DIRS for d in p.parts)]
    assert not found, f"session.json found inside repo: {found}"
