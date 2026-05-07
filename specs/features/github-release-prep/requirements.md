# Requirements: github-release-prep

- REQ-1: `README.md` at repo root covers: what vidnotes does, supported sources (Udemy, YouTube), prerequisites, install steps, and usage examples for every CLI command and major flag.
- REQ-2: `.gitignore` excludes all credentials (cookies files, `.env`), generated output (`~/vidnotes/`), state files (`.state.json`), transcript caches (`.transcripts/`), and standard Python/editor artifacts.
- REQ-3: Platform dependency documentation covers each external dependency — Python version, `yt-dlp`, Playwright browser install, and the `claude` CLI — with install commands for Linux, macOS, and Windows (WSL).
- REQ-4: A setup guide walks a new user from cloning the repo to running their first `vidnotes run` end-to-end, including auth login.
- REQ-5: A secrets/credentials audit confirms no cookies, auth tokens, API keys, or personal paths are present in any git-tracked file; any such files are added to `.gitignore` and removed from tracking if present.
- REQ-6: `pyproject.toml` has complete, publish-ready metadata: name, version, description, author, license, Python version constraint, and all runtime dependencies pinned or range-constrained.
- REQ-7: `README.ua.md` is a complete Ukrainian translation of `README.md`, covering all sections and examples.
