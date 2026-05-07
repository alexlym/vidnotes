# Feature: github-release-prep

## Goal
Prepare vidnotes for public release on GitHub by adding a README, .gitignore, platform dependency docs, setup guide, and auditing for committed secrets or credentials.

## Approach

Work in this order:

1. **Secrets audit** — run `git ls-files` to inventory everything tracked; confirm `session.json` (stored at `~/.config/vidnotes/session.json`) is outside the repo; confirm `config.toml` is not tracked (only `config.toml.example` exists); flag `vidnotes.egg-info/` as untracked noise to exclude.

2. **`.gitignore`** — create at repo root covering: Python artifacts (`__pycache__/`, `*.pyc`, `*.pyo`, `.venv/`, `dist/`, `build/`), `vidnotes.egg-info/`, local config override (`config.toml`), local output dir (`output/`), editor files (`.vscode/`, `*.swp`), test cache (`.pytest_cache/`), and macOS junk (`.DS_Store`).

3. **`pyproject.toml` metadata** — add `description`, `authors`, `license`, and `readme = "README.md"` to the `[project]` section. Current file is missing all four.

4. **`README.md`** — create at repo root with: project tagline, what it does, supported sources (deeplearning.ai/Udemy + YouTube), prerequisites, install steps (`pip install -e .`), auth setup (`vidnotes auth login`), and usage examples for every command and major flag (`run`, `translate`, `auth login`, `auth status`, `--dry-run`, `--lesson`, `--force`, `--refetch`, `--translate`). Embed platform dependency docs as a "Prerequisites" section.

5. **Platform dependency docs** — include in the README "Prerequisites" section: Python ≥ 3.11, `playwright install chromium` (after pip install), `yt-dlp` (via `pipx install yt-dlp` or system package), and the `claude` CLI with its install instructions. Note platform-specific gotchas (e.g. Playwright on Linux requires system libs; ChromeOS/Linux container notes).

6. **Tests T1–T5** — write `tests/test_gitignore.py` (T1–T3 using `pathspec` or `gitpython` to check `.gitignore` patterns), `tests/test_secrets_audit.py` (T4 scanning repo files for credential-like strings), `tests/test_package_meta.py` (T5 parsing `pyproject.toml` and asserting required fields are present and non-empty).

## Out of Scope

- PyPI publishing or building distribution packages (`python -m build`, `twine upload`)
- GitHub Actions / CI configuration
- CHANGELOG or release notes
- Adding a LICENSE file (separate decision for the user)
- Any code logic changes — this is docs, config, and tests only
- Documentation site (mkdocs, Sphinx, etc.)
- Semantic versioning decisions beyond confirming `version` is set in `pyproject.toml`

## Files to Change

| File | Change |
|------|--------|
| `README.md` | **Create** — full project README with tagline, features, prerequisites, install, auth, all commands and flags, output structure, config reference |
| `README.ua.md` | **Create** — Ukrainian translation of the full README |
| `.gitignore` | **Create** — Python artifacts, egg-info, local config, output dirs, editor/OS files |
| `pyproject.toml` | **Edit** — add `description`, `authors`, `license`, `readme` to `[project]` section |
| `tests/test_gitignore.py` | **Create** — T1: cookies.json ignored, T2: .state.json ignored, T3: .transcripts/ ignored |
| `tests/test_secrets_audit.py` | **Create** — T4: no tracked file contains a real-looking credential string |
| `tests/test_package_meta.py` | **Create** — T5: pyproject.toml has all required publish-ready fields |

## Verification

Run these in order after implementation:

1. **Secrets audit**: `git ls-files | xargs grep -l -i "cookie\|token\|password\|secret\|api.key" 2>/dev/null` — output should be empty or only documentation examples with clearly fake values.
2. **Gitignore coverage**: `git check-ignore -v config.toml vidnotes.egg-info/ output/` — all three should be matched.
3. **Package metadata**: `pip install --dry-run .` — no warnings about missing metadata.
4. **Feature tests**: `pytest tests/test_gitignore.py tests/test_secrets_audit.py tests/test_package_meta.py -v` — all pass.
5. **Regression suite**: `pytest -m "not integration"` — all existing tests still pass.
6. **README review**: open `README.md` and manually confirm every `vidnotes` subcommand and flag from `cli.py` is documented.
