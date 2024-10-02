import re
from typing import TYPE_CHECKING, Optional, TypeVar

from playwright.sync_api import BrowserContext

from languru.config import console
from languru.exceptions import CaptchaDetected

if TYPE_CHECKING:
    from playwright.sync_api import Page


T = TypeVar("T")


def try_close_page(page: "Page"):
    try:
        page.close()
    except Exception:
        pass


def get_page(
    browser_context: "BrowserContext", page_index: Optional[int] = None
) -> "Page":
    # Get the page
    if page_index is not None:
        if len(browser_context.pages) > page_index:
            page = browser_context.pages[page_index]
        else:
            console.print(
                f"Page index {page_index} not found, creating a new page.",
                style="yellow",
            )
            page = browser_context.new_page()
    else:
        page = browser_context.new_page()
    return page


def handle_captcha_page(
    page: "Page",
    *,
    raise_captcha: bool = False,
    skip_captcha: bool = False,
    captcha_manual_solve: bool = False,  # Default behavior.
) -> bool:  # Return True if captcha is solved, False if captcha is skipped.
    if is_captcha(page):
        if raise_captcha:
            console.print("Captcha detected")
            raise CaptchaDetected("Captcha detected")
        elif skip_captcha:
            console.print("Captcha detected, skipping...")
            try_close_page(page)
            return False
        elif captcha_manual_solve:
            console.print("Captcha detected, solving...")
            page.bring_to_front()
            page.pause()
        else:
            console.print("Captcha detected, solving...")
            page.bring_to_front()
            page.pause()
    return True


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
            console.print(f"Captcha element found: {selector}")
            return True

    # Check for CAPTCHA
    if re.search(r"verifying you are human", content, re.IGNORECASE) or re.search(
        r"check you are human", content, re.IGNORECASE
    ):
        console.print("The page is verifying you are human.")
        return True

    # Check google recaptcha
    captcha_element = soup.find("input", {"name": "g-recaptcha-response"})
    if captcha_element:
        console.print(f"Captcha element found: {captcha_element}")
        return True

    # Check for captcha in content
    if "unusual traffic" in content.lower():
        console.print("The page is a captcha.")
        return True

    # Check for captcha in title
    if soup.title and "captcha" in soup.title.text.lower():
        console.print(f"Captcha in title: {soup.title.text}")
        return True

    # Check for captcha in url
    if "captcha" in current_url or "challenge" in current_url:
        console.print(f"Captcha in url: {current_url}")
        return True

    return False
