"""Ask about the number of an element."""

from __future__ import annotations

from typing import TYPE_CHECKING

from screenpy.pacing import beat

if TYPE_CHECKING:
    from screenpy import Actor

    from ..target import Target


class Number:
    """Ask how many of an element are on the page.

    Examples::

        the_actor.should(See.the(Number.of(CONFETTI), IsEqualTo(10)))
    """

    @staticmethod
    def of(target: Target) -> Number:
        """Supply the Target to count.

        Args:
            target: the Target which describes the element to count.

        Returns:
            A new Number instance.
        """
        return Number(target)

    def describe(self) -> str:
        """Describe the Question in the present tense.

        Returns:
            A description of this Question.
        """
        return f"The number of {self.target}."

    @beat("{} examines the Number of the {target}.")
    def answered_by(self, the_actor: Actor) -> int:
        """Direct the Actor to read the Number from the target.

        Returns:
            The number of elements the Actor found.
        """
        return self.target.found_by(the_actor).count()

    def __init__(self, target: Target) -> None:
        self.target = target
