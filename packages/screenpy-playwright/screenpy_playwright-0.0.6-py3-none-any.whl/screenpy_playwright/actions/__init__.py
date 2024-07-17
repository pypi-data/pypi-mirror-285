"""Actions enabled by the Abilities in ScreenPy: Playwright."""

from .click import Click
from .enter import Enter
from .open import Open
from .refresh_the_page import RefreshThePage
from .save_screenshot import SaveScreenshot
from .scroll import Scroll
from .select import Select

# Natural-language-enabling aliases
Clicks = Click
Enters = Enter
GoTo = GoesTo = Visit = Visits = Opens = Open
Refresh = Refreshes = RefreshesThePage = RefreshThePage
SavesScreenshot = SavesAScreenshot = SaveAScreenshot = SaveScreenshot
Scrolls = Scroll
Selects = Select


__all__ = [
    "Click",
    "Clicks",
    "Enter",
    "Enters",
    "GoTo",
    "GoesTo",
    "Open",
    "Opens",
    "RefreshThePage",
    "RefreshesThePage",
    "SaveScreenshot",
    "SaveAScreenshot",
    "SavesScreenshot",
    "SavesAScreenshot",
    "Scroll",
    "Scrolls",
    "Select",
    "Selects",
    "Visit",
    "Visits",
]
