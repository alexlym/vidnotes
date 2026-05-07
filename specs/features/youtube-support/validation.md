# Validation: youtube-support

| # | Criterion | How to verify |
|---|-----------|---------------|
| 1 | REQ-1: YouTube URL accepted | `vidnotes run https://www.youtube.com/watch?v=<id> --dry-run` exits 0 with no "unsupported URL" error |
| 2 | REQ-2: Transcript fetched | Dry-run output shows a non-empty transcript preview |
| 3 | REQ-3: Timestamps preserved | Inspect cached transcript file — confirm `[MM:SS]` markers appear throughout |
| 4 | REQ-4: Timeline section present | Open output `.md` — confirm a `## Timeline` (or equivalent) section with multiple timestamped bullets |
| 5 | REQ-5: Topics section present | Open output `.md` — confirm a `## Topics` (or equivalent) section with thematic groupings |
| 6 | REQ-6: Output path correct | After full run, confirm file exists at `~/vidnotes/{channel-slug}/{video-slug}/{video-id}.md` |
| 7 | REQ-7: Transcript cached; re-fetch skipped | Run twice; confirm second run prints "already done" or skips download without hitting network; `--refetch` triggers a fresh download |
| 8 | REQ-8: Resume skips completed video | Run twice; confirm second run prints "already done" and produces no duplicate output; `--force` re-summarizes |
| 9 | REQ-9: Graceful error on bad URL | `vidnotes run https://www.youtube.com/watch?v=INVALID` exits with a readable error message and no traceback |
| 10 | REQ-10: Dry-run output | `--dry-run` prints video title, channel name, and transcript preview; confirms no `.md` file is written and Claude is not invoked |
