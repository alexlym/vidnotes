import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .config import state_file, transcripts_dir
from .models import LessonContent, LessonState, LessonStatus


def output_path(output_dir: Path, lesson) -> Path:
    return output_dir / lesson.course_slug / f"{lesson.slug}.md"


def write_summary(path: Path, lesson, content: LessonContent, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = {
        "title": lesson.title,
        "course": lesson.course_slug,
        "url": lesson.url,
        "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "content_source": content.source,
    }
    fm_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    path.write_text(f"---\n{fm_str}---\n\n{body}\n", encoding="utf-8")


# --- Transcript cache ---

def save_transcript(output_dir: Path, lesson, text: str) -> None:
    td = transcripts_dir(output_dir, lesson.course_slug)
    td.mkdir(parents=True, exist_ok=True)
    (td / f"{lesson.slug}.txt").write_text(text, encoding="utf-8")


def load_transcript(output_dir: Path, lesson) -> str | None:
    path = transcripts_dir(output_dir, lesson.course_slug) / f"{lesson.slug}.txt"
    return path.read_text(encoding="utf-8") if path.exists() else None


# --- State tracking ---

def load_state(output_dir: Path, course_slug: str) -> dict[str, LessonState]:
    path = state_file(output_dir, course_slug)
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    result = {}
    for slug, entry in data.get("lessons", {}).items():
        result[slug] = LessonState(
            status=LessonStatus(entry.get("status", "pending")),
            transcript_chars=entry.get("transcript_chars", 0),
            summarized_at=entry.get("summarized_at"),
            error=entry.get("error"),
        )
    return result


def save_state(output_dir: Path, course_slug: str, course_url: str, states: dict[str, LessonState]) -> None:
    path = state_file(output_dir, course_slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    lessons_data = {}
    for slug, s in states.items():
        entry = {"status": s.status.value, "transcript_chars": s.transcript_chars}
        if s.summarized_at:
            entry["summarized_at"] = s.summarized_at
        if s.error:
            entry["error"] = s.error
        lessons_data[slug] = entry
    path.write_text(json.dumps({
        "course_url": course_url,
        "course_slug": course_slug,
        "lessons": lessons_data,
    }, indent=2), encoding="utf-8")
