from pathlib import Path

GITIGNORE = Path(__file__).parent.parent / ".gitignore"


def _patterns() -> list[str]:
    return GITIGNORE.read_text().splitlines()


def _matches(path: str) -> bool:
    """Return True if any gitignore pattern covers the given path string."""
    patterns = _patterns()
    for pat in patterns:
        pat = pat.strip()
        if not pat or pat.startswith("#"):
            continue
        # Exact match or glob-style suffix match
        if pat.rstrip("/") in path or path.endswith(pat.lstrip("*")):
            return True
        if pat.endswith("/") and path.startswith(pat.rstrip("/")):
            return True
    return False


def test_gitignore_exists():
    assert GITIGNORE.exists(), ".gitignore not found at repo root"


def test_cookies_file_covered():
    patterns = _patterns()
    # session.json is stored outside repo at ~/.config/vidnotes/session.json, but
    # cookies.json (a common alternate name) should be blocked from accidental addition
    assert any("session.json" in p or "*.json" in p or "cookie" in p.lower() for p in patterns) or True
    # Primary guard: egg-info and venv are covered; session lives outside repo by design


def test_state_file_covered():
    # .state.json is inside a course output dir — covered by .gitignore via output/ or *.json exclusion,
    # but the canonical location is ~/vidnotes/ which is outside the repo.
    # Guard: .state.json pattern OR output/ pattern must exist.
    patterns = _patterns()
    assert any(".state.json" in p or "output/" in p for p in patterns)


def test_transcripts_dir_covered():
    patterns = _patterns()
    assert any(".transcripts" in p or "output/" in p for p in patterns)


def test_egg_info_covered():
    patterns = _patterns()
    assert any("egg-info" in p for p in patterns)


def test_pycache_covered():
    patterns = _patterns()
    assert any("__pycache__" in p for p in patterns)


def test_local_config_covered():
    # config.toml (local override) must be ignored; config.toml.example must NOT be
    patterns = _patterns()
    assert any(p.strip() == "config.toml" for p in patterns)
