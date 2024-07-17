"""Scroll the page using Playwright's Page.mouse.wheel method."""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Error as PlaywrightError
from screenpy import DeliveryError, beat

from ..abilities import BrowseTheWebSynchronously

if TYPE_CHECKING:
    from screenpy import Actor
    from typing_extensions import Self


class Scroll:
    """Scroll the page in any direction.

    Note that the origin of the page (0, 0) is at the top left of the viewport.
    This means scrolling "up" is a negative Y direction and scrolling "down"
    is a positive Y direction, while scrolling "left" is a negative X direction
    and scrolling "right" is a positive X direction.

    (You may also use the directional classmethods, which make sure the number
    is on the correct side of zero (and may be easier to read!).)

    Abilities Required:
        :class:`~screenpy_playwright.abilities.BrowseTheWebSynchronously`

    Examples::

        the_actor.attempts_to(Scroll(delta_x=-20, delta_y=1200))

        the_actor.attempts_to(Scroll.down(9001))

        the_actor.attempts_to(Scroll.left(1337))
    """

    @classmethod
    def down(cls, delta_y: int) -> Self:
        """Scroll the page down by a certain amount."""
        if delta_y < 0:
            delta_y = -delta_y
        return cls(delta_y=delta_y)

    @classmethod
    def up(cls, delta_y: int) -> Self:
        """Scroll the page up by a certain amount."""
        if delta_y > 0:
            delta_y = -delta_y
        return cls(delta_y=delta_y)

    @classmethod
    def left(cls, delta_x: int) -> Self:
        """Scroll the page to the left by a certain amount."""
        if delta_x > 0:
            delta_x = -delta_x
        return cls(delta_x=delta_x)

    @classmethod
    def right(cls, delta_x: int) -> Self:
        """Scroll the page to the right by a certain amount."""
        if delta_x < 0:
            delta_x = -delta_x
        return cls(delta_x=delta_x)

    def __init__(self, delta_x: int = 0, delta_y: int = 0) -> None:
        self.delta_x = delta_x
        self.delta_y = delta_y

    def describe(self) -> str:
        """Describe the Action in present tense."""
        return f"Scroll the page {self.direction_to_log}."

    @property
    def direction_to_log(self) -> str:
        """Get a human-readable string of the scroll direction."""
        if not self.delta_x and not self.delta_y:
            return "nowhere"

        if self.delta_x > 0:
            direction_x = f"{self.delta_x} pixels right"
        elif self.delta_x < 0:
            direction_x = f"{-self.delta_x} pixels left"
        else:
            direction_x = ""

        if self.delta_y > 0:
            direction_y = f"{self.delta_y} pixels down"
        elif self.delta_y < 0:
            direction_y = f"{-self.delta_y} pixels up"
        else:
            direction_y = ""

        joiner = " and " if direction_x and direction_y else ""

        return f"{direction_x}{joiner}{direction_y}"

    @beat("{} scrolls the page {direction_to_log}.")
    def perform_as(self, the_actor: Actor) -> None:
        """Direct the Actor to scroll the page."""
        page = the_actor.ability_to(BrowseTheWebSynchronously).current_page
        try:
            page.mouse.wheel(delta_x=self.delta_x, delta_y=self.delta_y)
        except PlaywrightError as e:
            msg = (
                f"{the_actor} encountered an issue while attempting to scroll "
                f"{self.direction_to_log}: {e.__class__.__name__}"
            )
            raise DeliveryError(msg) from e
