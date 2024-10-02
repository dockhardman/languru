import re
from typing import TYPE_CHECKING, Optional, TypeVar

from playwright.async_api import BrowserContext

from languru.config import console
from languru.exceptions import CaptchaDetected
from languru.utils.common import try_await_or_none

if TYPE_CHECKING:
    from playwright.async_api import Page


T = TypeVar("T")


async def try_close_page(page: "Page"):
    await try_await_or_none(page.close)


async def get_page(
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
            page = await browser_context.new_page()
    else:
        page = await browser_context.new_page()
    return page


async def handle_captcha_page(
    page: "Page",
    *,
    raise_captcha: bool = False,
    skip_captcha: bool = False,
    captcha_manual_solve: bool = False,  # Default behavior.
) -> bool:  # Return True if captcha is solved, False if captcha is skipped.
    if await is_captcha(page):
        if raise_captcha:
            console.print("Captcha detected")
            raise CaptchaDetected("Captcha detected")
        elif skip_captcha:
            console.print("Captcha detected, skipping...")
            await try_close_page(page)
            return False
        elif captcha_manual_solve:
            console.print("Captcha detected, solving...")
            await page.bring_to_front()
            await page.pause()
        else:
            console.print("Captcha detected, solving...")
            await page.bring_to_front()
            await page.pause()
    return True


async def simulate_human_behavior(page: "Page", timeout_ms: int = 3000):
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

    # Wait for the network to be idle
    await try_await_or_none(
        page.wait_for_load_state,
        "domcontentloaded",
        timeout=timeout_ms,
        _error_message="Error simulating human behavior: {error}",
    )

    # Scroll the page
    await try_await_or_none(
        page.evaluate,
        """
            window.scrollTo(0, 200);
            """,
        _error_message="Error simulating human behavior: {error}",
    )

    # Wait a bit more for any scrolling-triggered content
    await try_await_or_none(
        page.wait_for_timeout,
        3000,
        _error_message="Error simulating human behavior: {error}",
    )


async def is_captcha(page: "Page") -> bool:
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

    content = await page.content()
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
        if await page.query_selector(selector):
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
