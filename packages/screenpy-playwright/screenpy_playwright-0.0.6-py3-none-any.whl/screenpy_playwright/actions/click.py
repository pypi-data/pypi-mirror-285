"""Click on an element."""

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, TypedDict

from playwright.sync_api import Error as PlaywrightError
from screenpy import DeliveryError, beat

if TYPE_CHECKING:
    from playwright.sync_api import Position
    from screenpy import Actor
    from typing_extensions import Literal, NotRequired, Self, Unpack

    from ..target import Target

    class ClickTypes(TypedDict):
        """Types that can be passed to Playwright's ElementHandle.click method."""

        modifiers: NotRequired[
            Sequence[Literal["Alt", "Control", "Meta", "Shift"]] | None
        ]
        position: NotRequired[Position | None]
        delay: NotRequired[float | None]
        button: NotRequired[Literal["left", "middle", "right"] | None]
        click_count: NotRequired[int | None]
        timeout: NotRequired[float | None]
        force: NotRequired[bool | None]
        no_wait_after: NotRequired[bool | None]
        trial: NotRequired[bool | None]


class Click:
    """Click on an element!

    Abilities Required:
        :class:`~screenpy_playwright.abilities.BrowseTheWebSynchronously`

    Examples::

        the_actor.attempts_to(Click.on_the(LOG_IN_BUTTON))

        the_actor.attempts_to(Click(PROFILE_HEADER, delay=0.5, timeout=10))
    """

    kwargs: ClickTypes

    @classmethod
    def on_the(cls, target: Target, **kwargs: Unpack[ClickTypes]) -> Self:
        """Specify the element on which to click.

        Aliases:
            - ``on``
        """
        return cls(target, **kwargs)

    on = on_the

    def describe(self) -> str:
        """Describe the Action in present tense."""
        return f"Click on the {self.target}."

    @beat("{} clicks on the {target}.")
    def perform_as(self, the_actor: Actor) -> None:
        """Direct the Actor to click on the element."""
        try:
            self.target.found_by(the_actor).click(**self.kwargs)
        except PlaywrightError as e:
            msg = (
                f"{the_actor} encountered an issue while attempting to click "
                f"{self.target}: {e.__class__.__name__}"
            )
            raise DeliveryError(msg) from e

    def __init__(self, target: Target, **kwargs: Unpack[ClickTypes]) -> None:
        self.target = target
        self.kwargs = kwargs
