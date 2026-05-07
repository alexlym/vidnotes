# Tests: github-release-prep

## Tests to Write

| ID | Name / scenario | Type | File |
|----|-----------------|------|------|
| T1 | `.gitignore` covers cookies file (`cookies.json`) | unit | `tests/test_gitignore.py` |
| T2 | `.gitignore` covers state file (`.state.json`) | unit | `tests/test_gitignore.py` |
| T3 | `.gitignore` covers transcript cache dir (`.transcripts/`) | unit | `tests/test_gitignore.py` |
| T4 | No tracked file contains a real-looking secret (cookie, token, key) | unit | `tests/test_secrets_audit.py` |
| T5 | `pyproject.toml` has all required metadata fields | unit | `tests/test_package_meta.py` |

**Types:** `unit` (isolated function), `mock/workflow` (multi-layer, external deps mocked), `integration` (real network/DB/FS, use `@pytest.mark.integration`), `e2e` (full stack from entry point)

## Regression Suite
Tests from the table above that should run on every CI build (i.e. catch silent regressions).

- T1 — guards that credentials can't accidentally be committed in a future PR
- T2 — guards that per-course state files are never tracked
- T3 — guards that cached transcript data is never tracked
- T4 — catches accidental credential leakage in any future commit that adds text files
- T5 — catches pyproject.toml metadata regressions (e.g. someone removing `version` or `license`)

## Existing Tests to Update

- None expected — this feature adds only config/doc files and no logic changes; no existing tests should be affected.

## Test Commands
```
# Run only this feature's tests
pytest tests/test_gitignore.py tests/test_secrets_audit.py tests/test_package_meta.py -v

# Run full regression suite
pytest -m "not integration"

# Run including integration
pytest
```
