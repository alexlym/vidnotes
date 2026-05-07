# Skill: changelog

Generate a changelog entry for a completed feature.

## Steps
1. Read `specs/features/{feature}/plan.md` for the feature description
2. Read `specs/features/{feature}/requirements.md` for what was built
3. Read recent git log (`git log --oneline -10`) for commit context
4. Write a changelog entry in Keep-a-Changelog format:
   ### Added / Changed / Fixed
   - Brief description of user-visible change
   - Reference to spec: `specs/features/{feature}/`
5. Output only the entry text — user will paste it into CHANGELOG.md
