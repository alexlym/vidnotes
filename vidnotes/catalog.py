import json
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from rich.console import Console

from .fetcher import (
    PlaywrightFetcher,
    RequestsFetcher,
    needs_js_rendering,
    session_to_pw_cookies,
)
from .models import Course, Lesson

console = Console()

# Matches /courses/{slug}/lesson/{id}/{title-slug}
#      or /specializations/{slug}/lesson/{id}/{title-slug}
_LESSON_PATH_RE = re.compile(
    r"/(courses|specializations)/([^/?#]+)/lesson/([^/?#]+)(?:/([^/?#]+))?"
)


def _course_slug(url: str) -> str:
    parts = urlparse(url).path.strip("/").split("/")
    return parts[1] if len(parts) >= 2 else parts[0]


def _lessons_from_next_data(html: str, course_url: str) -> list[Lesson] | None:
    """Try to extract lessons from Next.js __NEXT_DATA__ JSON blob."""
    soup = BeautifulSoup(html, "lxml")
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag:
        return None

    try:
        data = json.loads(tag.string)
    except Exception:
        return None

    slug = _course_slug(course_url)
    lessons = []

    # Walk the JSON tree looking for lesson-shaped objects
    def walk(obj, path=""):
        if isinstance(obj, dict):
            # A lesson object typically has id, title, and a slug/url field
            if {"id", "title"} <= obj.keys():
                url_val = obj.get("url") or obj.get("slug") or obj.get("lessonSlug") or ""
                lesson_id = str(obj["id"])
                lesson_slug = url_val.strip("/").split("/")[-1] or lesson_id
                full_url = (
                    url_val if url_val.startswith("http")
                    else f"https://learn.deeplearning.ai/courses/{slug}/lesson/{lesson_id}/{lesson_slug}"
                )
                lessons.append(Lesson(
                    id=lesson_id,
                    slug=lesson_slug,
                    title=str(obj["title"]),
                    course_slug=slug,
                    url=full_url,
                    lesson_type=obj.get("type", "video"),
                ))
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)

    # Deduplicate by id
    seen = set()
    unique = []
    for l in lessons:
        if l.id not in seen:
            seen.add(l.id)
            unique.append(l)

    return unique if unique else None


def _lessons_from_links(html: str, course_url: str) -> list[Lesson]:
    """Parse lesson links directly from page HTML."""
    soup = BeautifulSoup(html, "lxml")
    slug = _course_slug(course_url)
    lessons = []
    seen = set()

    for a in soup.find_all("a", href=True):
        m = _LESSON_PATH_RE.search(a["href"])
        if not m:
            continue
        href = a["href"]
        if href in seen:
            continue
        seen.add(href)

        lesson_id = m.group(3)
        lesson_slug = m.group(4) or lesson_id
        # Use only the first text node to avoid concatenated type/duration badges
        title = next(a.stripped_strings, None) or lesson_slug.replace("-", " ").title()
        full_url = href if href.startswith("http") else f"https://learn.deeplearning.ai{href}"

        lessons.append(Lesson(
            id=lesson_id,
            slug=lesson_slug,
            title=title,
            course_slug=slug,
            url=full_url,
        ))

    return lessons


def get_lessons(course_url: str, session: requests.Session) -> list[Lesson]:
    """Return the ordered list of lessons for a course URL."""
    html = RequestsFetcher(session).get(course_url)

    # Strategy 1: __NEXT_DATA__ JSON (fastest, no JS needed)
    lessons = _lessons_from_next_data(html, course_url)
    if lessons:
        console.print(f"[dim]Found {len(lessons)} lessons via __NEXT_DATA__[/dim]")
        return lessons

    # Strategy 2: Parse lesson links from static HTML
    lessons = _lessons_from_links(html, course_url)
    if lessons:
        console.print(f"[dim]Found {len(lessons)} lessons via link parsing[/dim]")
        return lessons

    # Strategy 3: JS-rendered — use Playwright
    if needs_js_rendering(html):
        console.print("[dim]Page is JS-rendered, retrying with Playwright...[/dim]")
        fetcher = PlaywrightFetcher(session_to_pw_cookies(session))
        try:
            html = fetcher.get(course_url)
        finally:
            fetcher.close()

        lessons = _lessons_from_next_data(html, course_url) or _lessons_from_links(html, course_url)
        if lessons:
            console.print(f"[dim]Found {len(lessons)} lessons via Playwright[/dim]")
            return lessons

    console.print("[yellow]Warning: could not find any lessons on this page.[/yellow]")
    return []
