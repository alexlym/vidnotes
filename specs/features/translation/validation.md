# Validation: translation

| # | Criterion | How to verify |
|---|-----------|---------------|
| 1 | REQ-1 met — `--translate` flag generates translated files after summarizing | `vidnotes run <url> --translate ua` on a fresh course; confirm `{course-slug}/ua/*.md` files exist |
| 2 | REQ-2 met — standalone `translate` command works on existing summaries | Run `vidnotes run <url>` first, then `vidnotes translate <slug> ua`; confirm `{course-slug}/ua/*.md` without re-summarizing |
| 3 | REQ-3 met — course summary is also translated | Check `{course-slug}/ua/_course_summary.md` exists after either flow |
| 4 | REQ-4 met — output filenames mirror originals under lang subfolder | Confirm `{course-slug}/ua/lesson-1.md` matches structure of `{course-slug}/lesson-1.md` |
| 5 | REQ-5 met — plain language name accepted | `vidnotes translate <slug> polish` completes without error |
| 6 | REQ-6 met — re-run skips already-translated files | Run translate twice; second run prints "skipped" for all lessons; use `--force` to re-translate |
| 7 | REQ-7 met — missing source summary is warned and skipped | Delete one source `.md`, run `vidnotes translate`; confirm warning printed, other lessons translated |
| 8 | REQ-8 met — custom prompt override works | Place custom `translation_prompt.md` in `~/.config/vidnotes/prompts/`; confirm it is used over the bundled default |
| 9 | REQ-9 met — unrecognised language gives friendly error | `vidnotes run <url> --translate zzz`; confirm error message is printed with example valid values and no files are written |
| 10 | REQ-10 met — single command does full pipeline | `vidnotes run <url> --translate ua` on a completely fresh course (no cached transcripts); confirm transcripts fetched, summaries written, translations written, all in one run |
