# vidnotes — Agent Rules

## Workflow
- Before implementing any feature, check `specs/features/{name}/plan.md`, `requirements.md`, and `tests.md`. Wait for user review and confirmation before starting implementation.
- Before writing code, run `pytest` to confirm the regression suite is green.
- While implementing, write/update tests as described in `specs/features/{name}/tests.md` — including any cross-feature tests identified there.
- After implementing, run `pytest` — all regression tests must pass before marking a feature done.
- After implementing, run validation against `specs/features/{name}/validation.md`.
- Never modify the constitution files without user approval.
- After a plan is approved, copy it from `~/.claude/plans/` into `specs/features/{name}/plan.md` before starting implementation.
- After implementation, update any existing feature specs that were affected by the change — append a `## Changelog` section at the bottom of their `plan.md` noting what changed and why.

## Conventions
- CLI entry point: `vidnotes/cli.py`
- Summaries output to `~/vidnotes/{course-slug}/`
- State file: `{course-slug}/.state.json`; transcript cache: `{course-slug}/.transcripts/`
- Subprocess call to `claude -p` for all LLM work (no API key)
- Prompt templates: `~/.config/vidnotes/prompts/*.md` (bundled defaults auto-copied on first run)

## Testing
- Regression suite (unit + mock/workflow): `pytest` — configured in `pyproject.toml` to exclude `integration` by default
- Integration tests (real network + yt-dlp): `pytest -m integration`
- Integration + auth (requires `vidnotes auth login`): `pytest -m "integration and requires_auth"`
- Dry-run smoke test: `vidnotes run <url> --dry-run`
- For session/auth changes: `vidnotes auth status`
