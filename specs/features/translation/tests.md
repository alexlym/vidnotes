# Tests: translation

## Tests to Write

| ID | Name / scenario | Type | File |
|----|-----------------|------|------|
| T1 | `translated_path()` returns correct subfolder path for a lesson | unit | tests/test_translation.py |
| T2 | translation skipped when output file already exists (no `--force`) | unit | tests/test_translation.py |
| T3 | translation runs when `--force` is set even if file exists | unit | tests/test_translation.py |
| T4 | missing source summary emits warning and skips lesson | unit | tests/test_translation.py |
| T5 | `vidnotes translate <slug> ua` CLI command translates all existing summaries | mock/workflow | tests/test_cli.py |
| T6 | `vidnotes run <url> --translate ua` summarizes then translates in one pass | mock/workflow | tests/test_cli.py |
| T7 | `--force` on translate command re-translates already-translated files | mock/workflow | tests/test_cli.py |
| T8 | plain language name (e.g. `polish`) passed through to prompt without error | mock/workflow | tests/test_cli.py |
| T9 | real translation of a YouTube video summary into Ukrainian | integration | tests/test_integration.py |
| T10 | unrecognised language code exits with friendly error, no files written | unit | tests/test_translation.py |
| T11 | `vidnotes run <url> --translate ua` on fresh course completes full pipeline (fetch → summarize → translate) | mock/workflow | tests/test_cli.py |

## Regression Suite

- T1 — guards core path-building logic; silent breakage would misplace all output files
- T2 — guards resume/skip behaviour; regression would re-translate everything on every run
- T3 — guards `--force` override; regression would make force flag ineffective
- T4 — guards graceful degradation; regression would crash mid-batch on missing files
- T5 — guards CLI routing for `translate` subcommand
- T6 — guards end-to-end `--translate` flag wiring in `run`
- T10 — guards early exit on bad language input; regression would silently pass garbage to Claude
- T11 — guards full single-command pipeline; regression would break the primary advertised usage
<!-- T9 excluded — requires real network and Claude CLI, use @pytest.mark.integration -->

## Existing Tests to Update

- `tests/test_cli.py` — `run` command tests may need a `--translate` branch; check any test that asserts the full output file list to avoid false failures
- `tests/test_summarizer.py` — if `load_prompt_template` is extended to support translation templates, update tests that assert the default template path

## Test Commands
```
# This feature only
pytest tests/test_translation.py tests/test_cli.py -k "translate"

# Full regression suite
pytest -m "not integration"

# Including integration
pytest -m integration
```
