"""Ask about the text in an element."""

from __future__ import annotations

from typing import TYPE_CHECKING

from screenpy.pacing import beat

if TYPE_CHECKING:
    from screenpy import Actor

    from ..target import Target


class Text:
    """Ask for the text from a Target.

    Examples::

        the_actor.should(
            See.the(Text.of_the(WELCOME_BANNER), ReadsExactly("Welcome!"))
        )
    """

    @staticmethod
    def of_the(target: Target) -> Text:
        """Supply the Target whose text to read.

        Args:
            target: the Target which describes the Element to read.

        Returns:
            A new instance of Text.
        """
        return Text(target)

    def describe(self) -> str:
        """Describe the Question in the present tense.

        Returns:
            A description of this Question.
        """
        return f"The text from the {self.target}."

    @beat("{} examines the text of the {target}.")
    def answered_by(self, the_actor: Actor) -> str | None:
        """Direct the Actor to read the text from the target.

        Returns:
            The text found by the Actor.
        """
        return self.target.found_by(the_actor).text_content()

    def __init__(self, target: Target) -> None:
        self.target = target
