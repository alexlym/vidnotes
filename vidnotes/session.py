import json
import os
import re
import stat

import requests
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from .config import AUTH_LOGIN_URL, LEARN_BASE_URL, SESSION_FILE, CONFIG_DIR


def login() -> None:
    """Open a visible browser for the user to log in, then save cookies."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    print("Browser opening — please log in, then wait for it to close automatically...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        # Open the main app — it loads the homepage with a Sign In button
        # rather than auto-redirecting. We click the button to trigger the
        # OAuth flow with the proper redirect_uri.
        page.goto(LEARN_BASE_URL)
        page.wait_for_load_state("networkidle")

        if page.url.startswith(LEARN_BASE_URL):
            # Find and click the sign-in button/link
            sign_in = re.compile(r"sign.?in", re.IGNORECASE)
            clicked = False
            for locator in [
                page.get_by_role("button", name=sign_in),
                page.get_by_role("link", name=sign_in),
            ]:
                if locator.count() > 0:
                    locator.first.click()
                    clicked = True
                    break
            if not clicked:
                print("Could not find a Sign In button — please click it manually in the browser.")

        # Wait for the auth domain to appear
        page.wait_for_url(
            lambda url: "auth.deeplearning.ai" in url,
            timeout=15_000,
        )
        print("Please log in in the browser window, then wait...")

        # Wait for the redirect back to learn.deeplearning.ai after login
        page.wait_for_url(
            lambda url: url.startswith(LEARN_BASE_URL),
            timeout=120_000,
        )

        cookies = context.cookies()
        current_url = page.url
        browser.close()

    print(f"Landed on: {current_url}")

    SESSION_FILE.write_text(json.dumps({"cookies": cookies}, indent=2))
    os.chmod(SESSION_FILE, stat.S_IRUSR | stat.S_IWUSR)
    print(f"Session saved to {SESSION_FILE}")


def load_session() -> requests.Session | None:
    """Load saved cookies into a requests.Session. Returns None if no session file."""
    if not SESSION_FILE.exists():
        return None

    data = json.loads(SESSION_FILE.read_text())
    session = requests.Session()
    for c in data["cookies"]:
        session.cookies.set(c["name"], c["value"], domain=c.get("domain"), path=c.get("path", "/"))
    return session


def validate_session(session: requests.Session) -> bool:
    """Return True if the session is still authenticated."""
    try:
        resp = session.get(LEARN_BASE_URL, timeout=10)
        # A redirect to the auth domain means the session expired
        return "auth.deeplearning.ai" not in resp.url
    except requests.RequestException:
        return False


def get_session() -> requests.Session:
    """Return a valid requests.Session, triggering browser login if needed."""
    session = load_session()
    if session is None or not validate_session(session):
        login()
        session = load_session()
    return session
