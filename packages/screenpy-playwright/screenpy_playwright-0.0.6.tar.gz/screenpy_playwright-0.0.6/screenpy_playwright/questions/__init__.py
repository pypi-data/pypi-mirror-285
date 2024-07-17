"""Questions that can be asked using the Abilities in ScreenPy: Playwright."""

from .attribute import Attribute
from .browser_url import BrowserURL
from .element import Element
from .number import Number
from .text import Text

# Natural-language-enabling aliases
TheAttribute = Attribute
TheBrowserURL = BrowserURL
TheElement = Element
TheNumber = Number
TheText = Text

__all__ = [
    "Attribute",
    "BrowserURL",
    "Element",
    "Number",
    "Text",
    "TheAttribute",
    "TheBrowserURL",
    "TheElement",
    "TheNumber",
    "TheText",
]
