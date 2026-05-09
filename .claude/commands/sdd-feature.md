Create a feature spec for a new roadmap item. Run this before starting any implementation.

Usage: `/sdd-feature <feature-name>`

The feature name becomes the folder name under `specs/features/`. Use kebab-case (e.g. `youtube-support`, `translation`).

---

## Step 1 — Confirm the feature name

If no feature name was provided, ask: "What is the feature name? (kebab-case, e.g. youtube-support)"

Check that `specs/features/{name}/` does not already exist. If it does, tell the user and stop.

---

## Step 2 — Ask for a brief description

Ask: "Describe the feature in 1–2 sentences — what it adds and why."

---

## Step 3 — Create the spec files

Create `specs/features/{name}/` with these three files:

### `specs/features/{name}/plan.md`

```markdown
# Feature: {feature-name}

## Goal
{1-sentence description from Step 2}

## Approach
<!-- How it will be implemented: which files change, what logic is added -->

## Out of Scope
<!-- What this explicitly does NOT do -->

## Files to Change
<!-- List each file and what changes -->

## Verification
<!-- How to test end-to-end -->
```

### `specs/features/{name}/requirements.md`

```markdown
# Requirements: {feature-name}

- REQ-1: <!-- functional requirement -->
- REQ-2: <!-- functional requirement -->
- REQ-3: <!-- edge case or constraint -->
```

### `specs/features/{name}/validation.md`

```markdown
# Validation: {feature-name}

| # | Criterion | How to verify |
|---|-----------|---------------|
| 1 | REQ-1 met | <!-- manual step or command --> |
| 2 | REQ-2 met | <!-- manual step or command --> |
| 3 | REQ-3 met | <!-- manual step or command --> |
```

### `specs/features/{name}/tests.md`

List each test to write with its type. Then decide which tests belong in the regression suite — a test can appear in both places (e.g. a mock CLI test is both a workflow test and a regression guard). Only include types that are relevant; remove sections that don't apply.

```markdown
# Tests: {feature-name}

## Tests to Write

| ID | Name / scenario | Type | File |
|----|-----------------|------|------|
| T1 | <!-- e.g. valid URL recognised --> | unit | <!-- e.g. tests/test_catalog.py --> |
| T2 | <!-- e.g. CLI dry-run shows title --> | mock/workflow | <!-- tests/test_cli.py --> |
| T3 | <!-- e.g. real video fetched --> | integration | <!-- tests/test_integration.py --> |

**Types:** `unit` (isolated function), `mock/workflow` (multi-layer, external deps mocked), `integration` (real network/DB/FS, use `@pytest.mark.integration`), `e2e` (full stack from entry point)

## Regression Suite
Tests from the table above that should run on every CI build (i.e. catch silent regressions).
Integration tests only if they are fast and don't require auth/credentials.

- T1 — <!-- reason: guards core URL detection logic -->
- T2 — <!-- reason: guards CLI routing and output format -->
<!-- T3 excluded — requires network, use @pytest.mark.integration -->

## Existing Tests to Update
Review tests across the whole test suite — not just files related to this feature. Changes to shared utilities, models, or CLI routing often break tests in other feature areas.

- <!-- none, or: file + which test(s) + what changes and why -->
- <!-- e.g. tests/test_cli.py::test_dl_ai_routing — needs new branch for YouTube auth skip -->

## Test Commands
<!-- Run only this feature's tests (e.g. pytest tests/test_catalog.py -k youtube) -->
<!-- Run full regression suite (e.g. pytest -m "not integration") -->
<!-- Run including integration (e.g. pytest) -->
```

---

## Step 4 — Update the roadmap

Add the feature as a planned item in `specs/constitution/roadmap.md` if it is not already listed:

```
- [ ] {Feature description} (`specs/features/{name}/`)
```

---

## Step 5 — Present next steps

Tell the user:
- Which files were created
- That `plan.md` needs the Approach, Out of Scope, Files to Change, and Verification sections filled in before implementation begins
- That `tests.md` needs the test table, regression selection, and cross-feature test review filled in before writing code — scan the full test suite for tests that touch shared code (models, CLI routing, config) to catch indirect breakage early
- To run `/sdd-feature` again for additional features, or start a planning session to fill in `plan.md` and `tests.md`
