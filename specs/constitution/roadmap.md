# Roadmap

## Completed
- [x] CLI with course URL, `--dry-run`, `--lesson` filter
- [x] Interactive browser login (Playwright), cookie persistence
- [x] Transcript extraction from `__NEXT_DATA__`
- [x] Per-lesson Markdown summaries via `claude -p`
- [x] Transcript caching, per-lesson state, resume support
- [x] `--force` (re-summarize) and `--refetch` (re-download) flags
- [x] Whole-course summary (`_course_summary.md`)

## Planned
- [x] YouTube video support — transcript + Timeline/Topics summary via `vidnotes run <youtube-url>` (`specs/features/youtube-support/`)
- [x] Translation of summaries to another language (`specs/features/translation/`)
- [ ] `vidnotes transcripts` command — list all cached transcripts across courses/videos with their paths, and print usage hints for further processing (re-summarize, translate, custom prompt) (`specs/features/transcript-browser/`)
- [ ] `vidnotes ask "<question>"` — Q&A over transcripts: ask a question and get an answer with citations to specific lessons/videos; optionally scope to a single course or search across all downloaded content (`specs/features/transcript-qa/`)
- [ ] Translation progress — show a Rich progress bar with lesson count and ETA during long multi-file translate runs; optionally run `claude -p` calls in parallel to cut total time from N×30s to ~30s (`specs/features/translation-progress/`)
- [ ] Agent usage guide — a compact `AGENT.md` listing every command, flag, and example so an AI agent can load one small file and use vidnotes immediately without reading the full project (`specs/features/agent-guide/`)
- [ ] GitHub public release prep — README, .gitignore, platform dependency docs, setup guide, and any secrets/credentials audit for external review (`specs/features/github-release-prep/`)
- [ ] Configurable Claude model per task — set the model used for per-lesson summaries, whole-course summary, and translation independently via `config.toml` (e.g. Opus for course summary, Haiku for translation) with a `--model` CLI override (`specs/features/configurable-models/`)
- [ ] Usage tracking — record tokens/cost per summarization and translation call; write a `_usage.json` to the course folder with per-lesson and totals so the user can see what each run cost (`specs/features/usage-tracking/`)
