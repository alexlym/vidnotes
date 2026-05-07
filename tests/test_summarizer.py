from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vidnotes.models import Lesson, LessonContent
from vidnotes.summarizer import summarize_youtube

_YOUTUBE_PROMPT_SRC = Path(__file__).parent.parent / "vidnotes" / "youtube_prompt.md"


def _make_content(transcript="[0:00] Hello world\n[1:00] More content"):
    lesson = Lesson(
        id="96jN2OCOfLs",
        slug="96jN2OCOfLs",
        title="Test Video",
        course_slug="test-channel/test-video",
        url="https://youtube.com/watch?v=96jN2OCOfLs",
    )
    return LessonContent(
        lesson=lesson,
        transcript=transcript,
        page_text=None,
        source="yt-transcript",
    )


def test_summarize_youtube_passes_title_to_prompt(tmp_path):
    prompt_file = tmp_path / "youtube_summary.md"
    prompt_file.write_text(_YOUTUBE_PROMPT_SRC.read_text())
    content = _make_content()
    with patch("vidnotes.summarizer._YOUTUBE_PROMPT_FILE", prompt_file), \
         patch("vidnotes.summarizer.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="## Timeline\n- done\n\n## Topics\n#### T\n- x", returncode=0)
        summarize_youtube(content, claude_bin="claude")
    prompt = mock_run.call_args[0][0][-1]
    assert "Test Video" in prompt


def test_summarize_youtube_passes_channel_to_prompt(tmp_path):
    prompt_file = tmp_path / "youtube_summary.md"
    prompt_file.write_text(_YOUTUBE_PROMPT_SRC.read_text())
    content = _make_content()
    with patch("vidnotes.summarizer._YOUTUBE_PROMPT_FILE", prompt_file), \
         patch("vidnotes.summarizer.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="summary", returncode=0)
        summarize_youtube(content, claude_bin="claude")
    prompt = mock_run.call_args[0][0][-1]
    assert "Test Channel" in prompt


def test_summarize_youtube_returns_claude_output(tmp_path):
    prompt_file = tmp_path / "youtube_summary.md"
    prompt_file.write_text(_YOUTUBE_PROMPT_SRC.read_text())
    content = _make_content()
    with patch("vidnotes.summarizer._YOUTUBE_PROMPT_FILE", prompt_file), \
         patch("vidnotes.summarizer.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="  the summary  ", returncode=0)
        result = summarize_youtube(content, claude_bin="claude")
    assert result == "the summary"


def test_summarize_youtube_truncates_long_transcript(tmp_path):
    prompt_file = tmp_path / "youtube_summary.md"
    prompt_file.write_text(_YOUTUBE_PROMPT_SRC.read_text())
    content = _make_content(transcript="x" * 200_000)
    with patch("vidnotes.summarizer._YOUTUBE_PROMPT_FILE", prompt_file), \
         patch("vidnotes.summarizer.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="summary", returncode=0)
        summarize_youtube(content, claude_bin="claude")
    prompt = mock_run.call_args[0][0][-1]
    assert "[transcript truncated]" in prompt


def test_summarize_youtube_creates_prompt_file_from_package(tmp_path):
    prompt_file = tmp_path / "youtube_summary.md"
    assert not prompt_file.exists()
    content = _make_content()
    with patch("vidnotes.summarizer._YOUTUBE_PROMPT_FILE", prompt_file), \
         patch("vidnotes.summarizer._PACKAGE_YOUTUBE_PROMPT", _YOUTUBE_PROMPT_SRC), \
         patch("vidnotes.summarizer.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="summary", returncode=0)
        summarize_youtube(content, claude_bin="claude")
    assert prompt_file.exists()
