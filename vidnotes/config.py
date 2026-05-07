import tomllib
from pathlib import Path
from dataclasses import dataclass

CONFIG_DIR = Path.home() / ".config" / "vidnotes"
SESSION_FILE = CONFIG_DIR / "session.json"
PROMPTS_DIR = CONFIG_DIR / "prompts"
DEFAULT_PROMPT_FILE = PROMPTS_DIR / "summarize.md"
TRANSLATION_PROMPT_FILE = PROMPTS_DIR / "translation.md"

# Auth / platform constants
AUTH_LOGIN_URL = "https://auth.deeplearning.ai/login"
LEARN_BASE_URL = "https://learn.deeplearning.ai"

# Set after one-time DevTools inspection: right-click transcript text → Inspect,
# note the CSS selector of the container element.
TRANSCRIPT_SELECTOR = "[data-testid='transcript']"


_DEFAULT_OUTPUT = Path.home() / "vidnotes"


def transcripts_dir(output_dir: Path, course_slug: str) -> Path:
    return output_dir / course_slug / ".transcripts"


def state_file(output_dir: Path, course_slug: str) -> Path:
    return output_dir / course_slug / ".state.json"


@dataclass
class Settings:
    output_dir: Path = _DEFAULT_OUTPUT

    @classmethod
    def load(cls, config_path: Path | None = None) -> "Settings":
        # Check explicit path, then ~/.config/vidnotes/config.toml, then ./config.toml
        candidates = [config_path, CONFIG_DIR / "config.toml", Path("config.toml")]
        path = next((p for p in candidates if p and p.exists()), None)
        if path is None:
            return cls()
        with open(path, "rb") as f:
            data = tomllib.load(f)
        opts = data.get("options", {})
        return cls(
            output_dir=Path(opts.get("output_dir", str(Path.home() / "vidnotes"))),
        )
