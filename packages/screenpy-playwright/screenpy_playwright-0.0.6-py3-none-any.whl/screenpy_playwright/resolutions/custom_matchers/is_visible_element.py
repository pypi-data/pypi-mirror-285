"""
A matcher that matches a visible element.

For example:

    assert_that(driver.find_element_by_id("search"), is_visible_element())
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from hamcrest.core.base_matcher import BaseMatcher
from playwright.sync_api import Locator

if TYPE_CHECKING:
    from hamcrest.core.description import Description


class IsVisibleElement(BaseMatcher[Optional[Locator]]):
    """Match a locator whose ``is_visible`` method returns True."""

    def _matches(self, item: Locator | None) -> bool:
        if item is None:
            return False
        return item.is_visible()

    def describe_to(self, description: Description) -> None:
        """Describe the passing case."""
        description.append_text("the element is visible")

    def describe_match(self, _: Locator | None, match_description: Description) -> None:
        """Describe the matching case."""
        match_description.append_text("it was visible")

    def describe_mismatch(
        self, item: Locator | None, mismatch_description: Description
    ) -> None:
        """Describe the failing case."""
        if item is None:
            mismatch_description.append_text("was not even present")
            return
        mismatch_description.append_text("was not visible")


def is_visible_element() -> IsVisibleElement:
    """Match any locator whose described element is visible."""
    return IsVisibleElement()
