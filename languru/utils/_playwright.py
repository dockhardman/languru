from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page


def simulate_human_behavior(page: "Page", timeout_ms: int = 3000):
    # Wait for the network to be idle
    page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
    # Scroll the page
    page.evaluate(
        """
        window.scrollTo(0, 200);
        """
    )
    # Wait a bit more for any scrolling-triggered content
    page.wait_for_timeout(3000)
