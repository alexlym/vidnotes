# Requirements: translation

- REQ-1: `vidnotes run <url> --translate <lang>` translates all summaries after generating them, writing to `{course-slug}/{lang}/` alongside the originals
- REQ-2: `vidnotes translate <course-slug-or-url> <lang>` translates all existing summaries for a course/video without re-summarizing
- REQ-3: Both per-lesson summaries and `_course_summary.md` are translated
- REQ-4: Output files mirror the original filenames under a language subfolder: `{course-slug}/{lang}/{lesson-slug}.md`
- REQ-5: Language is specified as a BCP-47 code or plain name (e.g. `ua`, `de`, `polish`) — Claude resolves ambiguous names
- REQ-6: Already-translated files are skipped on re-run (same resume logic as summaries), overridable with `--force`
- REQ-7: If a source summary does not exist yet, `vidnotes translate` warns and skips that lesson rather than failing
- REQ-8: Translation uses a dedicated prompt template (`translation_prompt.md`) bundled as a default and overridable via `~/.config/vidnotes/prompts/`
- REQ-9: If the language code or name is not recognised (e.g. typo, gibberish), print a clear error message listing example valid values and exit without processing any files
- REQ-10: `vidnotes run <url> --translate <lang>` is the single-command flow — fetches transcripts, generates summaries, and translates all in one pass without any intermediate manual steps
