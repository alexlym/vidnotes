import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .fetcher import RequestsFetcher
from .models import Lesson, LessonContent
from .writer import load_transcript, save_transcript


def extract_content(lesson: Lesson, session: requests.Session, output_dir: Path | None = None) -> LessonContent:
    """Extract transcript or page text. Uses cached transcript if available."""

    # Check cache first
    if output_dir is not None:
        cached = load_transcript(output_dir, lesson)
        if cached:
            return LessonContent(lesson=lesson, transcript=cached, page_text=None, source="cached")

    html = RequestsFetcher(session).get(lesson.url)
    soup = BeautifulSoup(html, "lxml")

    # Primary: transcript embedded in __NEXT_DATA__
    tag = soup.find("script", id="__NEXT_DATA__")
    if tag:
        try:
            props = json.loads(tag.string)["props"]["pageProps"]
            captions = props.get("captions")
            if captions and captions.strip():
                text = captions.strip()
                if output_dir is not None:
                    save_transcript(output_dir, lesson, text)
                return LessonContent(lesson=lesson, transcript=text, page_text=None, source="next-data")
        except (KeyError, json.JSONDecodeError):
            pass

    # Fallback: readable page text (reading/article lessons)
    page_text = _extract_page_text(soup)
    if page_text and output_dir is not None:
        save_transcript(output_dir, lesson, page_text)
    return LessonContent(
        lesson=lesson,
        transcript=None,
        page_text=page_text or None,
        source="page-text" if page_text else "none",
    )


def _extract_page_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body
    if not main:
        return ""
    lines = []
    for el in main.find_all(["p", "h1", "h2", "h3", "h4", "li", "pre", "code"]):
        text = el.get_text(strip=True)
        if text:
            lines.append(text)
    return "\n".join(lines)
