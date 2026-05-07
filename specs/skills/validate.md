# Skill: validate

Run this skill after implementing a feature to check it against the feature's validation scorecard.

## Steps
1. Read `specs/features/{feature}/requirements.md` — understand the acceptance criteria
2. Read `specs/features/{feature}/validation.md` — find the scorecard
3. For each item in the scorecard:
   - Test it manually or read the relevant code
   - Mark PASS / FAIL / PARTIAL
4. Report results as a table: Criterion | Status | Notes
5. If any FAIL: describe what's missing and suggest a fix
6. If all PASS: confirm the feature is complete and update `specs/constitution/roadmap.md`
