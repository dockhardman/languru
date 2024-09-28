import re
from typing import TYPE_CHECKING

from languru.config import console

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


def simulate_captcha(page: "Page"):
    content = page.content()
    # Check for CAPTCHA
    if re.search(r"verifying you are human", content, re.IGNORECASE) or re.search(
        r"check you are human", content, re.IGNORECASE
    ):
        console.print("CAPTCHA detected. Please solve it manually.")
        page.pause()
        # Optionally, wait for user input before continuing
        input("Press Enter after you've completed the verification...")
