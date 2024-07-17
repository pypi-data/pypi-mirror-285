"""Select an option!"""

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, TypedDict

from playwright.sync_api import Error as PlaywrightError
from screenpy import DeliveryError, UnableToAct, beat

if TYPE_CHECKING:
    from playwright.sync_api import ElementHandle
    from screenpy import Actor
    from typing_extensions import NotRequired, Self, Unpack

    from screenpy_playwright import Target

    class SelectTypes(TypedDict):
        """Types that can be passed to Playwright's Locator.select_option method."""

        index: NotRequired[int | Sequence[int] | None]
        label: NotRequired[str | Sequence[str] | None]
        element: NotRequired[ElementHandle | Sequence[ElementHandle] | None]
        timeout: NotRequired[float | None]
        no_wait_after: NotRequired[bool | None]
        force: NotRequired[bool | None]


class Select:
    """Select an option from a dropdown or multi-select field.

    Abilities Required:
        :class:`~screenpy_playwright.abilities.BrowseTheWebSynchronously`

    Examples::

        the_actor.attempts_to(
            Select("north-facing").from_the(NPC_ORIENTATION_DROPDOWN)
        )

        the_actor.attempts_to(
            Select.the_option("January").from_the(EXPIRY_MONTH_DROPDOWN)
        )

        the_actor.attempts_to(
            Select.the_options("red", "green", "blue").from_(FAVORITE_COLOR_SELECT)
        )

        the_actor.attempts_to(
            Select(value="20+").from_the(NUMBER_OF_COOKIES_DROPDOWN)
        )
    """

    target: Target | None
    args: tuple[str, ...]
    kwargs: SelectTypes

    @classmethod
    def the_option(cls, *args: str, **kwargs: Unpack[SelectTypes]) -> Self:
        """Specify the option to select.

        The valid arguments for this method follow the parameters for the
        `select_option <https://playwright.dev/python/docs/api/class-locator#locator-select-option>`_
        method in Playwright.

        Aliases:
            - ``the_options``
        """
        return cls(*args, **kwargs)

    @classmethod
    def the_options(cls, *args: str, **kwargs: Unpack[SelectTypes]) -> Self:
        """Alias for the_option."""
        return cls.the_option(*args, **kwargs)

    def __init__(self, *args: str, **kwargs: Unpack[SelectTypes]) -> None:
        self.args = args
        self.kwargs = kwargs
        self.target = None

    def from_the(self, target: Target) -> Self:
        """Specify the dropdown or multi-select field to select from.

        Aliases:
            - ``from_``
        """
        self.target = target
        return self

    from_ = from_the

    @property
    def option_to_log(self) -> str:
        """Get a log-friendly version of the option."""
        return "', '".join(self.args)

    def describe(self) -> str:
        """Describe the Action in present tense."""
        return f"Select '{self.option_to_log}' from the {self.target}."

    @beat("{} selects '{option_to_log}' from the {target}.")
    def perform_as(self, the_actor: Actor) -> None:
        """Direct the Actor to select the option from the dropdown."""
        if self.target is None:
            msg = (
                "Target was not supplied for Select."
                " Provide a target by using either the .from_() or .from_the() method."
            )
            raise UnableToAct(msg)

        try:
            self.target.found_by(the_actor).select_option(self.args, **self.kwargs)
        except PlaywrightError as e:
            msg = (
                f"{the_actor} encountered an issue while attempting to select "
                f"{self.target}: {e.__class__.__name__}"
            )
            raise DeliveryError(msg) from e
