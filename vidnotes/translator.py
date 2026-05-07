import shutil
import subprocess
from pathlib import Path

from .config import PROMPTS_DIR, TRANSLATION_PROMPT_FILE

_PACKAGE_TRANSLATION_PROMPT = Path(__file__).parent / "translation_prompt.md"

# Common BCP-47 codes and plain names accepted as valid language inputs.
# Claude resolves the actual translation; this list only gates obvious typos/gibberish.
_KNOWN_LANGUAGES: set[str] = {
    # codes
    "af", "ar", "az", "be", "bg", "bn", "bs", "ca", "cs", "cy", "da", "de",
    "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fr", "ga", "gl", "gu",
    "he", "hi", "hr", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "km",
    "kn", "ko", "lt", "lv", "mk", "ml", "mn", "mr", "ms", "mt", "my", "nl",
    "no", "nb", "nn", "pa", "pl", "pt", "ro", "ru", "si", "sk", "sl", "sq",
    "sr", "sv", "sw", "ta", "te", "th", "tl", "tr", "ua", "ur", "uz",
    "vi", "zh", "zu",
    # plain names
    "afrikaans", "arabic", "azerbaijani", "belarusian", "bulgarian", "bengali",
    "bosnian", "catalan", "chinese", "croatian", "czech", "danish", "dutch",
    "english", "esperanto", "estonian", "finnish", "french", "galician",
    "georgian", "german", "greek", "gujarati", "hebrew", "hindi", "hungarian",
    "icelandic", "indonesian", "irish", "italian", "japanese", "kannada",
    "kazakh", "khmer", "korean", "latvian", "lithuanian", "macedonian",
    "malay", "maltese", "marathi", "mongolian", "myanmar", "burmese",
    "nepali", "norwegian", "persian", "polish", "portuguese", "punjabi",
    "romanian", "russian", "serbian", "sinhalese", "slovak", "slovenian",
    "somali", "spanish", "swahili", "swedish", "tagalog", "tamil", "telugu",
    "thai", "turkish", "ukrainian", "urdu", "uzbek", "vietnamese", "welsh",
    "zulu",
}

_EXAMPLES = "ua, de, fr, pl, ja, zh, arabic, polish, ukrainian"


def validate_language(lang: str) -> str | None:
    """Return the language string if recognised, None otherwise."""
    return lang if lang.lower() in _KNOWN_LANGUAGES else None


def translated_output_path(output_dir: Path, lesson, lang: str) -> Path:
    return output_dir / lesson.course_slug / lang / f"{lesson.slug}.md"


def _ensure_translation_prompt_file() -> Path:
    if not TRANSLATION_PROMPT_FILE.exists():
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(_PACKAGE_TRANSLATION_PROMPT, TRANSLATION_PROMPT_FILE)
    return TRANSLATION_PROMPT_FILE


def translate(summary_text: str, lang: str, claude_bin: str = "claude") -> str:
    template = _ensure_translation_prompt_file().read_text()
    prompt = template.replace("{lang}", lang).replace("{summary}", summary_text)
    result = subprocess.run([claude_bin, "-p", prompt], capture_output=True, text=True, check=True)
    return result.stdout.strip()
