# Tech Stack

## Language
Python 3.11+ (uses `str | None` union syntax, `tomllib` stdlib)

## Key Dependencies
- `typer` — CLI framework
- `rich` — terminal output
- `playwright` — one-time interactive browser login (sync API)
- `requests` + `beautifulsoup4` + `lxml` — HTTP and HTML parsing
- `pyyaml` — YAML frontmatter in output files
- `claude` CLI — called as subprocess for all LLM summarization

## Package Layout
- `vidnotes/cli.py` — Typer app, all commands
- `vidnotes/session.py` — Playwright login, cookie persistence
- `vidnotes/catalog.py` — lesson list from `__NEXT_DATA__` JSON
- `vidnotes/extractor.py` — transcript extraction and cache
- `vidnotes/summarizer.py` — `claude -p` subprocess calls
- `vidnotes/writer.py` — file I/O, state tracking
- `vidnotes/config.py` — paths and settings
- `vidnotes/models.py` — dataclasses and enums

## Config & Output Paths
- Config: `~/.config/vidnotes/` (session, prompts)
- Output: `~/vidnotes/{course-slug}/`
- State: `~/vidnotes/{course-slug}/.state.json`
- Transcripts: `~/vidnotes/{course-slug}/.transcripts/{slug}.txt`

## Setup & Distribution

Distributed as an editable local install — no PyPI package.

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install Playwright's Chromium browser (required for DL.ai login)
playwright install chromium

# Prerequisites (must be done once, outside this project)
# - Claude CLI installed and logged in: https://claude.ai/code
# - yt-dlp available on PATH (installed as a dependency, no extra step)
```

First run for DL.ai courses requires a one-time interactive browser login:
```bash
vidnotes auth login
```
This opens a visible Chromium window, waits for you to log in, then saves cookies to
`~/.config/vidnotes/session.json`. YouTube URLs skip auth entirely.

## Constraints
- No `anthropic` SDK — uses `claude` CLI subprocess only
- `password` OAuth grant not available on deeplearning.ai → Playwright required for login
- Transcripts embedded in `__NEXT_DATA__["props"]["pageProps"]["captions"]` (no Wistia API)
- Course summary prompt uses `str.replace()` not `str.format()` to preserve `{slug}` literals
