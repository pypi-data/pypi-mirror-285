"""Get an element on the page."""

from playwright.sync_api import Locator
from screenpy import Actor, beat

from screenpy_playwright.target import Target


class Element:
    """Ask about an element on the page.

    Examples::

        the_actor.should(See.the(Element(SEARCH_BAR), IsVisible()))
    """

    def __init__(self, target: Target) -> None:
        self.target = target

    def describe(self) -> str:
        """Describe the Question in the present tense."""
        return f"The {self.target} element."

    @beat("{} looks at the {target}.")
    def answered_by(self, actor: Actor) -> Locator:
        """Direct the Actor to inspect the element."""
        return self.target.found_by(actor)
