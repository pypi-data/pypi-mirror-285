"""Used to overwrite type hints for Locator methods from Playwright.

Hopefully this is only temporary.  -pgoy 2024-JUL-12
"""

from collections import UserString
from dataclasses import dataclass
from typing import Pattern, TypedDict

from playwright.sync_api import FrameLocator, Locator
from screenpy import Actor as Actor
from typing_extensions import NotRequired, Self, Unpack

from .abilities import BrowseTheWebSynchronously as BrowseTheWebSynchronously
from .exceptions import TargetingError as TargetingError

_ManipulationArgsType = tuple[str | int | None, ...]

class _ManipulationKwargsType(TypedDict):
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
    def __hash__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...
    def __getattr__(self, name: str) -> Target | _Manipulation: ...
    def __call__(
        self,
        *args: Unpack[_ManipulationArgsType],
        **kwargs: Unpack[_ManipulationKwargsType],
    ) -> Target: ...
    def get_locator(self) -> str: ...
    def __init__(
        self,
        target: Target,
        name: str,
        args: _ManipulationArgsType | None = ...,
        kwargs: _ManipulationKwargsType | None = ...,
    ) -> None: ...

class Target(FrameLocator, Locator):
    manipulations: list[_Manipulation]
    first: Target
    last: Target
    owner: Target
    content_frame: Target
    @classmethod
    def the(cls, name: str) -> Self: ...
    def located_by(self, locator: str) -> Target: ...
    def in_frame(self, frame_locator: str) -> Target: ...
    def __getattribute__(self, name: str) -> _Manipulation: ...
    @property
    def target_name(self) -> str: ...
    @target_name.setter
    def target_name(self, value: str) -> None: ...
    def found_by(self, the_actor: Actor) -> Locator: ...
    def __init__(self, name: str | None = None) -> None: ...

    # overridden Locator methods
    def and_(self, locator: Locator | Target) -> Target: ...
    def filter(
        self,
        *,
        has_text: str | Pattern | None = None,
        has_not_text: str | Pattern | None = None,
        has: Locator | Target | None = None,
        has_not: Locator | Target | None = None,
    ) -> Target: ...
    def frame_locator(self, selector: str) -> Target: ...
    def get_by_alt_text(
        self, text: str | Pattern, *, exact: bool | None = None
    ) -> Target: ...
    def get_by_label(
        self, text: str | Pattern, *, exact: bool | None = None
    ) -> Target: ...
    def get_by_placeholder(
        self, text: str | Pattern, *, exact: bool | None = None
    ) -> Target: ...
    def get_by_role(
        self,
        role: str,
        *,
        checked: bool | None = None,
        disabled: bool | None = None,
        expanded: bool | None = None,
        include_hidden: bool | None = None,
        level: int | None = None,
        name: str | Pattern | None = None,
        pressed: bool | None = None,
        selected: bool | None = None,
        exact: bool | None = None,
    ) -> Target: ...
    def get_by_test_id(self, test_id: str | Pattern) -> Target: ...
    def get_by_text(
        self, text: str | Pattern, *, exact: bool | None = None
    ) -> Target: ...
    def get_by_title(
        self, text: str | Pattern, *, exact: bool | None = None
    ) -> Target: ...
    def locator(
        self,
        selector: str | Locator,
        *,
        has_text: str | Pattern | None = None,
        has_not_text: str | Pattern | None = None,
        has: Locator | Target | None = None,
        has_not: Locator | Target | None = None,
    ) -> Target: ...
    def nth(self, index: int) -> Target: ...
    def or_(self, locator: Locator | Target) -> Target: ...
