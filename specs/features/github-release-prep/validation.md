# Validation: github-release-prep

| # | Criterion | How to verify |
|---|-----------|---------------|
| 1 | REQ-1 met — README covers all commands and flags | Open `README.md`; confirm sections exist for every `vidnotes` subcommand (`run`, `auth`, `transcripts`, `ask`) and the major flags (`--dry-run`, `--lesson`, `--force`, `--refetch`, `--translate`). |
| 2 | REQ-2 met — .gitignore covers credentials and generated output | Run `git check-ignore -v cookies.json ~/.config/vidnotes/ ~/vidnotes/`; each should be ignored. Confirm `*.state.json` and `.transcripts/` are matched. |
| 3 | REQ-3 met — platform dependency docs are present and correct | Read the dependency docs; verify install commands for `yt-dlp`, `playwright install chromium`, and `claude` CLI are shown for Linux/macOS/Windows. |
| 4 | REQ-4 met — setup guide works end-to-end | Follow the setup guide from scratch in a clean environment (or review each step manually); confirm `vidnotes auth login` and `vidnotes run <url> --dry-run` would succeed after following it. |
| 5 | REQ-5 met — no secrets in tracked files | Run `git ls-files | xargs grep -l -i "cookie\|token\|password\|secret\|api.key" 2>/dev/null` — output should be empty or limited to doc examples with clearly fake values. |
| 6 | REQ-6 met — pyproject.toml is publish-ready | Run `pip install --dry-run .` and inspect output for missing metadata warnings. Confirm `name`, `version`, `description`, `authors`, `license`, `requires-python`, and `dependencies` are all set. |
| 7 | REQ-7 met — Ukrainian README exists and is complete | Open `README.ua.md`; confirm all sections from `README.md` are present and in Ukrainian. |
