# Skill: test

Plan, execute, and update tests for a feature being implemented.

## Steps

### Planning (before writing code)
1. Read `specs/features/{feature}/tests.md` — review the test table, regression selections, and existing-test updates
2. Scan the full test suite for tests that touch shared code (models, CLI routing, config, utilities). Add any missed cross-feature impacts to the "Existing Tests to Update" section in `tests.md`
3. Confirm the test commands in `tests.md` match those in `CLAUDE.md` and `pyproject.toml`

### Baseline (before implementing)
4. Run the full regression suite to confirm it is green before any changes:
   ```
   pytest
   ```
   If any tests are already failing, stop and report — do not proceed with new code on a broken baseline

### During implementation
5. Write new tests as listed in the test table, matching the types already used in the project (unit, mock/workflow, integration)
6. Update existing tests identified in `tests.md` — including tests in other feature areas that touch shared code
7. Run the feature's own tests frequently as you implement to catch regressions early:
   ```
   pytest tests/test_{feature}.py
   ```

### After implementation
8. Run the full regression suite — all tests must pass:
   ```
   pytest
   ```
9. If integration tests exist for this feature, run them separately and report results:
   ```
   pytest -m integration
   ```
10. Update `tests.md` to reflect any test IDs added or changed during implementation
11. Report: tests added (file + function name), tests updated, pass/fail summary
