import re
from typing import TYPE_CHECKING

from languru.config import console

if TYPE_CHECKING:
    from playwright.sync_api import Page


def simulate_human_behavior(page: "Page", timeout_ms: int = 3000):
    """Simulate human-like behavior on a webpage.

    Parameters
    ----------
    page : Page
        The Playwright Page object representing the webpage.
    timeout_ms : int, optional
        Maximum time to wait for the page to load (default is 3000 ms).

    Raises
    ------
    Exception
        If an error occurs during the simulation process.
    """

    try:
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
    except Exception as e:
        console.print(f"Error simulating human behavior: {e}")


def simulate_captcha(page: "Page"):
    """Check for CAPTCHA presence and prompt user action if detected.

    Parameters
    ----------
    page : Page
        The Playwright Page object representing the webpage.

    Raises
    ------
    Exception
        If an error occurs while checking for CAPTCHA.
    """

    try:
        content = page.content()
        # Check for CAPTCHA
        if re.search(r"verifying you are human", content, re.IGNORECASE) or re.search(
            r"check you are human", content, re.IGNORECASE
        ):
            console.print("CAPTCHA detected. Please solve it manually.")
            page.pause()
            # Optionally, wait for user input before continuing
            input("Press Enter after you've completed the verification...")
    except Exception as e:
        console.print(f"Error simulating captcha: {e}")


def is_captcha(page: "Page") -> bool:
    """Determine if the current page is a CAPTCHA.

    Parameters
    ----------
    page : Page
        The Playwright Page object representing the webpage.

    Returns
    -------
    bool
        True if the page contains a CAPTCHA, False otherwise.

    Raises
    ------
    Exception
        If an error occurs while analyzing the page content.
    """

    from bs4 import BeautifulSoup

    content = page.content()
    soup = BeautifulSoup(content, "html.parser")
    current_url = page.url

    # Check for captcha in selectors
    for selector in (
        "iframe[src*='recaptcha']",
        "#captcha-form",
        "form[action*='challenge']",
        "div.g-recaptcha",
        "input[name='captcha']",
    ):
        if page.query_selector(selector):
            return True

    # Check for CAPTCHA
    if re.search(r"verifying you are human", content, re.IGNORECASE) or re.search(
        r"check you are human", content, re.IGNORECASE
    ):
        console.print("The page is a captcha.")
        return True

    # Check google recaptcha
    captcha_element = soup.find("input", {"name": "g-recaptcha-response"})
    if captcha_element:
        return True

    # Check for captcha in content
    if "captcha" in content.lower() or "unusual traffic" in content.lower():
        return True

    # Check for captcha in title
    if soup.title and "captcha" in soup.title.text.lower():
        return True

    # Check for captcha in url
    if "captcha" in current_url or "challenge" in current_url:
        return True

    return False
