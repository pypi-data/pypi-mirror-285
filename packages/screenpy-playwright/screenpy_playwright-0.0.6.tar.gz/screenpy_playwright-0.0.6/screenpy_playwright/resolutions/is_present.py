"""Matches against a present WebElement."""

from __future__ import annotations

from typing import TYPE_CHECKING

from screenpy import beat

from .custom_matchers import is_present_element

if TYPE_CHECKING:
    from .custom_matchers.is_present_element import IsPresentElement


class IsPresent:
    """Match on a present element.

    The element does not need to be visible, only that it exists.

    Examples::

        the_actor.should(See.the(Element(WELCOME_BANNER), IsPresent()))
    """

    def describe(self) -> str:
        """Describe the Resolution's expectation."""
        return "present"

    @beat("... hoping it's present.")
    def resolve(self) -> IsPresentElement:
        """Produce the Matcher to make the assertion."""
        return is_present_element()
