# Feature: YouTube Single Video Support

## Goal
Add `vidnotes run <youtube-url>` support: download the video's transcript via `yt-dlp` and produce a Markdown summary organised by **time section** (timestamp ranges) and **topic section** (subject groupings).

## Approach

### URL routing (`cli.py`)
Add a routing block at the top of `run()`, before deeplearning.ai auth, that detects a YouTube URL and switches to the YouTube path. Everything downstream (summarizer, writer, state tracking) is reused without modification.

### Transcript extraction (`youtube.py`)
New module handles:
- URL detection (`is_youtube_url`)
- Metadata fetch + `Lesson` construction (`get_lessons`)
- VTT subtitle download, timestamp-preserving parse, caching (`extract_content`)

### Prompt template (`youtube_prompt.md`)
New per-video prompt distinct from the course-lesson template. Instructs Claude to produce two summary sections:
1. **Timeline** — one or more bullets per time block with the start timestamp and what happens; granularity follows content density
2. **Topics** — grouped thematic sections regardless of when they appear

The prompt receives `{title}`, `{channel}`, and `{transcript}` (plain text with timestamps preserved).

### VTT parsing
`_parse_vtt()` keeps one timestamp marker per cue (`[MM:SS]`) and strips WEBVTT headers, HTML tags, and adjacent duplicate lines. This gives Claude enough temporal anchors to build the timeline section without flooding the prompt.

## Out of Scope
- Playlist / channel URLs
- Non-English subtitles (fallback to English auto-captions only)
- Translation of summaries
- Chapter markers from video metadata

## Files to Change

| File | Change |
|---|---|
| `vidnotes/youtube.py` | **New** — `is_youtube_url`, `get_lessons`, `extract_content`, `_parse_vtt`, `_slugify` |
| `vidnotes/youtube_prompt.md` | **New** — prompt template with Timeline + Topics sections |
| `vidnotes/cli.py` | Routing block + replace both `extract_content` call sites with `_extract(l)` |
| `vidnotes/summarizer.py` | Add `summarize_youtube()` that loads `youtube_prompt.md` instead of `default_prompt.md` |
| `specs/constitution/roadmap.md` | Mark YouTube support done |

**Unchanged**: `models.py`, `writer.py`, `extractor.py`, `catalog.py`, `session.py`, `fetcher.py`

## Verification

1. `vidnotes run <youtube-url> --dry-run` — prints video title, channel name, and first 300 chars of transcript; exits cleanly
2. `vidnotes run <youtube-url>` — produces `~/vidnotes/{channel-slug}/{video-slug}/{video-id}.md` containing both a **Timeline** and a **Topics** section
3. Re-running the same URL — prints "already done", skips summarization
4. `vidnotes run <youtube-url> --force` — re-summarizes, overwrites the output file
5. Invalid / private video URL — exits with a clear error message, no traceback

## Build Order

1. Write `youtube.py` (all functions)
2. Write `youtube_prompt.md`
3. Add `summarize_youtube()` to `summarizer.py`
4. Wire routing into `cli.py`
5. Dry-run gate (step 1 of Verification above) — stop and confirm before proceeding
6. Full run + resume + force checks
7. Update `roadmap.md`
