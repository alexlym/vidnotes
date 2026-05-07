from dataclasses import dataclass, field
from enum import Enum


@dataclass
class Lesson:
    id: str
    slug: str
    title: str
    course_slug: str
    url: str
    lesson_type: str = "video"  # "video" | "reading" | "quiz"


@dataclass
class Course:
    id: str
    slug: str
    title: str
    url: str
    lessons: list[Lesson] = field(default_factory=list)


@dataclass
class LessonContent:
    lesson: Lesson
    transcript: str | None
    page_text: str | None
    source: str  # "next-data" | "cached" | "page-text" | "none"


class LessonStatus(str, Enum):
    PENDING = "pending"
    TRANSCRIPT_SAVED = "transcript_saved"
    SUMMARIZED = "summarized"
    FAILED = "failed"


@dataclass
class LessonState:
    status: LessonStatus = LessonStatus.PENDING
    transcript_chars: int = 0
    summarized_at: str | None = None
    error: str | None = None
