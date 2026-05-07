import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from .catalog import get_lessons
from .config import SESSION_FILE, Settings, transcripts_dir
from .extractor import extract_content
from .models import LessonState, LessonStatus
from .session import get_session, load_session, login, validate_session
from .summarizer import load_prompt_template, summarize, summarize_course, summarize_youtube
from .translator import _EXAMPLES, translate, translated_output_path, validate_language
from .writer import (
    load_state,
    load_transcript,
    output_path,
    save_state,
    write_summary,
)
from .youtube import extract_content as yt_extract_content
from .youtube import get_lessons as yt_get_lessons
from .youtube import is_youtube_url

app = typer.Typer(help="Summarize video courses and YouTube videos into Markdown notes using Claude.")
auth_app = typer.Typer(help="Manage authentication.")
app.add_typer(auth_app, name="auth")

console = Console()
_CLAUDE_BIN = shutil.which("claude") or "claude"
_NOW = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@auth_app.command("login")
def auth_login():
    """Open a browser to log in and save the session."""
    login()
    console.print("[green]Login successful.[/green]")


@auth_app.command("status")
def auth_status():
    """Check whether the saved session is still valid."""
    session = load_session()
    if session is None:
        console.print(f"[red]No session found.[/red] Run [bold]vidnotes auth login[/bold] first.")
        raise typer.Exit(1)
    if validate_session(session):
        console.print(f"[green]Session is valid.[/green] (saved at {SESSION_FILE})")
    else:
        console.print("[yellow]Session has expired.[/yellow] Run [bold]vidnotes auth login[/bold] to refresh.")
        raise typer.Exit(1)


@app.command()
def run(
    course_url: Annotated[str, typer.Argument(help="Full URL of the course or YouTube video to summarize")],
    output_dir: Annotated[Path | None, typer.Option(help="Directory to write summaries")] = None,
    lesson: Annotated[str | None, typer.Option(help="Only process this lesson (slug or partial title)")] = None,
    force: Annotated[bool, typer.Option(help="Re-generate summaries (uses cached transcripts)")] = False,
    refetch: Annotated[bool, typer.Option(help="Re-download transcripts and re-generate summaries")] = False,
    dry_run: Annotated[bool, typer.Option(help="Extract content but skip Claude call")] = False,
    translate_lang: Annotated[str | None, typer.Option("--translate", help="Translate summaries into this language after summarizing (e.g. ua, de, polish)")] = None,
):
    settings = Settings.load()
    if output_dir is not None:
        settings.output_dir = output_dir

    if translate_lang is not None and validate_language(translate_lang) is None:
        console.print(f"[red]Unknown language:[/red] [bold]{translate_lang}[/bold]")
        console.print(f"Use a BCP-47 code or plain name, e.g.: {_EXAMPLES}")
        raise typer.Exit(1)

    console.print(f"[bold]vidnotes[/bold] — {course_url}")

    is_yt = is_youtube_url(course_url)

    if is_yt:
        console.print("Fetching video info...")
        lessons = yt_get_lessons(course_url)
        _extract = lambda l: yt_extract_content(l, settings.output_dir)
        _summarize = lambda content: summarize_youtube(content, _CLAUDE_BIN)
    else:
        session = get_session()
        console.print("[green]Authenticated.[/green]")
        console.print("Fetching lesson list...")
        lessons = get_lessons(course_url, session)
        template = load_prompt_template()
        _extract = lambda l: extract_content(l, session, settings.output_dir)
        _summarize = lambda content: summarize(content, template, _CLAUDE_BIN)

    if not lessons:
        console.print("[red]No lessons found. Check the URL and try again.[/red]")
        raise typer.Exit(1)

    if lesson:
        slug = lesson.lower()
        lessons = [l for l in lessons if slug in l.slug.lower() or slug in l.title.lower()]
        if not lessons:
            console.print(f"[red]No lesson matching '{lesson}' found.[/red]")
            raise typer.Exit(1)

    course_slug = lessons[0].course_slug
    course_title = course_slug.replace("-", " ").title()
    console.print(f"Found [bold]{len(lessons)}[/bold] lesson(s).\n")

    # Load state
    states = load_state(settings.output_dir, course_slug)

    # Wipe transcript cache on --refetch
    if refetch:
        td = transcripts_dir(settings.output_dir, course_slug)
        if td.exists():
            shutil.rmtree(td)
            console.print("[dim]Transcript cache cleared.[/dim]")
        for s in states.values():
            if s.status != LessonStatus.SUMMARIZED or refetch:
                s.status = LessonStatus.PENDING

    if dry_run:
        console.print("[bold]Extracting content (dry run — no summaries):[/bold]\n")
        for i, l in enumerate(lessons, 1):
            content = _extract(l)
            preview_len = 300 if is_yt else 200
            preview = (content.transcript or content.page_text or "")[:preview_len]
            console.print(f"  {i:2}. [cyan]{l.title}[/cyan] [{content.source}]")
            if is_yt:
                channel = l.course_slug.split('/')[0].replace('-', ' ').title()
                console.print(f"      Channel: {channel}")
            console.print(f"      {preview}{'...' if len(preview) == preview_len else ''}\n")
        return

    done, skipped, failed = 0, 0, 0
    total = len(lessons)

    for i, l in enumerate(lessons, 1):
        state = states.get(l.slug, LessonState())
        path = output_path(settings.output_dir, l)

        already_summarized = state.status == LessonStatus.SUMMARIZED and path.exists()
        has_transcript = (
            state.status == LessonStatus.TRANSCRIPT_SAVED
            or load_transcript(settings.output_dir, l) is not None
        )

        if already_summarized and not force and not refetch:
            console.print(f"  [{i}/{total}] [dim]Skipping {l.title} (already done)[/dim]")
            skipped += 1
            continue

        action = "Re-summarizing" if has_transcript and not refetch else "Summarizing"
        console.print(f"  [{i}/{total}] {action} [cyan]{l.title}[/cyan]...", end=" ")

        try:
            content = _extract(l)

            if not content.transcript and not content.page_text:
                console.print("[yellow]no content, skipped[/yellow]")
                state.status = LessonStatus.FAILED
                state.error = "no content found"
                states[l.slug] = state
                save_state(settings.output_dir, course_slug, course_url, states)
                skipped += 1
                continue

            state.transcript_chars = len(content.transcript or content.page_text or "")
            state.status = LessonStatus.TRANSCRIPT_SAVED
            states[l.slug] = state
            save_state(settings.output_dir, course_slug, course_url, states)

            body = _summarize(content)
            write_summary(path, l, content, body)

            state.status = LessonStatus.SUMMARIZED
            state.summarized_at = _NOW()
            state.error = None
            states[l.slug] = state
            save_state(settings.output_dir, course_slug, course_url, states)

            console.print("[green]✓[/green]")
            done += 1

        except Exception as e:
            console.print(f"[red]✗ {e}[/red]")
            state.status = LessonStatus.FAILED
            state.error = str(e)
            states[l.slug] = state
            save_state(settings.output_dir, course_slug, course_url, states)
            failed += 1

    out_path = (settings.output_dir / course_slug).resolve()
    console.print(f"\nDone: [green]{done}[/green] summarized, [dim]{skipped}[/dim] skipped, [red]{failed}[/red] failed.")
    console.print(f"Output: {out_path}")

    if is_yt:
        if translate_lang:
            _run_translation(settings.output_dir, lessons, translate_lang, force)
        return

    # Course summary (deeplearning.ai only)
    all_summarized = all(
        states.get(l.slug, LessonState()).status == LessonStatus.SUMMARIZED
        for l in lessons
    )
    if not all_summarized and done == 0:
        return

    if failed > 0:
        console.print(f"[yellow]Skipping course summary — {failed} lesson(s) failed. Fix and re-run.[/yellow]")
        return

    console.print("\nGenerating course summary...")
    lessons_with_transcripts = []
    for l in lessons:
        t = load_transcript(settings.output_dir, l)
        if t:
            lessons_with_transcripts.append((l, t))

    course_summary_path = settings.output_dir / course_slug / "_course_summary.md"
    if lessons_with_transcripts:
        try:
            body = summarize_course(lessons_with_transcripts, course_title, _CLAUDE_BIN)
            course_summary_path.write_text(body, encoding="utf-8")
            console.print(f"[green]✓[/green] Course summary → {course_summary_path}")
        except Exception as e:
            console.print(f"[red]Course summary failed: {e}[/red]")
            course_summary_path = None

    if translate_lang:
        _run_translation(settings.output_dir, lessons, translate_lang, force, course_summary_path)


def _run_translation(
    output_dir: Path,
    lessons: list,
    lang: str,
    force: bool,
    course_summary_path: Path | None = None,
) -> None:
    console.print(f"\nTranslating to [bold]{lang}[/bold]...")
    t_done, t_skipped, t_failed = 0, 0, 0

    for lesson in lessons:
        src = output_path(output_dir, lesson)
        if not src.exists():
            console.print(f"  [yellow]⚠ {lesson.title} — no summary found, skipping[/yellow]")
            t_skipped += 1
            continue

        dest = translated_output_path(output_dir, lesson, lang)
        if dest.exists() and not force:
            console.print(f"  [dim]Skipping {lesson.title} (already translated)[/dim]")
            t_skipped += 1
            continue

        console.print(f"  Translating [cyan]{lesson.title}[/cyan]...", end=" ")
        try:
            body = translate(src.read_text(encoding="utf-8"), lang, _CLAUDE_BIN)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(body, encoding="utf-8")
            console.print("[green]✓[/green]")
            t_done += 1
        except Exception as e:
            console.print(f"[red]✗ {e}[/red]")
            t_failed += 1

    if course_summary_path and course_summary_path.exists():
        dest = course_summary_path.parent / lang / "_course_summary.md"
        if dest.exists() and not force:
            console.print(f"  [dim]Skipping course summary (already translated)[/dim]")
            t_skipped += 1
        else:
            console.print(f"  Translating [cyan]course summary[/cyan]...", end=" ")
            try:
                body = translate(course_summary_path.read_text(encoding="utf-8"), lang, _CLAUDE_BIN)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(body, encoding="utf-8")
                console.print("[green]✓[/green]")
                t_done += 1
            except Exception as e:
                console.print(f"[red]✗ {e}[/red]")
                t_failed += 1

    console.print(f"Translation: [green]{t_done}[/green] done, [dim]{t_skipped}[/dim] skipped, [red]{t_failed}[/red] failed.")


@app.command()
def translate_cmd(
    course: Annotated[str, typer.Argument(help="Course slug or URL to translate")],
    lang: Annotated[str, typer.Argument(help="Target language (BCP-47 code or plain name, e.g. ua, de, polish)")],
    output_dir: Annotated[Path | None, typer.Option(help="Directory where summaries are stored")] = None,
    force: Annotated[bool, typer.Option(help="Re-translate even if output already exists")] = False,
):
    """Translate existing summaries for a course or video into another language."""
    settings = Settings.load()
    if output_dir is not None:
        settings.output_dir = output_dir

    if validate_language(lang) is None:
        console.print(f"[red]Unknown language:[/red] [bold]{lang}[/bold]")
        console.print(f"Use a BCP-47 code or plain name, e.g.: {_EXAMPLES}")
        raise typer.Exit(1)

    # Resolve course slug from URL or treat as slug directly
    if course.startswith("http"):
        if is_youtube_url(course):
            lessons = yt_get_lessons(course)
        else:
            session = get_session()
            lessons = get_lessons(course, session)
        if not lessons:
            console.print("[red]No lessons found for that URL.[/red]")
            raise typer.Exit(1)
        course_slug = lessons[0].course_slug
    else:
        course_slug = course
        course_dir = settings.output_dir / course_slug
        if not course_dir.exists():
            console.print(f"[red]Course directory not found:[/red] {course_dir}")
            raise typer.Exit(1)
        # Build minimal lesson stubs from existing summary files
        lessons = _lessons_from_dir(course_dir, course_slug)

    course_summary_path = settings.output_dir / course_slug / "_course_summary.md"
    _run_translation(
        settings.output_dir,
        lessons,
        lang,
        force,
        course_summary_path if course_summary_path.exists() else None,
    )


def _lessons_from_dir(course_dir: Path, course_slug: str):
    """Build minimal Lesson-like objects from .md files in a course directory."""
    from .models import Lesson
    lessons = []
    for md in sorted(course_dir.glob("*.md")):
        if md.name.startswith("_"):
            continue
        slug = md.stem
        lessons.append(Lesson(
            id=slug, slug=slug,
            title=slug.replace("-", " ").title(),
            course_slug=course_slug,
            url="",
        ))
    return lessons


app.command("translate")(translate_cmd)
