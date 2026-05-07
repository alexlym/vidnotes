# vidnotes

Turn video courses and YouTube videos into structured Markdown notes using Claude.

- Summarizes each lesson individually, then generates a whole-course summary
- Supports [deeplearning.ai](https://learn.deeplearning.ai) courses and any YouTube video
- Caches transcripts locally — resume interrupted runs, re-summarize without re-downloading
- Translate any set of notes into another language in one command

> **About this project:** vidnotes is a vibe-coded experiment in using [Claude Code](https://claude.ai/code) as a daily development partner. The entire codebase is built with a spec-driven development workflow from the course [Spec-Driven Development with Coding Agents](https://learn.deeplearning.ai/courses/spec-driven-development-with-coding-agents) — every feature starts as a spec before a line of code is written.

---

## Prerequisites

| Dependency | Version | Install |
|------------|---------|---------|
| Python | ≥ 3.11 | [python.org](https://www.python.org/downloads/) or `pyenv` |
| Claude CLI | latest | `npm install -g @anthropic-ai/claude-code` |
| yt-dlp | latest | `pipx install yt-dlp` or `pip install yt-dlp` |
| Playwright (Chromium) | ≥ 1.40 | installed automatically; run `playwright install chromium` after `pip install` |

**Linux / ChromeOS note:** Playwright on Linux may need system libraries — if the browser fails to launch, run:
```
playwright install-deps chromium
```

**Claude CLI note:** You must be logged in (`claude`) and have an active subscription. vidnotes calls `claude -p` as a subprocess — no API key needed.

---

## Install

```bash
git clone https://github.com/yourusername/vidnotes.git
cd vidnotes
pip install -e .
playwright install chromium
```

Verify the install:
```bash
vidnotes --help
```

---

## Configuration (optional)

Copy the example config and edit to taste:
```bash
cp config.toml.example ~/.config/vidnotes/config.toml
```

`config.toml` options:
```toml
[options]
output_dir = "~/vidnotes"   # where notes are written (default: ~/vidnotes)
```

You can also pass `--output-dir` on any command to override.

---

## Authentication (deeplearning.ai only)

YouTube videos require no auth. For deeplearning.ai courses, log in once:

```bash
vidnotes auth login
```

A browser opens — log in, then close it. Your session is saved to `~/.config/vidnotes/session.json` and reused automatically.

Check session status at any time:
```bash
vidnotes auth status
```

---

## Usage

### Summarize a deeplearning.ai course

```bash
vidnotes run https://learn.deeplearning.ai/courses/your-course
```

Notes are written to `~/vidnotes/<course-slug>/`. A whole-course summary is generated at `_course_summary.md` after all lessons are done.

### Summarize a YouTube video

```bash
vidnotes run https://www.youtube.com/watch?v=VIDEO_ID
```

### Options for `vidnotes run`

| Flag | Description |
|------|-------------|
| `--lesson SLUG` | Only process lessons whose slug or title contains `SLUG` |
| `--force` | Re-generate summaries (reuses cached transcripts) |
| `--refetch` | Re-download transcripts and re-generate summaries |
| `--dry-run` | Extract and preview content without calling Claude |
| `--translate LANG` | Translate summaries into `LANG` after summarizing (e.g. `ua`, `de`, `polish`) |
| `--output-dir DIR` | Write output to `DIR` instead of the default |

### Examples

```bash
# Preview what would be processed without summarizing
vidnotes run https://learn.deeplearning.ai/courses/ml-ops --dry-run

# Process only the first lesson matching "intro"
vidnotes run https://learn.deeplearning.ai/courses/ml-ops --lesson intro

# Re-summarize all lessons (transcripts already cached)
vidnotes run https://learn.deeplearning.ai/courses/ml-ops --force

# Summarize and translate to Ukrainian in one step
vidnotes run https://www.youtube.com/watch?v=VIDEO_ID --translate ua
```

---

## Translate existing notes

Translate previously generated notes into another language:

```bash
# By course slug
vidnotes translate ml-ops ua

# By URL
vidnotes translate https://learn.deeplearning.ai/courses/ml-ops ukrainian

# Re-translate even if translated files already exist
vidnotes translate ml-ops de --force
```

Language can be a BCP-47 code (`ua`, `de`, `fr`, `zh`) or a plain name (`ukrainian`, `german`, `french`).

Translated files are written alongside the originals under a `<lang>/` subdirectory.

---

## Output structure

```
~/vidnotes/
└── <course-slug>/
    ├── lesson-one.md
    ├── lesson-two.md
    ├── _course_summary.md
    ├── ua/
    │   ├── lesson-one.md
    │   └── lesson-two.md
    ├── .state.json          # progress tracking (gitignored)
    └── .transcripts/        # cached transcripts (gitignored)
```

---

## Custom prompts

vidnotes ships with default prompts. To customise them, edit the files in `~/.config/vidnotes/prompts/` (created automatically on first run):

| File | Purpose |
|------|---------|
| `summarize.md` | Per-lesson summary prompt (deeplearning.ai) |
| `translation.md` | Translation prompt |

YouTube and course-summary prompts are built-in and not yet user-configurable.

---

## Roadmap

- `vidnotes transcripts` — browse all cached transcripts across courses
- `vidnotes ask "<question>"` — Q&A over transcripts with citations
- Parallel translation with progress bar
- Agent guide (`AGENT.md`) for AI-assisted workflows
