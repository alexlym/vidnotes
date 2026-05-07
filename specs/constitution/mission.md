# Mission

vidnotes turns video courses and YouTube videos into permanent, searchable Markdown study notes.

## Goals
- One command to summarize an entire course into per-lesson `.md` files
- A whole-course reference document (`_course_summary.md`) alongside individual notes
- YouTube videos summarized into Timeline + Topics sections with no authentication required
- Works with any logged-in Claude account — no API key required
- Resumable: never re-summarize a lesson or video that already has a good summary

## Non-Goals
- Does not support other learning platforms (Coursera, Udemy, etc.)
- Does not support YouTube playlists or channels — single videos only
- Does not store credentials — login is interactive, one-time browser session
- Not a real-time tool — designed for batch runs, not live note-taking

## Success Metrics
- Dry run completes for any course URL without crashing
- Per-lesson summaries cover all sections: Overview, Key Concepts, Technical Details, Practical Takeaways, Review Questions
- Course summary is ~1-2 A4 pages with per-lesson subsections
- Resume after interruption skips already-completed lessons correctly
