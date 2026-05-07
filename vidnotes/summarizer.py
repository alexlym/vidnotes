import shutil
import subprocess
from pathlib import Path

from .config import DEFAULT_PROMPT_FILE, PROMPTS_DIR
from .models import LessonContent

_PACKAGE_DEFAULT = Path(__file__).parent / "default_prompt.md"
_PACKAGE_COURSE_PROMPT = Path(__file__).parent / "course_prompt.md"
_PACKAGE_YOUTUBE_PROMPT = Path(__file__).parent / "youtube_prompt.md"
_COURSE_PROMPT_FILE = PROMPTS_DIR / "course_summary.md"
_YOUTUBE_PROMPT_FILE = PROMPTS_DIR / "youtube_summary.md"

_MAX_TRANSCRIPT_CHARS = 150_000


def _ensure_prompt_file() -> Path:
    if not DEFAULT_PROMPT_FILE.exists():
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(_PACKAGE_DEFAULT, DEFAULT_PROMPT_FILE)
    return DEFAULT_PROMPT_FILE


def _ensure_course_prompt_file() -> Path:
    if not _COURSE_PROMPT_FILE.exists():
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(_PACKAGE_COURSE_PROMPT, _COURSE_PROMPT_FILE)
    return _COURSE_PROMPT_FILE


def load_prompt_template() -> str:
    return _ensure_prompt_file().read_text()


def _build_prompt(content: LessonContent, template: str) -> str:
    transcript = content.transcript or ""
    if len(transcript) > _MAX_TRANSCRIPT_CHARS:
        transcript = transcript[:_MAX_TRANSCRIPT_CHARS] + "\n[transcript truncated]"
    return template.format(
        course_title=content.lesson.course_slug.replace("-", " ").title(),
        lesson_title=content.lesson.title,
        transcript=transcript,
        page_text=content.page_text or "(none)",
    )


def _ensure_youtube_prompt_file() -> Path:
    if not _YOUTUBE_PROMPT_FILE.exists():
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(_PACKAGE_YOUTUBE_PROMPT, _YOUTUBE_PROMPT_FILE)
    return _YOUTUBE_PROMPT_FILE


def summarize(content: LessonContent, template: str, claude_bin: str = "claude") -> str:
    prompt = _build_prompt(content, template)
    result = subprocess.run([claude_bin, "-p", prompt], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def summarize_youtube(content: LessonContent, claude_bin: str = "claude") -> str:
    template = _ensure_youtube_prompt_file().read_text()
    transcript = content.transcript or ""
    if len(transcript) > _MAX_TRANSCRIPT_CHARS:
        transcript = transcript[:_MAX_TRANSCRIPT_CHARS] + "\n[transcript truncated]"
    channel = content.lesson.course_slug.split('/')[0].replace('-', ' ').title()
    prompt = (template
              .replace('{title}', content.lesson.title)
              .replace('{channel}', channel)
              .replace('{transcript}', transcript))
    result = subprocess.run([claude_bin, '-p', prompt], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def summarize_course(lessons_with_transcripts: list[tuple], course_title: str, claude_bin: str = "claude") -> str:
    """Generate a whole-course summary from all lesson transcripts.

    lessons_with_transcripts: list of (lesson, transcript_text) tuples in order.
    """
    template = _ensure_course_prompt_file().read_text()

    # Build combined transcript block, truncating proportionally if too long
    total_chars = sum(len(t) for _, t in lessons_with_transcripts)
    per_lesson_limit = (
        _MAX_TRANSCRIPT_CHARS // len(lessons_with_transcripts)
        if total_chars > _MAX_TRANSCRIPT_CHARS
        else None
    )

    blocks = []
    for lesson, transcript in lessons_with_transcripts:
        text = transcript[:per_lesson_limit] if per_lesson_limit else transcript
        blocks.append(f"## {lesson.title}\n{text}")

    combined = "\n\n".join(blocks)
    # Use simple replacement — template may contain {slug} etc. as Claude instructions
    prompt = template.replace("{course_title}", course_title).replace("{lesson_transcripts}", combined)

    result = subprocess.run([claude_bin, "-p", prompt], capture_output=True, text=True, check=True)
    return result.stdout.strip()
