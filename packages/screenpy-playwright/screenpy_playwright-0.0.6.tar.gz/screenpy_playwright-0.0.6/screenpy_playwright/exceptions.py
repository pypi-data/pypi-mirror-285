"""Exceptions thrown by ScreenPy: Playwright."""

from screenpy.exceptions import AbilityError, ScreenPyError


class NoPageError(AbilityError):
    """The Actor has no open pages."""


class TargetingError(ScreenPyError):
    """There was an issue targeting an element."""
