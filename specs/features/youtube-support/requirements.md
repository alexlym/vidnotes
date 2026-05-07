# Requirements: youtube-support

- REQ-1: `vidnotes run <url>` accepts any `youtube.com/watch`, `youtube.com/shorts`, or `youtu.be/` URL without additional flags or config.
- REQ-2: The transcript is fetched by whatever method produces the most complete English text; auto-captions are acceptable as fallback.
- REQ-3: Parsed transcript preserves timestamp markers so Claude can build a time-based summary.
- REQ-4: The summary output contains a **Timeline** section with one or more bullets per time block, each starting with the timestamp and describing what is covered — granularity should reflect the density of content, not a fixed interval.
- REQ-5: The summary output contains a **Topics** section: thematic groupings of content regardless of when they appear in the video.
- REQ-6: Output file is written to `~/vidnotes/{channel-slug}/{video-slug}/{video-id}.md`, where `video-slug` is derived from the video title.
- REQ-7: Transcript is cached on first download inside `~/vidnotes/{channel-slug}/{video-slug}/.transcripts/`; subsequent runs skip re-fetching unless `--refetch` is passed.
- REQ-8: A completed video is skipped on re-run ("already done") unless `--force` is passed.
- REQ-9: If the transcript cannot be fetched (private video, no captions, network error), the tool exits with a clear human-readable error and no Python traceback.
- REQ-10: `--dry-run` prints the video title, channel name, and a transcript preview (first ~300 chars) without invoking Claude or writing any files.
