"""
A matcher that matches a present element.

For example:

    assert_that(driver.find_element_by_id("search"), is_present_element())
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from hamcrest.core.base_matcher import BaseMatcher
from playwright.sync_api import Locator

if TYPE_CHECKING:
    from hamcrest.core.description import Description


class IsPresentElement(BaseMatcher[Optional[Locator]]):
    """Match a locator which finds at least 1 element."""

    def _matches(self, item: Locator | None) -> bool:
        if item is None:
            return False
        return item.count() > 0

    def describe_to(self, description: Description) -> None:
        """Describe what is needed to pass this test."""
        description.append_text("an element which is present")

    def describe_match(self, _: Locator | None, match_description: Description) -> None:
        """Describe the matching case."""
        match_description.append_text("it was present")

    def describe_mismatch(
        self, _: Locator | None, mismatch_description: Description
    ) -> None:
        """Describe the failing case."""
        mismatch_description.append_text("was not present")


def is_present_element() -> IsPresentElement:
    """Match a locator which finds at least 1 element present on the page."""
    return IsPresentElement()
