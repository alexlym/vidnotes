from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


class BaseFetcher(ABC):
    @abstractmethod
    def get(self, url: str) -> str:
        ...

    def close(self):
        pass


class RequestsFetcher(BaseFetcher):
    def __init__(self, session: requests.Session):
        self.session = session

    def get(self, url: str) -> str:
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.text


class PlaywrightFetcher(BaseFetcher):
    def __init__(self, cookies: list[dict]):
        self._cookies = cookies
        self._pw = None
        self._browser = None
        self._context = None

    def _ensure_started(self):
        if self._pw is None:
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(headless=True)
            self._context = self._browser.new_context()
            self._context.add_cookies(self._cookies)

    def get(self, url: str, wait_selector: str = "main") -> str:
        self._ensure_started()
        page = self._context.new_page()
        page.goto(url)
        try:
            page.wait_for_selector(wait_selector, timeout=10_000)
        except Exception:
            pass
        html = page.content()
        page.close()
        return html

    def close(self):
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()
        self._pw = self._browser = self._context = None


def needs_js_rendering(html: str) -> bool:
    soup = BeautifulSoup(html, "lxml")
    for root_id in ("__next", "root", "app"):
        el = soup.find(id=root_id)
        if el and len(el.get_text(strip=True)) < 200:
            return True
    return False


def session_to_pw_cookies(session: requests.Session) -> list[dict]:
    return [
        {"name": c.name, "value": c.value, "domain": c.domain, "path": c.path or "/"}
        for c in session.cookies
    ]
