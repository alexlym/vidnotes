import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import typer

from .models import Lesson, LessonContent
from .writer import load_transcript, save_transcript


def is_youtube_url(url: str) -> bool:
    return bool(re.search(r'(youtube\.com/(watch|shorts)|youtu\.be/)', url))


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text.strip())
    return text[:60].rstrip('-')


def _parse_vtt(text: str) -> str:
    timestamp_re = re.compile(r'^(\d+):(\d{2}):(\d{2})\.\d+ -->')
    lines = text.splitlines()
    result = []
    prev_text = None
    pending_ts = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(('WEBVTT', 'NOTE', 'STYLE', 'Kind:', 'Language:')):
            continue
        if re.match(r'^\d+$', stripped):
            continue

        m = timestamp_re.match(stripped)
        if m:
            h, mm, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
            pending_ts = f"[{h * 60 + mm}:{s:02d}]"
            continue

        clean = re.sub(r'<[^>]+>', '', stripped).strip()
        if not clean or clean == prev_text:
            continue

        if pending_ts:
            result.append(f"{pending_ts} {clean}")
            pending_ts = None
        else:
            result.append(clean)

        prev_text = clean

    return '\n'.join(result)


def get_lessons(url: str) -> list[Lesson]:
    try:
        proc = subprocess.run(
            ['yt-dlp', '--dump-json', '--no-warnings', url],
            capture_output=True, text=True, check=True,
        )
    except FileNotFoundError:
        typer.echo("Error: yt-dlp not found. Install it with: pip install yt-dlp", err=True)
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error: {e.stderr.strip() or 'yt-dlp failed to fetch video info'}", err=True)
        raise typer.Exit(1)

    info = json.loads(proc.stdout)
    video_id = info.get('id', 'unknown')
    title = info.get('title', 'Untitled')
    channel = info.get('channel') or info.get('uploader') or 'youtube'
    course_slug = f"{_slugify(channel)}/{_slugify(title)}"

    return [Lesson(
        id=video_id,
        slug=video_id,
        title=title,
        course_slug=course_slug,
        url=f"https://youtube.com/watch?v={video_id}",
    )]


def extract_content(lesson: Lesson, output_dir: Path) -> LessonContent:
    cached = load_transcript(output_dir, lesson)
    if cached:
        return LessonContent(lesson=lesson, transcript=cached, page_text=None, source="cached")

    tmpdir = tempfile.mkdtemp()
    try:
        subprocess.run(
            [
                'yt-dlp',
                '--write-subs', '--write-auto-subs',
                '--sub-langs', 'en.*',
                '--sub-format', 'vtt',
                '--skip-download',
                '--no-warnings',
                '-o', f"{tmpdir}/%(id)s",
                lesson.url,
            ],
            capture_output=True, text=True,
        )
        vtt_files = list(Path(tmpdir).glob('*.vtt'))
        if vtt_files:
            transcript = _parse_vtt(vtt_files[0].read_text(encoding='utf-8'))
            save_transcript(output_dir, lesson, transcript)
            return LessonContent(lesson=lesson, transcript=transcript, page_text=None, source="yt-transcript")

        # Fallback: use video description
        proc2 = subprocess.run(
            ['yt-dlp', '--dump-json', '--no-warnings', lesson.url],
            capture_output=True, text=True,
        )
        if proc2.returncode == 0:
            description = json.loads(proc2.stdout).get('description', '')
            if description:
                save_transcript(output_dir, lesson, description)
                return LessonContent(lesson=lesson, transcript=description, page_text=None, source="yt-description")

        return LessonContent(lesson=lesson, transcript=None, page_text=None, source="none")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
