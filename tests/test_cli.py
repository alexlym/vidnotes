import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from vidnotes.cli import app
from vidnotes.models import Lesson, LessonContent

runner = CliRunner()

YT_URL = "https://www.youtube.com/watch?v=96jN2OCOfLs"
DL_URL = "https://learn.deeplearning.ai/courses/build-and-train-an-llm-with-jax"


def _yt_lesson():
    return Lesson(
        id="96jN2OCOfLs",
        slug="96jN2OCOfLs",
        title="Test Video",
        course_slug="test-channel/test-video",
        url=YT_URL,
    )


def _yt_content(lesson):
    return LessonContent(
        lesson=lesson,
        transcript="[0:00] Hello\n[1:00] World",
        page_text=None,
        source="yt-transcript",
    )


def _dl_lesson():
    return Lesson(
        id="intro",
        slug="intro",
        title="Introduction",
        course_slug="build-and-train-an-llm-with-jax",
        url=DL_URL + "/lesson/1",
    )


def _dl_content(lesson):
    return LessonContent(
        lesson=lesson,
        transcript="Welcome to the course.",
        page_text=None,
        source="next-data",
    )


# --- YouTube: dry-run ---

def test_yt_dry_run_exits_zero(tmp_path):
    lesson = _yt_lesson()
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)):
        result = runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0


def test_yt_dry_run_shows_title(tmp_path):
    lesson = _yt_lesson()
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)):
        result = runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path), "--dry-run"])
    assert "Test Video" in result.output


def test_yt_dry_run_shows_channel(tmp_path):
    lesson = _yt_lesson()
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)):
        result = runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path), "--dry-run"])
    assert "Test Channel" in result.output


def test_yt_dry_run_shows_transcript_preview(tmp_path):
    lesson = _yt_lesson()
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)):
        result = runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path), "--dry-run"])
    assert "Hello" in result.output


def test_yt_dry_run_does_not_write_file(tmp_path):
    lesson = _yt_lesson()
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)):
        runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path), "--dry-run"])
    assert not any(tmp_path.rglob("*.md"))


def test_yt_dry_run_does_not_call_claude(tmp_path):
    lesson = _yt_lesson()
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)), \
         patch("vidnotes.cli.summarize_youtube") as mock_summarize:
        runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path), "--dry-run"])
    mock_summarize.assert_not_called()


# --- YouTube: full run ---

def test_yt_full_run_writes_output_file(tmp_path):
    lesson = _yt_lesson()
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)), \
         patch("vidnotes.cli.summarize_youtube", return_value="## Timeline\n- x\n\n## Topics\n#### T\n- y"):
        runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path)])
    out = tmp_path / "test-channel" / "test-video" / "96jN2OCOfLs.md"
    assert out.exists()


def test_yt_full_run_output_contains_timeline(tmp_path):
    lesson = _yt_lesson()
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)), \
         patch("vidnotes.cli.summarize_youtube", return_value="## Timeline\n- x\n\n## Topics\n#### T\n- y"):
        runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path)])
    text = (tmp_path / "test-channel" / "test-video" / "96jN2OCOfLs.md").read_text()
    assert "Timeline" in text


def test_yt_full_run_output_contains_topics(tmp_path):
    lesson = _yt_lesson()
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)), \
         patch("vidnotes.cli.summarize_youtube", return_value="## Timeline\n- x\n\n## Topics\n#### T\n- y"):
        runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path)])
    text = (tmp_path / "test-channel" / "test-video" / "96jN2OCOfLs.md").read_text()
    assert "Topics" in text


def test_yt_full_run_does_not_generate_course_summary(tmp_path):
    lesson = _yt_lesson()
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)), \
         patch("vidnotes.cli.summarize_youtube", return_value="## Timeline\n- x"), \
         patch("vidnotes.cli.summarize_course") as mock_course:
        runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path)])
    mock_course.assert_not_called()


# --- YouTube: resume / force ---

def _write_state(tmp_path, status="summarized"):
    state_file = tmp_path / "test-channel" / "test-video" / ".state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps({
        "course_url": YT_URL,
        "course_slug": "test-channel/test-video",
        "lessons": {"96jN2OCOfLs": {"status": status, "transcript_chars": 20}},
    }))
    out = tmp_path / "test-channel" / "test-video" / "96jN2OCOfLs.md"
    out.write_text("existing summary")


def test_yt_resume_skips_already_done(tmp_path):
    lesson = _yt_lesson()
    _write_state(tmp_path)
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.summarize_youtube") as mock_summarize:
        result = runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path)])
    assert "already done" in result.output
    mock_summarize.assert_not_called()


def test_yt_force_resumes(tmp_path):
    lesson = _yt_lesson()
    _write_state(tmp_path)
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)), \
         patch("vidnotes.cli.summarize_youtube", return_value="## Timeline\nnew\n\n## Topics\nnew"):
        runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path), "--force"])
    text = (tmp_path / "test-channel" / "test-video" / "96jN2OCOfLs.md").read_text()
    assert "existing summary" not in text


def test_yt_refetch_clears_transcript_cache(tmp_path):
    lesson = _yt_lesson()
    _write_state(tmp_path)
    cache_dir = tmp_path / "test-channel" / "test-video" / ".transcripts"
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "96jN2OCOfLs.txt").write_text("old transcript")
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)), \
         patch("vidnotes.cli.summarize_youtube", return_value="new"):
        runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path), "--refetch"])
    assert not cache_dir.exists()


# --- YouTube: error cases ---

def test_yt_no_content_skips_gracefully(tmp_path):
    lesson = _yt_lesson()
    empty = LessonContent(lesson=lesson, transcript=None, page_text=None, source="none")
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=empty), \
         patch("vidnotes.cli.summarize_youtube") as mock_summarize:
        result = runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    mock_summarize.assert_not_called()


# --- DL.ai routing ---

def test_dl_dry_run_exits_zero(tmp_path):
    lesson = _dl_lesson()
    with patch("vidnotes.cli.get_session", return_value=MagicMock()), \
         patch("vidnotes.cli.get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.extract_content", return_value=_dl_content(lesson)):
        result = runner.invoke(app, ["run", DL_URL, "--output-dir", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0


def test_dl_dry_run_shows_lesson_title(tmp_path):
    lesson = _dl_lesson()
    with patch("vidnotes.cli.get_session", return_value=MagicMock()), \
         patch("vidnotes.cli.get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.extract_content", return_value=_dl_content(lesson)):
        result = runner.invoke(app, ["run", DL_URL, "--output-dir", str(tmp_path), "--dry-run"])
    assert "Introduction" in result.output


def test_dl_full_run_writes_output(tmp_path):
    lesson = _dl_lesson()
    with patch("vidnotes.cli.get_session", return_value=MagicMock()), \
         patch("vidnotes.cli.get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.extract_content", return_value=_dl_content(lesson)), \
         patch("vidnotes.cli.summarize", return_value="## Overview\nGreat."), \
         patch("vidnotes.cli.summarize_course", return_value="# Course Summary"):
        result = runner.invoke(app, ["run", DL_URL, "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    out = tmp_path / "build-and-train-an-llm-with-jax" / "intro.md"
    assert out.exists()


def test_dl_full_run_does_not_call_summarize_youtube(tmp_path):
    lesson = _dl_lesson()
    with patch("vidnotes.cli.get_session", return_value=MagicMock()), \
         patch("vidnotes.cli.get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.extract_content", return_value=_dl_content(lesson)), \
         patch("vidnotes.cli.summarize", return_value="## Overview\nGreat."), \
         patch("vidnotes.cli.summarize_course", return_value="# Course Summary"), \
         patch("vidnotes.cli.summarize_youtube") as mock_yt:
        runner.invoke(app, ["run", DL_URL, "--output-dir", str(tmp_path)])
    mock_yt.assert_not_called()


# --- Translation: CLI tests (T5–T8, T11) ---

def _write_yt_summary(tmp_path):
    """Write a pre-existing summary for the YT test lesson."""
    out = tmp_path / "test-channel" / "test-video" / "96jN2OCOfLs.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("# Summary\nHello world.")
    return out


# T5 — vidnotes translate <slug> ua translates all existing summaries

def test_translate_cmd_translates_existing_summaries(tmp_path):
    _write_yt_summary(tmp_path)
    with patch("vidnotes.cli.translate", return_value="# Переклад") as mock_translate:
        result = runner.invoke(app, ["translate", "test-channel/test-video", "ua",
                                     "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    mock_translate.assert_called_once()
    dest = tmp_path / "test-channel" / "test-video" / "ua" / "96jN2OCOfLs.md"
    assert dest.exists()
    assert dest.read_text() == "# Переклад"


# T6 — vidnotes run <url> --translate ua summarizes then translates

def test_run_with_translate_calls_translate_after_summarize(tmp_path):
    lesson = _yt_lesson()
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)), \
         patch("vidnotes.cli.summarize_youtube", return_value="## Timeline\n- x"), \
         patch("vidnotes.cli.translate", return_value="## Хронологія\n- x") as mock_translate:
        result = runner.invoke(app, ["run", YT_URL, "--translate", "ua",
                                     "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    mock_translate.assert_called_once()
    dest = tmp_path / "test-channel" / "test-video" / "ua" / "96jN2OCOfLs.md"
    assert dest.exists()


# T7 — --force on translate command re-translates already-translated files

def test_translate_cmd_force_overwrites(tmp_path):
    _write_yt_summary(tmp_path)
    dest = tmp_path / "test-channel" / "test-video" / "ua" / "96jN2OCOfLs.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("# Old")

    with patch("vidnotes.cli.translate", return_value="# New") as mock_translate:
        runner.invoke(app, ["translate", "test-channel/test-video", "ua", "--force",
                            "--output-dir", str(tmp_path)])
    mock_translate.assert_called_once()
    assert dest.read_text() == "# New"


# T8 — plain language name passed through without error

def test_translate_cmd_accepts_plain_language_name(tmp_path):
    _write_yt_summary(tmp_path)
    with patch("vidnotes.cli.translate", return_value="# Переклад"):
        result = runner.invoke(app, ["translate", "test-channel/test-video", "ukrainian",
                                     "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "Unknown language" not in result.output


# T11 — full pipeline: fetch → summarize → translate in one run

def test_run_translate_full_pipeline_creates_both_files(tmp_path):
    lesson = _yt_lesson()
    with patch("vidnotes.cli.yt_get_lessons", return_value=[lesson]), \
         patch("vidnotes.cli.yt_extract_content", return_value=_yt_content(lesson)), \
         patch("vidnotes.cli.summarize_youtube", return_value="## Timeline\n- x"), \
         patch("vidnotes.cli.translate", return_value="## Хронологія\n- x"):
        result = runner.invoke(app, ["run", YT_URL, "--translate", "ua",
                                     "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    original = tmp_path / "test-channel" / "test-video" / "96jN2OCOfLs.md"
    translated = tmp_path / "test-channel" / "test-video" / "ua" / "96jN2OCOfLs.md"
    assert original.exists()
    assert translated.exists()
