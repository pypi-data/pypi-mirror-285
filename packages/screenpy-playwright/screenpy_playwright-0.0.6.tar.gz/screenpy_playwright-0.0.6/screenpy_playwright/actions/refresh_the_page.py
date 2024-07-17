"""Refresh the page!"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from playwright.sync_api import Error as PlaywrightError
from screenpy import DeliveryError, beat

from screenpy_playwright.abilities import BrowseTheWebSynchronously

if TYPE_CHECKING:
    from screenpy import Actor
    from typing_extensions import NotRequired, Unpack

    class ReloadTypes(TypedDict):
        """Types that can be passed to Playwright's Page.reload."""

        timeout: NotRequired[float | None]
        wait_until: NotRequired[
            Literal["commit", "domcontentloaded", "load", "networkidle"] | None
        ]


class RefreshThePage:
    """Refresh the current page in the browser.

    Abilities Required:
        :class:`~screenpy_playwright.abilities.BrowseTheWebSynchronously`

    Examples:
        the_actor.attempts_to(RefreshThePage())
    """

    kwargs: ReloadTypes

    def __init__(self, **kwargs: Unpack[ReloadTypes]) -> None:
        """Initialize the action."""
        self.kwargs = kwargs

    def describe(self) -> str:
        """Describe the Action in present tense."""
        return "Refresh the page."

    @beat("{} refreshes the page.")
    def perform_as(self, the_actor: Actor) -> None:
        """Direct the Actor to refresh the page."""
        page = the_actor.ability_to(BrowseTheWebSynchronously).current_page
        try:
            page.reload(**self.kwargs)
        except PlaywrightError as e:
            msg = (
                f"{the_actor} encountered an issue while attempting to "
                f"refresh the page: {e.__class__.__name__}"
            )
            raise DeliveryError(msg) from e
