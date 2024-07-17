"""Ask about the current browser URL."""

from screenpy import Actor, beat

from screenpy_playwright.abilities import BrowseTheWebSynchronously


class BrowserURL:
    """Ask about the current browser URL.

    Examples::

        the_actor.should(
            See.the(BrowserURL(), ReadsExactly("https://www.nintendo.com"))
        )
    """

    def describe(self) -> str:
        """Describe the Question."""
        return "The current browser URL."

    @beat("{} reads the current browser URL.")
    def answered_by(self, the_actor: Actor) -> str:
        """Ask the Actor about the current browser URL."""
        page = the_actor.ability_to(BrowseTheWebSynchronously).current_page

        # On single-page applications, after clicking an element which redirects
        # the user, the browser URL is not immediately updated in Playwright.
        # This can cause the page URL to be stale if requested immediately after
        # interacting with such an element, even if the page has fully loaded.
        # This appears to be because single-page applications hijack the typical
        # browser routing behavior Playwright seems to rely on.
        # As a workaround, checking an element will force Playwright to refresh
        # its information about the page, including the current URL.
        page.locator("html").is_visible()
        return page.url
