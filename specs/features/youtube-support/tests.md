# Tests: youtube-support

## Tests to Write

All tests below were written as part of this feature. Test IDs group related scenarios.

| ID | Scenario | Type | File |
|----|----------|------|------|
| T1 | `is_youtube_url` — accepts watch, shorts, youtu.be; rejects non-YouTube and arbitrary URLs | unit | `tests/test_youtube.py` |
| T2 | `_slugify` — lowercases, strips special chars, collapses whitespace, truncates at 60, no trailing dash | unit | `tests/test_youtube.py` |
| T3 | `_parse_vtt` — keeps one `[MM:SS]` timestamp per cue, deduplicates adjacent lines, strips HTML tags, skips WEBVTT header, handles hour offsets correctly | unit | `tests/test_youtube.py` |
| T4 | `get_lessons` — returns exactly one `Lesson` with correct `id`, `title`, and `course_slug` in `channel/title-slug` format | unit (mocked yt-dlp subprocess) | `tests/test_youtube.py` |
| T5 | `get_lessons` errors — exits cleanly (`click.Exit`) when yt-dlp binary is missing or returns non-zero | unit (mocked subprocess) | `tests/test_youtube.py` |
| T6 | `extract_content` — returns cached transcript when `.transcripts/{id}.txt` exists; downloads and parses VTT, saves to cache; falls back to description JSON when no VTT; returns `source="none"` when both fail | unit (mocked subprocess + tmp_path) | `tests/test_youtube.py` |
| T7 | `summarize_youtube` — passes video title and channel name into the rendered prompt | unit (mocked subprocess) | `tests/test_summarizer.py` |
| T8 | `summarize_youtube` — returns Claude stdout stripped of leading/trailing whitespace | unit (mocked subprocess) | `tests/test_summarizer.py` |
| T9 | `summarize_youtube` — appends `[transcript truncated]` in prompt when transcript exceeds character limit | unit (mocked subprocess) | `tests/test_summarizer.py` |
| T10 | `summarize_youtube` — copies `youtube_prompt.md` from package data to config dir on first run if file is missing | unit (mocked subprocess + tmp_path) | `tests/test_summarizer.py` |
| T11 | CLI dry-run (YouTube) — exits zero; output contains title, channel, and transcript preview; no `.md` files written; `summarize_youtube` not called | mock/workflow | `tests/test_cli.py` |
| T12 | CLI full run (YouTube) — writes output file at `{channel}/{video}/{id}.md`; file contains both a `Timeline` and `Topics` section | mock/workflow | `tests/test_cli.py` |
| T13 | CLI full run (YouTube) — `summarize_course` is never called (single video, no course summary) | mock/workflow | `tests/test_cli.py` |
| T14 | CLI resume/force/refetch (YouTube) — default re-run prints "already done" and skips; `--force` overwrites output; `--refetch` deletes `.transcripts/` before re-downloading | mock/workflow | `tests/test_cli.py` |
| T15 | CLI no-content graceful skip — exits zero, skips summarization when both transcript and page_text are None | mock/workflow | `tests/test_cli.py` |
| T16 | CLI DL.ai routing — dry-run and full run use the dl.ai path; `summarize_youtube` is never called for a deeplearning.ai URL | mock/workflow | `tests/test_cli.py` |
| T17 | Real dry-run (YouTube) — exits zero, output contains channel name and non-trivial transcript preview | integration (real network + yt-dlp) | `tests/test_integration.py` |
| T18 | Real metadata — `get_lessons` returns correct video ID and `channel/title` `course_slug` format from live yt-dlp call | integration | `tests/test_integration.py` |
| T19 | Real transcript caching — first call downloads and returns a transcript with timestamps; second call returns `source="cached"` | integration | `tests/test_integration.py` |
| T20 | Real output path — `course_slug` splits into two non-empty parts (channel slug, video slug) | integration | `tests/test_integration.py` |
| T21 | DL.ai dry-run (real session) — exits zero, output lists at least one lesson | integration + requires_auth | `tests/test_integration.py` |

**Types:**
- `unit` — isolated, no network, uses `tmp_path` or mocked subprocess
- `mock/workflow` — full CLI layer via `typer.testing.CliRunner`, all external calls mocked
- `integration` — real network + yt-dlp; marked `@pytest.mark.integration`
- `requires_auth` — also needs a valid `vidnotes` session; marked `@pytest.mark.requires_auth`

---

## Regression Suite

Tests that run on every `pytest` invocation (default config excludes `integration`).
All unit and mock/workflow tests are regression candidates. Integration tests require a network
call so they are excluded from the default suite but run explicitly via `pytest -m integration`.

| ID | Included in regression | Reason |
|----|------------------------|--------|
| T1 | yes | guards URL routing — breakage would silently send YouTube URLs to the dl.ai path |
| T2 | yes | guards file path correctness — bad slugs corrupt output directories |
| T3 | yes | guards transcript quality fed to Claude — wrong parsing degrades every summary |
| T4 | yes | guards Lesson structure used across the whole pipeline |
| T5 | yes | guards user-facing error messages on missing yt-dlp |
| T6 | yes | guards caching, fallback, and source tagging used by CLI and writer |
| T7 | yes | guards prompt correctness — missing title/channel would silently produce bad summaries |
| T8 | yes | guards output cleaning |
| T9 | yes | guards transcript truncation — removing this would send >150k-char prompts to Claude |
| T10 | yes | guards prompt bootstrapping on fresh installs |
| T11 | yes | guards the entire dry-run contract |
| T12 | yes | guards output file path and required section headings |
| T13 | yes | guards that YouTube does not trigger course-summary generation |
| T14 | yes | guards resume/force/refetch state logic — breakage silently re-summarizes everything |
| T15 | yes | guards graceful handling of videos with no captions |
| T16 | yes | guards that dl.ai and YouTube routes don't bleed into each other |
| T17–T20 | no — `@pytest.mark.integration` | require network + yt-dlp; run with `pytest -m integration` |
| T21 | no — `@pytest.mark.integration @pytest.mark.requires_auth` | requires live session; run manually |

---

## Existing Tests to Update

No pre-existing test files were present before this feature. This is the initial test suite.

---

## Test Commands

```bash
# Default: regression suite only (T1–T16) — configured in pyproject.toml
pytest

# Feature unit tests only
pytest tests/test_youtube.py tests/test_summarizer.py

# CLI/workflow tests only
pytest tests/test_cli.py

# Integration tests (requires internet + yt-dlp)
pytest -m integration

# Integration tests that also need a valid session
pytest -m "integration and requires_auth"

# Everything
pytest --override-ini="addopts=" 
```
