"""Extended protocols allowed by ScreenPy: Playwright."""

from typing import Protocol


class PageObject(Protocol):
    """PageObjects have a URL."""

    url: str
