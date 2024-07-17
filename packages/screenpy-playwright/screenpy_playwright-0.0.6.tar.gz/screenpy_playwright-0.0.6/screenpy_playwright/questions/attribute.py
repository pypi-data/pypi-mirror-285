"""Get the value of an HTML attribute on a Target."""

from __future__ import annotations

from typing import TYPE_CHECKING

from screenpy import UnableToAnswer

if TYPE_CHECKING:
    from screenpy import Actor
    from typing_extensions import Self

    from ..target import Target


class Attribute:
    """Ask about the value of an HTML attribute on a Target.

    Abilities Required:
        :class:`~screenpy_playwright.abilities.BrowseTheWebSynchronously`

    Examples::

        the_actor.should(
            See.the(
                Attribute("aria-label").of_the(LOGIN_LINK),
                ContainsTheText("Log in to the application.")
            )
        )

        the_actor.attempts_to(
            MakeNote.of_the(Attribute("href").of_the(LOGIN_LINK).as_(
                "login link"
            ),
        )
    """

    target: Target | None

    def __init__(self, attribute: str) -> None:
        self.attribute = attribute
        self.target = None

    def describe(self) -> str:
        """Describe the Question in present tense."""
        return f'The "{self.attribute}" attribute of the {self.target}.'

    def of_the(self, target: Target) -> Self:
        """Supply the Target to get the attribute from.

        Args:
            target: the Target to get the attribute from.
        """
        self.target = target
        return self

    def answered_by(self, the_actor: Actor) -> str | None:
        """Ask the Actor to get the value of the attribute.

        Args:
            the_actor: the Actor who will answer this Question.

        Returns:
            str | None: the value of the attribute.
        """
        if self.target is None:
            msg = "No Target was provided! Supply one with .of_the()."
            raise UnableToAnswer(msg)

        return self.target.found_by(the_actor).get_attribute(self.attribute)
