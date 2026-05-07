import json
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vidnotes.models import Lesson
from vidnotes.youtube import (
    _parse_vtt,
    _slugify,
    extract_content,
    get_lessons,
    is_youtube_url,
)

# --- is_youtube_url ---

def test_watch_url():
    assert is_youtube_url("https://www.youtube.com/watch?v=96jN2OCOfLs")

def test_shorts_url():
    assert is_youtube_url("https://www.youtube.com/shorts/abc123")

def test_youtu_be_url():
    assert is_youtube_url("https://youtu.be/96jN2OCOfLs")

def test_non_youtube_url():
    assert not is_youtube_url("https://learn.deeplearning.ai/courses/some-course")

def test_random_url():
    assert not is_youtube_url("https://www.google.com")


# --- _slugify ---

def test_slugify_basic():
    assert _slugify("Hello World") == "hello-world"

def test_slugify_special_chars():
    result = _slugify("C++ Programming: A Guide!")
    assert "+" not in result
    assert ":" not in result
    assert "!" not in result

def test_slugify_truncates_at_60():
    assert len(_slugify("a" * 100)) <= 60

def test_slugify_collapses_whitespace():
    assert _slugify("  foo   bar  ") == "foo-bar"

def test_slugify_no_trailing_dash():
    result = _slugify("hello world!")
    assert not result.endswith("-")


# --- _parse_vtt ---

SAMPLE_VTT = textwrap.dedent("""\
    WEBVTT
    Kind: captions
    Language: en

    1
    00:00:00.000 --> 00:00:02.000
    Hello, welcome to this video.

    2
    00:00:02.000 --> 00:00:04.000
    Hello, welcome to this video.

    3
    00:00:04.000 --> 00:00:06.500
    Today we cover <b>machine learning</b> basics.

    4
    00:00:10.000 --> 00:00:12.000
    Let's get started.
""")

def test_parse_vtt_includes_timestamps():
    result = _parse_vtt(SAMPLE_VTT)
    assert "[0:00]" in result

def test_parse_vtt_deduplicates_adjacent():
    result = _parse_vtt(SAMPLE_VTT)
    assert result.count("Hello, welcome to this video.") == 1

def test_parse_vtt_strips_html_tags():
    result = _parse_vtt(SAMPLE_VTT)
    assert "<b>" not in result
    assert "machine learning" in result

def test_parse_vtt_produces_multiple_lines():
    result = _parse_vtt(SAMPLE_VTT)
    assert len(result.splitlines()) >= 3

def test_parse_vtt_skips_webvtt_header():
    result = _parse_vtt(SAMPLE_VTT)
    assert "WEBVTT" not in result
    assert "Kind:" not in result

def test_parse_vtt_hour_offset():
    vtt = textwrap.dedent("""\
        WEBVTT

        01:05:30.000 --> 01:05:32.000
        Deep in the video.
    """)
    result = _parse_vtt(vtt)
    assert "[65:30]" in result


# --- get_lessons ---

_YT_DLP_JSON = json.dumps({
    "id": "96jN2OCOfLs",
    "title": "Test Video Title",
    "channel": "Test Channel",
    "uploader": "Test Channel",
})

def test_get_lessons_returns_one_lesson():
    with patch("vidnotes.youtube.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=_YT_DLP_JSON, stderr="")
        lessons = get_lessons("https://www.youtube.com/watch?v=96jN2OCOfLs")
    assert len(lessons) == 1

def test_get_lessons_video_id():
    with patch("vidnotes.youtube.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=_YT_DLP_JSON, stderr="")
        lesson = get_lessons("https://www.youtube.com/watch?v=96jN2OCOfLs")[0]
    assert lesson.id == "96jN2OCOfLs"
    assert lesson.slug == "96jN2OCOfLs"

def test_get_lessons_title():
    with patch("vidnotes.youtube.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=_YT_DLP_JSON, stderr="")
        lesson = get_lessons("https://www.youtube.com/watch?v=96jN2OCOfLs")[0]
    assert lesson.title == "Test Video Title"

def test_get_lessons_course_slug_format():
    with patch("vidnotes.youtube.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=_YT_DLP_JSON, stderr="")
        lesson = get_lessons("https://www.youtube.com/watch?v=96jN2OCOfLs")[0]
    assert lesson.course_slug == "test-channel/test-video-title"

def test_get_lessons_yt_dlp_not_found():
    import click
    with patch("vidnotes.youtube.subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(click.exceptions.Exit):
            get_lessons("https://www.youtube.com/watch?v=abc")

def test_get_lessons_yt_dlp_error():
    import click
    import subprocess
    with patch("vidnotes.youtube.subprocess.run",
               side_effect=subprocess.CalledProcessError(1, "yt-dlp", stderr="Video unavailable")):
        with pytest.raises(click.exceptions.Exit):
            get_lessons("https://www.youtube.com/watch?v=abc")


# --- extract_content ---

def _make_lesson():
    return Lesson(
        id="96jN2OCOfLs",
        slug="96jN2OCOfLs",
        title="Test Video",
        course_slug="test-channel/test-video",
        url="https://youtube.com/watch?v=96jN2OCOfLs",
    )


def test_extract_content_returns_cached(tmp_path):
    lesson = _make_lesson()
    td = tmp_path / "test-channel" / "test-video" / ".transcripts"
    td.mkdir(parents=True)
    (td / f"{lesson.slug}.txt").write_text("cached transcript")
    content = extract_content(lesson, tmp_path)
    assert content.source == "cached"
    assert content.transcript == "cached transcript"

def test_extract_content_from_vtt(tmp_path):
    lesson = _make_lesson()
    with patch("vidnotes.youtube.subprocess.run") as mock_run, \
         patch("vidnotes.youtube.tempfile.mkdtemp") as mock_tmp, \
         patch("vidnotes.youtube.shutil.rmtree"):
        tmpdir = str(tmp_path / "tmp")
        Path(tmpdir).mkdir()
        mock_tmp.return_value = tmpdir
        mock_run.return_value = MagicMock(returncode=0)
        (Path(tmpdir) / f"{lesson.id}.en.vtt").write_text(SAMPLE_VTT)
        content = extract_content(lesson, tmp_path)
    assert content.source == "yt-transcript"
    assert content.transcript is not None
    assert "[0:00]" in content.transcript

def test_extract_content_vtt_is_cached(tmp_path):
    lesson = _make_lesson()
    with patch("vidnotes.youtube.subprocess.run") as mock_run, \
         patch("vidnotes.youtube.tempfile.mkdtemp") as mock_tmp, \
         patch("vidnotes.youtube.shutil.rmtree"):
        tmpdir = str(tmp_path / "tmp")
        Path(tmpdir).mkdir()
        mock_tmp.return_value = tmpdir
        mock_run.return_value = MagicMock(returncode=0)
        (Path(tmpdir) / f"{lesson.id}.en.vtt").write_text(SAMPLE_VTT)
        extract_content(lesson, tmp_path)
    cache = tmp_path / "test-channel" / "test-video" / ".transcripts" / f"{lesson.slug}.txt"
    assert cache.exists()

def test_extract_content_fallback_to_description(tmp_path):
    lesson = _make_lesson()
    desc_json = json.dumps({"description": "A great video about machine learning."})
    with patch("vidnotes.youtube.subprocess.run") as mock_run, \
         patch("vidnotes.youtube.tempfile.mkdtemp") as mock_tmp, \
         patch("vidnotes.youtube.shutil.rmtree"):
        tmpdir = str(tmp_path / "tmp")
        Path(tmpdir).mkdir()
        mock_tmp.return_value = tmpdir
        mock_run.side_effect = [
            MagicMock(returncode=0),
            MagicMock(returncode=0, stdout=desc_json),
        ]
        content = extract_content(lesson, tmp_path)
    assert content.source == "yt-description"
    assert "machine learning" in content.transcript

def test_extract_content_source_none_when_nothing_found(tmp_path):
    lesson = _make_lesson()
    with patch("vidnotes.youtube.subprocess.run") as mock_run, \
         patch("vidnotes.youtube.tempfile.mkdtemp") as mock_tmp, \
         patch("vidnotes.youtube.shutil.rmtree"):
        tmpdir = str(tmp_path / "tmp")
        Path(tmpdir).mkdir()
        mock_tmp.return_value = tmpdir
        mock_run.side_effect = [
            MagicMock(returncode=0),
            MagicMock(returncode=1, stdout=""),
        ]
        content = extract_content(lesson, tmp_path)
    assert content.source == "none"
    assert content.transcript is None
