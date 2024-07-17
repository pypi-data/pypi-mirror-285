"""Resolutions provide answers to the Actor's Questions."""

from .is_present import IsPresent
from .is_visible import IsVisible

# Natural-language-enabling aliases
Visible = IsVisible
Exists = Exist = Present = IsPresent

__all__ = [
    "Exists",
    "Exist",
    "IsPresent",
    "IsVisible",
    "Present",
    "Visible",
]
