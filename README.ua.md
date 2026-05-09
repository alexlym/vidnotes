# vidnotes

Перетворюй відеокурси та YouTube-відео на структуровані нотатки у форматі Markdown за допомогою Claude.

- Створює конспект кожного уроку окремо, а потім — загальний огляд курсу
- Підтримує курси [deeplearning.ai](https://learn.deeplearning.ai) та будь-які YouTube-відео
- Кешує транскрипти локально — можна переривати і продовжувати, або повторно конспектувати без повторного завантаження
- Переклад нотаток будь-якою мовою — однією командою

> **Про проєкт:** vidnotes — це вайб-кодинг експеримент із використання [Claude Code](https://claude.ai/code) як щоденного партнера з розробки. Увесь код написано за методологією специфікаційно-орієнтованої розробки з курсу [Spec-Driven Development with Coding Agents](https://learn.deeplearning.ai/courses/spec-driven-development-with-coding-agents) — кожна функція починається зі специфікації, перш ніж написати хоч рядок коду.

---

## Вимоги

| Залежність | Версія | Встановлення |
|------------|--------|--------------|
| Python | ≥ 3.11 | [python.org](https://www.python.org/downloads/) або `pyenv` |
| Claude CLI | остання | `npm install -g @anthropic-ai/claude-code` |
| yt-dlp | остання | `pipx install yt-dlp` або `pip install yt-dlp` |
| Playwright (Chromium) | ≥ 1.40 | встановлюється автоматично; після `pip install` запусти `playwright install chromium` |

**Linux / ChromeOS:** Playwright на Linux може потребувати системних бібліотек. Якщо браузер не запускається:
```
playwright install-deps chromium
```

**Claude CLI:** Необхідно бути авторизованим (`claude`) та мати активну підписку. vidnotes викликає `claude -p` як підпроцес — API-ключ не потрібен.

---

## Встановлення

```bash
git clone https://github.com/yourusername/vidnotes.git
cd vidnotes
pip install -e .
playwright install chromium
```

Перевір встановлення:
```bash
vidnotes --help
```

---

## Налаштування (необов'язково)

Скопіюй приклад конфігурації і відредагуй за потреби:
```bash
cp config.toml.example ~/.config/vidnotes/config.toml
```

Параметри `config.toml`:
```toml
[options]
output_dir = "~/vidnotes"   # де зберігати нотатки (за замовчуванням: ~/vidnotes)
```

Також можна передати `--output-dir` у будь-якій команді, щоб замінити це значення.

---

## Авторизація (лише для deeplearning.ai)

YouTube-відео не потребують авторизації. Для курсів deeplearning.ai потрібно увійти один раз:

```bash
vidnotes auth login
```

Відкриється браузер — увійдіть в акаунт, а потім закрийте вікно. Сесія зберігається у `~/.config/vidnotes/session.json` і використовується автоматично.

Перевірити стан сесії:
```bash
vidnotes auth status
```

---

## Використання

### Конспект курсу deeplearning.ai

```bash
vidnotes run https://learn.deeplearning.ai/courses/назва-курсу
```

Нотатки зберігаються у `~/vidnotes/<slug-курсу>/`. Після обробки всіх уроків автоматично генерується загальний огляд курсу `_course_summary.md`.

### Конспект YouTube-відео

```bash
vidnotes run https://www.youtube.com/watch?v=VIDEO_ID
```

### Параметри команди `vidnotes run`

| Прапор | Опис |
|--------|------|
| `--lesson SLUG` | Обробити лише уроки, у slug або назві яких є `SLUG` |
| `--force` | Повторно згенерувати конспекти (транскрипти беруться з кешу) |
| `--refetch` | Повторно завантажити транскрипти і перегенерувати конспекти |
| `--dry-run` | Витягти і показати вміст без виклику Claude |
| `--translate LANG` | Після конспектування перекласти нотатки на мову `LANG` (напр. `ua`, `de`, `польська`) |
| `--output-dir DIR` | Зберегти результат у `DIR` замість стандартної теки |

### Приклади

```bash
# Попередній перегляд без конспектування
vidnotes run https://learn.deeplearning.ai/courses/ml-ops --dry-run

# Обробити лише уроки, що містять "intro" у назві
vidnotes run https://learn.deeplearning.ai/courses/ml-ops --lesson intro

# Повторно згенерувати конспекти (транскрипти вже закешовані)
vidnotes run https://learn.deeplearning.ai/courses/ml-ops --force

# Конспект і переклад українською за один раз
vidnotes run https://www.youtube.com/watch?v=VIDEO_ID --translate ua
```

---

## Переклад наявних нотаток

Перекласти раніше згенеровані нотатки на іншу мову:

```bash
# За slug курсу
vidnotes translate ml-ops ua

# За URL
vidnotes translate https://learn.deeplearning.ai/courses/ml-ops ukrainian

# Переклад навіть якщо перекладені файли вже існують
vidnotes translate ml-ops de --force
```

Мова може бути вказана кодом BCP-47 (`ua`, `de`, `fr`, `zh`) або назвою (`ukrainian`, `german`, `french`).

Перекладені файли зберігаються поруч з оригіналами у підтеці `<lang>/`.

---

## Структура результату

```
~/vidnotes/
└── <slug-курсу>/
    ├── urok-pershyi.md
    ├── urok-druhyi.md
    ├── _course_summary.md
    ├── ua/
    │   ├── urok-pershyi.md
    │   └── urok-druhyi.md
    ├── .state.json          # відстеження прогресу (в .gitignore)
    └── .transcripts/        # кеш транскриптів (в .gitignore)
```

---

## Власні шаблони запитів

vidnotes постачається зі стандартними шаблонами. Щоб їх налаштувати, відредагуй файли у `~/.config/vidnotes/prompts/` (створюються автоматично при першому запуску):

| Файл | Призначення |
|------|-------------|
| `summarize.md` | Шаблон конспекту уроку (deeplearning.ai) |
| `translation.md` | Шаблон перекладу |

Шаблони для YouTube і загального огляду курсу вбудовані і поки що не підлягають налаштуванню.

---

## Додавання функцій (для контриб'юторів)

Цей проєкт використовує специфікаційно-орієнтований підхід — кожна функція починається зі специфікації, перш ніж написати хоч рядок коду.

У [Claude Code](https://claude.ai/code), відкритому в цьому репозиторії, запусти:

```
/sdd-feature <назва-функції>
```

Команда створить `specs/features/<назва-функції>/` із чотирма файлами: `plan.md`, `requirements.md`, `validation.md` і `tests.md`. Заповни план і тести, погодь їх, а тоді реалізуй. Повний опис процесу — у `CLAUDE.md`.

---

## Плани розвитку

- `vidnotes transcripts` — перегляд усіх закешованих транскриптів по курсах
- `vidnotes ask "<питання>"` — запитання по транскриптах із посиланнями на уроки
- Паралельний переклад із прогрес-баром
- Довідник для агентів (`AGENT.md`) для роботи з AI-асистентами
