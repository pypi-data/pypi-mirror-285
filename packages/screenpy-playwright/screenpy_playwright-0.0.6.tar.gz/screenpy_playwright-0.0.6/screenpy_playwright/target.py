"""Represent an element on the page using its locator and a description."""

from __future__ import annotations

from collections import UserString
from dataclasses import dataclass
from typing import TYPE_CHECKING, Pattern, Tuple, TypedDict, Union

from playwright.sync_api import FrameLocator, Locator

from .abilities import BrowseTheWebSynchronously
from .exceptions import TargetingError

if TYPE_CHECKING:
    from screenpy import Actor
    from typing_extensions import NotRequired, Self, Unpack

    _ManipulationArgsType = Tuple[Union[str, int, None], ...]

    class _ManipulationKwargsType(TypedDict):
        """Types for kwargs that are passed to Playwright's locator methods."""

        has_text: NotRequired[str | Pattern[str] | None]
        has_not_text: NotRequired[str | Pattern[str] | None]
        has: NotRequired[Locator | None]
        has_not: NotRequired[Locator | None]
        exact: NotRequired[bool | None]
        checked: NotRequired[bool | None]
        disabled: NotRequired[bool | None]
        expanded: NotRequired[bool | None]
        include_hidden: NotRequired[bool | None]
        level: NotRequired[int | None]
        name: NotRequired[str | Pattern[str] | None]
        pressed: NotRequired[bool | None]
        selected: NotRequired[bool | None]


@dataclass
class _Manipulation(UserString):
    """Represent one of the Playwright options for creating a locator.

    Could be a function or an attribute.

    This class allows the ScreenPy Playwright Target to behave just like a
    Playwright Locator, which has a robust, chainable API for describing
    elements.

    This approach necessary because Locators are built from a Page base. We
    don't have a Page to build from until the Actor is provided during the
    :meth:`Target.found_by` call.
    """

    target: Target
    name: str
    args: _ManipulationArgsType | None = None
    kwargs: _ManipulationKwargsType | None = None

    def __hash__(self) -> int:
        """Appear as the name, in case this is an attribute and not a method."""
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Appear as the name, in case this is an attribute and not a method."""
        return self.name == other

    def __getattr__(self, name: str) -> Target | _Manipulation:
        """Defer back to the Target for unknown attributes."""
        return getattr(self.target, name)

    def __call__(
        self,
        *args: Unpack[_ManipulationArgsType],
        **kwargs: Unpack[_ManipulationKwargsType],
    ) -> Target:
        """Add args and kwargs to the manipulation."""
        self.args = args
        self.kwargs = kwargs
        return self.target

    def get_locator(self) -> str:
        """Reconstruct the locator function/attribute string."""
        args = kwargs = left_paren = right_paren = comma = ""
        if self.args is not None or self.kwargs is not None:
            left_paren = "("
            right_paren = ")"
        if self.args:
            args = ", ".join(repr(a) for a in self.args)
        if self.kwargs:
            kwargs = ", ".join(f"{k}={v!r}" for k, v in self.kwargs.items())
        if args and kwargs:
            comma = ", "
        return f"{self.name}{left_paren}{args}{comma}{kwargs}{right_paren}"

    def __repr__(self) -> str:
        """Return the Target for representation."""
        return repr(self.target)

    # make sure we handle str here as well
    __str__ = __repr__


class Target(Locator, FrameLocator):
    """A described element on a webpage.

    Uses Playwright's Locator API to describe an element on a webpage, with a
    few natural-language helpers. See the
    `Playwright documentation <https://playwright.dev/python/docs/locators>`_
    for more information.

    Examples::

        # Using CSS
        Target.the('"Log In" button').located_by("button:has-text('Log In')")

        # Using xpath
        Target.the("toast message").located_by("//toast")

        # Using Target methods with Playwright strategies
        Target.the('"Pick up Milk" todo item').in_frame("#todoframe").get_by_text(
            "Pick up Milk"
        )

        # Using Playwright strategies directly
        Target("To-Do list").frame_locator("#todoframe").get_by_label("todo")
    """

    manipulations: list[_Manipulation]
    _description: str | None

    @classmethod
    def the(cls: type[Self], name: str) -> Self:
        """Provide a human-readable description of the target."""
        return cls(name)

    def located_by(self, locator: str) -> Target:
        """Provide the CSS locator which describes the element."""
        self.manipulations.append(
            _Manipulation(self, "locator", args=(locator,), kwargs={})
        )
        return self

    def in_frame(self, frame_locator: str) -> Target:
        """Provide the CSS locator which describes the frame."""
        self.manipulations.append(
            _Manipulation(self, "frame_locator", args=(frame_locator,), kwargs={})
        )
        return self

    def __getattribute__(self, name: str) -> _Manipulation:
        """Convert a Playwright Locator strategy into a Manipulation."""
        is_private = name.startswith("_")
        superclass_has_attr = hasattr(Locator, name) or hasattr(FrameLocator, name)
        if not is_private and superclass_has_attr:
            attr = getattr(Locator, name) or getattr(FrameLocator, name)
            is_property = type(attr) is property
            r_type = getattr(attr, "__annotations__", {}).get("return")
            is_right_type = r_type is Locator or r_type is FrameLocator
            is_right_str = r_type in ["Locator", "FrameLocator"]

            if is_property or is_right_type or is_right_str:
                manipulation = _Manipulation(self, name)
                self.manipulations.append(manipulation)
                return manipulation

            msg = f"'{name}' cannot be accessed until `found_by` is called."
            raise TargetingError(msg)

        return super().__getattribute__(name)

    @property
    def target_name(self) -> str:
        """Get the name of the Target.

        If a description was not provided, an identifier will be created using
        the manipulation chain.

        Returns:
            The text representation of this Target.
        """
        if self._description:
            target_name = self._description
        elif self.manipulations:
            target_name = ".".join(m.get_locator() for m in self.manipulations)
        else:
            target_name = "None"
        return target_name

    @target_name.setter
    def target_name(self, value: str) -> None:
        """Set the target_name.

        Args:
            value: the new description to use.
        """
        self._description = value

    def found_by(self, the_actor: Actor) -> Locator:
        """Get the Playwright Locator described by this Target.

        Args:
            the_actor: the Actor who should find this Locator.

        Returns:
            The Locator which describes the element.
        """
        page = the_actor.ability_to(BrowseTheWebSynchronously).current_page

        if not self.manipulations:
            msg = f"{self} does not have any locator strategy set."
            raise TargetingError(msg)

        # Start with a base locator to ease typing. :face_rolling_eyes:
        locator = page.locator("html")
        for manipulation in self.manipulations:
            if manipulation.args is None and manipulation.kwargs is None:
                locator = getattr(locator, manipulation.name)
            else:
                args = []
                for arg in manipulation.args:
                    arg_to_append = arg
                    if isinstance(arg, Target):
                        arg_to_append = arg.found_by(the_actor)
                    args.append(arg_to_append)
                kwargs = {
                    k: v.found_by(the_actor) if isinstance(v, Target) else v
                    for k, v in manipulation.kwargs.items()
                }
                locator = getattr(locator, manipulation.name)(*args, **kwargs)

        return locator

    def __repr__(self) -> str:
        """Get a human-readable representation of this Target.

        Returns:
            A string representing this Target.
        """
        return self.target_name

    __str__ = __repr__

    def __init__(self, name: str | None = None) -> None:
        self._description = name
        self.manipulations = []
