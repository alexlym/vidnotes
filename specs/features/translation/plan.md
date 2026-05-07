# Feature: translation

## Goal
Translate generated Markdown summaries (per-lesson and course summary) into another language via `claude -p`, writing output into a language subfolder within the course/video directory.

## Approach

### Language validation
A static allowlist of common BCP-47 codes and plain names (e.g. `ua`, `de`, `fr`, `polish`, `german`) is checked upfront in `translator.py` before any files are touched. If the input doesn't match, exit with a friendly error listing examples. This catches typos early rather than discovering them after processing the first lesson. Claude handles the actual translation for any name that passes validation, so the allowlist only needs to cover common cases — not be exhaustive.

### Translation logic (`vidnotes/translator.py` — new file)
- `validate_language(lang: str) -> str | None` — returns normalised lang string or `None` if not recognised
- `translated_output_path(output_dir, lesson, lang) -> Path` — returns `{output_dir}/{course_slug}/{lang}/{lesson_slug}.md`
- `translate(summary_text: str, lang: str, claude_bin: str) -> str` — loads the translation prompt, injects `{lang}` and `{summary}`, calls `claude -p`, returns translated body
- `_ensure_translation_prompt_file() -> Path` — same copy-on-first-use pattern as other prompts in `summarizer.py`

### Skip/resume logic
File existence is the source of truth — if `{lang}/{slug}.md` already exists, skip. No new state fields needed. `--force` bypasses the check.

### CLI changes (`vidnotes/cli.py`)
1. Add `--translate: str | None` option to the existing `run` command. After all summaries complete (same point where course summary is currently generated), loop over the lesson output files and translate each one, then translate `_course_summary.md` if it exists.
2. Add a new `translate` subcommand: `vidnotes translate <course-slug-or-url> <lang>`. Resolves the slug from a URL the same way `run` does, then scans `{output_dir}/{course_slug}/*.md` (excluding `_course_summary.md` first, then handles it separately). Warns and skips missing source files rather than failing.

### Prompt template (`vidnotes/translation_prompt.md` — new file)
Bundled default instructs Claude to translate the provided Markdown summary into `{lang}`, preserving all Markdown structure, headings, code blocks, and frontmatter fields verbatim — only translating prose content.

### Config (`vidnotes/config.py`)
Add `TRANSLATION_PROMPT_FILE = PROMPTS_DIR / "translation.md"` constant, consistent with the existing prompt file constants.

## Out of Scope
- Translating raw transcripts (only finished `.md` summaries)
- Auto-detecting or inferring the source language
- Running multiple target languages in a single command
- Translating while each lesson is being summarised (translation always runs as a separate pass after all summaries are done)
- Modifying `.state.json` to track translation status (file existence is sufficient)

## Files to Change

| File | Change |
|------|--------|
| `vidnotes/translator.py` | **New.** `validate_language`, `translate`, `translated_output_path`, `_ensure_translation_prompt_file` |
| `vidnotes/translation_prompt.md` | **New.** Bundled default translation prompt |
| `vidnotes/config.py` | Add `TRANSLATION_PROMPT_FILE` constant |
| `vidnotes/cli.py` | Add `--translate` option to `run`; add `translate` subcommand |
| `tests/test_translation.py` | **New.** Unit tests T1–T4, T10 |
| `tests/test_cli.py` | Add mock/workflow tests T5–T8, T11 |
| `tests/test_integration.py` | Add integration test T9 |

## Verification
<!-- Manual end-to-end steps — automated coverage in tests/test_translation.py and tests/test_cli.py -->
1. Fresh YouTube video: `vidnotes run <url> --translate ua` — confirm `{slug}/ua/{lesson}.md` and `{slug}/ua/_course_summary.md` created with Ukrainian text
2. Existing course: `vidnotes run <url>` then `vidnotes translate <slug> ua` — confirm translation files created, no re-summarisation output in console
3. Re-run translate: second `vidnotes translate <slug> ua` — confirm all lessons print "skipped"; `--force` causes re-translation
4. Bad language: `vidnotes run <url> --translate zzz` — confirm error message with examples printed, zero files written under `zzz/`
5. Missing source: delete one `.md`, run `vidnotes translate <slug> ua` — confirm warning for that lesson, others translated successfully

## Changelog

### Implemented 2026-05-07
- New `vidnotes/translator.py`: `validate_language`, `translate`, `translated_output_path`, `_ensure_translation_prompt_file`
- New `vidnotes/translation_prompt.md`: bundled default prompt
- `vidnotes/config.py`: added `TRANSLATION_PROMPT_FILE` constant
- `vidnotes/cli.py`: added `--translate` option to `run`; added `translate` subcommand; added `_run_translation` helper; added `_lessons_from_dir` helper for slug-based resolution
- `tests/test_translation.py`: 11 new unit tests (T1–T4, T10 + validate_language units)
- `tests/test_cli.py`: 5 new mock/workflow tests (T5–T8, T11)
