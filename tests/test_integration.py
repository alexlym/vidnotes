"""
Integration tests — hit the real network.

Run with:
    pytest -m integration

YouTube tests require yt-dlp and internet access.
DL.ai tests also require a valid session: run `dl-summarizer auth login` first.
"""

import pytest
from typer.testing import CliRunner

from vidnotes.cli import app
from vidnotes.youtube import extract_content, get_lessons

runner = CliRunner()

YT_URL = "https://www.youtube.com/watch?v=96jN2OCOfLs"
DL_URL = "https://learn.deeplearning.ai/courses/build-and-train-an-llm-with-jax"


# --- YouTube ---

@pytest.mark.integration
def test_yt_dry_run_exits_zero(tmp_path):
    result = runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0, result.output


@pytest.mark.integration
def test_yt_dry_run_shows_channel(tmp_path):
    result = runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path), "--dry-run"])
    assert "Channel" in result.output


@pytest.mark.integration
def test_yt_dry_run_shows_transcript_preview(tmp_path):
    result = runner.invoke(app, ["run", YT_URL, "--output-dir", str(tmp_path), "--dry-run"])
    # A real transcript should have content beyond just headers
    assert len(result.output) > 200


@pytest.mark.integration
def test_yt_get_lessons_returns_real_video():
    lessons = get_lessons(YT_URL)
    assert len(lessons) == 1
    assert lessons[0].id == "96jN2OCOfLs"
    assert "/" in lessons[0].course_slug


@pytest.mark.integration
def test_yt_transcript_has_timestamps(tmp_path):
    lessons = get_lessons(YT_URL)
    content = extract_content(lessons[0], tmp_path)
    assert content.source in ("yt-transcript", "yt-description", "cached")
    assert content.transcript
    if content.source == "yt-transcript":
        assert "[" in content.transcript


@pytest.mark.integration
def test_yt_transcript_is_cached_on_second_call(tmp_path):
    lessons = get_lessons(YT_URL)
    extract_content(lessons[0], tmp_path)
    content2 = extract_content(lessons[0], tmp_path)
    assert content2.source == "cached"


@pytest.mark.integration
def test_yt_output_path_has_channel_and_video_slug(tmp_path):
    lessons = get_lessons(YT_URL)
    parts = lessons[0].course_slug.split("/")
    assert len(parts) == 2
    assert parts[0]  # channel slug non-empty
    assert parts[1]  # video slug non-empty


# --- DL.ai (requires valid session) ---

@pytest.mark.integration
@pytest.mark.requires_auth
def test_dl_dry_run_exits_zero(tmp_path):
    result = runner.invoke(app, ["run", DL_URL, "--output-dir", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0, result.output


@pytest.mark.integration
@pytest.mark.requires_auth
def test_dl_dry_run_shows_lessons(tmp_path):
    result = runner.invoke(app, ["run", DL_URL, "--output-dir", str(tmp_path), "--dry-run"])
    # Should list at least one lesson
    assert "lesson" in result.output.lower() or "Found" in result.output
