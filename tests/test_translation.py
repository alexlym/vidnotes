from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from vidnotes.cli import app
from vidnotes.models import Lesson
from vidnotes.translator import translated_output_path, validate_language

runner = CliRunner()

YT_URL = "https://www.youtube.com/watch?v=96jN2OCOfLs"


def _lesson(slug="lesson-1", course_slug="my-course"):
    return Lesson(id=slug, slug=slug, title=slug.replace("-", " ").title(),
                  course_slug=course_slug, url="")


# T1 — translated_output_path builds correct subfolder path

def test_translated_output_path(tmp_path):
    lesson = _lesson()
    result = translated_output_path(tmp_path, lesson, "ua")
    assert result == tmp_path / "my-course" / "ua" / "lesson-1.md"


# T2 — translation skipped when output already exists (no --force)

def test_translate_cmd_skips_existing(tmp_path):
    course_dir = tmp_path / "my-course"
    course_dir.mkdir(parents=True)
    (course_dir / "lesson-1.md").write_text("# Summary")
    dest = course_dir / "ua" / "lesson-1.md"
    dest.parent.mkdir(parents=True)
    dest.write_text("# Existing translation")

    with patch("vidnotes.cli.translate") as mock_translate:
        result = runner.invoke(app, ["translate", "my-course", "ua", "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    mock_translate.assert_not_called()
    assert "already translated" in result.output


# T3 — translation runs with --force even if output exists

def test_translate_cmd_force_retranslates(tmp_path):
    course_dir = tmp_path / "my-course"
    course_dir.mkdir(parents=True)
    (course_dir / "lesson-1.md").write_text("# Summary")
    dest = course_dir / "ua" / "lesson-1.md"
    dest.parent.mkdir(parents=True)
    dest.write_text("# Old translation")

    with patch("vidnotes.cli.translate", return_value="# New translation") as mock_translate:
        result = runner.invoke(app, ["translate", "my-course", "ua", "--force", "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    mock_translate.assert_called_once()
    assert dest.read_text() == "# New translation"


# T4 — missing source summary warns and skips

def test_translate_cmd_warns_on_missing_source(tmp_path):
    course_dir = tmp_path / "my-course"
    course_dir.mkdir(parents=True)
    # no .md files written

    with patch("vidnotes.cli.translate") as mock_translate:
        result = runner.invoke(app, ["translate", "my-course", "ua", "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    mock_translate.assert_not_called()


# T10 — unrecognised language exits with friendly error, no files written

def test_run_unknown_language_exits_with_error(tmp_path):
    result = runner.invoke(app, ["run", YT_URL, "--translate", "zzz",
                                 "--output-dir", str(tmp_path)])
    assert result.exit_code != 0
    assert "Unknown language" in result.output
    assert not any(tmp_path.rglob("*.md"))


def test_translate_cmd_unknown_language_exits_with_error(tmp_path):
    (tmp_path / "my-course").mkdir(parents=True)
    result = runner.invoke(app, ["translate", "my-course", "zzz", "--output-dir", str(tmp_path)])
    assert result.exit_code != 0
    assert "Unknown language" in result.output


def test_unknown_language_error_shows_examples(tmp_path):
    result = runner.invoke(app, ["run", YT_URL, "--translate", "zzz",
                                 "--output-dir", str(tmp_path)])
    assert "ua" in result.output


# validate_language unit tests

def test_validate_language_accepts_ua():
    assert validate_language("ua") == "ua"

def test_validate_language_accepts_plain_name():
    assert validate_language("ukrainian") == "ukrainian"

def test_validate_language_rejects_gibberish():
    assert validate_language("zzz") is None

def test_validate_language_rejects_numeric():
    assert validate_language("123") is None
