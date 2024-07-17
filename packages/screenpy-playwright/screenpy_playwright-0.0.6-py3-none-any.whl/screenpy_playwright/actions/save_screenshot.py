"""Save a screenshot of the current page."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from playwright.sync_api import Error as PlaywrightError
from screenpy import AttachTheFile, DeliveryError, UnableToAct, beat

from ..abilities import BrowseTheWebSynchronously

if TYPE_CHECKING:
    from screenpy import Actor
    from typing_extensions import Self


class SaveScreenshot:
    """Save a screenshot of the Actor's current page.

    Use the :meth:`~SaveScreenshot.and_attach_it` method to indicate that this
    screenshot should be attached to all reports through the Narrator's
    adapters. This method also accepts any keyword arguments those adapters
    might require.

    Abilities Required:
        :class:`~screenpy_playwright.abilities.BrowseTheWebSynchronously`

    Examples::

        the_actor.attempts_to(SaveScreenshot("screenshot.png"))

        the_actor.attempts_to(SaveScreenshot.as_(filepath))

        # attach file to the Narrator's reports (behavior depends on adapter).
        the_actor.attempts_to(SaveScreenshot.as_(filepath).and_attach_it())

        # using screenpy_adapter_allure plugin!
        from allure_commons.types import AttachmentTypes
        the_actor.attempts_to(
            SaveScreenshot.as_(filepath).and_attach_it_with(
                attachment_type=AttachmentTypes.PNG,
            ),
        )
    """

    attach_kwargs: dict | None
    path: str
    filename: str

    def describe(self) -> str:
        """Describe the Action in present tense."""
        return f"Save screenshot as {self.filename}"

    @classmethod
    def as_(cls, path: str) -> Self:
        """Supply the name and/or filepath for the screenshot.

        If only a name is supplied, the screenshot will appear in the current
        working directory.

        Args:
            path: The filepath for the screenshot, including its name.
        """
        return cls(path=path)

    def and_attach_it(self, **kwargs: Any) -> Self:  # noqa: ANN401
        """Indicate the screenshot should be attached to any reports.

        This method accepts any additional keywords needed by any adapters
        attached for :external+screenpy:ref:`Narration`.

        Aliases:
            - ``and_attach_it_with``

        Args:
            kwargs: keyword arguments for the adapters used by the narrator.
        """
        self.attach_kwargs = kwargs
        return self

    and_attach_it_with = and_attach_it

    @beat("{} saves a screenshot as {filename}")
    def perform_as(self, the_actor: Actor) -> None:
        """Direct the actor to save a screenshot."""
        current_page = the_actor.ability_to(BrowseTheWebSynchronously).current_page
        if current_page is None:
            msg = "No page has been opened! Cannot save a screenshot."
            raise UnableToAct(msg)

        try:
            screenshot = current_page.screenshot(path=self.path)
        except PlaywrightError as e:
            msg = (
                f"{the_actor} encountered an issue while attempting to "
                f"save a screenshot: {e.__class__.__name__}"
            )
            raise DeliveryError(msg) from e

        Path(self.path).write_bytes(screenshot)

        if self.attach_kwargs is not None:
            the_actor.attempts_to(AttachTheFile(self.path, **self.attach_kwargs))

    def __init__(self, path: str) -> None:
        self.path = path
        self.filename = path.split(os.path.sep)[-1]
        self.attach_kwargs = None
