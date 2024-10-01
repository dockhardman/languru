from pathlib import Path
from typing import List, Optional, Text, Union

from bs4 import BeautifulSoup
from diskcache import Cache
from playwright.sync_api import BrowserContext
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_sync
from yarl import URL

from languru.config import console
from languru.types.web.search import SearchResult
from languru.utils._playwright import (
    get_page,
    handle_captcha_page,
    simulate_human_behavior,
    try_close_page,
)
from languru.utils.bs import drop_no_used_attrs
from languru.utils.crawler import escape_query

HOME_URL = "https://www.bing.com/"

cache = Cache(Path.home().joinpath(".languru/data/cache/web_cache"))


def search_with_page(
    query: Text,
    browser_context: "BrowserContext",
    *,
    num_results: int = 10,
    is_stealth: bool = False,
    timeout_ms: int = 60000,
    home_url: Text | URL = URL(HOME_URL),
    screenshot_filepath: Optional[Union[Path, Text]] = None,
    cache_result: Cache = cache,
    close_page: Optional[bool] = None,
    page_index: Optional[int] = None,
    raise_captcha: bool = False,
    skip_captcha: bool = False,
    captcha_manual_solve: bool = False,  # Default behavior.
) -> List["SearchResult"]:
    """
    Search for a query on Google and return the search results.
    """
    query = query.strip()
    if not query:
        raise ValueError("Query is empty")
    query = escape_query(query)

    search_results: List["SearchResult"] = []

    # Get the page
    page = get_page(browser_context, page_index)

    # Stealth mode
    if is_stealth:
        stealth_sync(page)

    try:
        page.goto(
            str(home_url),
            timeout=timeout_ms,
            wait_until="domcontentloaded",
        )
        simulate_human_behavior(page, timeout_ms=timeout_ms)

        # Input text into the search box
        search_box = page.locator("#sb_form_q")
        search_box.fill(query)

        # Press 'Enter' instead of clicking the search button
        search_box.press("Enter", timeout=1000)

        # Wait for the results page to load
        page.wait_for_load_state("domcontentloaded")
        # page.wait_for_selector("#search")

        # Check for CAPTCHA
        if not handle_captcha_page(
            page,
            raise_captcha=raise_captcha,
            skip_captcha=skip_captcha,
            captcha_manual_solve=captcha_manual_solve,
        ):
            return []

        # Wait for the search results to load
        try:
            page.wait_for_selector("#b_results", state="visible", timeout=10000)
        except PlaywrightTimeoutError:
            console.print("Could not find search results, skip it.")
            return []
        simulate_human_behavior(page, timeout_ms=timeout_ms)

        # Get the page content
        content = page.content()
        content = drop_no_used_attrs(content)

        # Parse the search results
        search_results = parse_search_results(content)

        if screenshot_filepath:
            page.screenshot(type="jpeg", path=screenshot_filepath)
        cache_result[query] = search_results

    except PlaywrightTimeoutError:
        console.print_exception()
        if screenshot_filepath:
            page.screenshot(type="jpeg", path=screenshot_filepath)

    if close_page:
        try_close_page(page)
    return search_results[:num_results]


def parse_search_results(
    html_content: Text | BeautifulSoup, *, debug: bool = False
) -> List["SearchResult"]:
    soup = (
        BeautifulSoup(html_content, "html.parser")
        if isinstance(html_content, Text)
        else html_content
    )
    search_results = []

    # Find all search result divs
    result_divs = soup.find_all("li", class_="b_algo")

    for div in result_divs:
        # Extract URL
        a_tag = div.find("a")
        if not a_tag or "href" not in a_tag.attrs:  # No URL found
            continue
        url: Optional[Text] = a_tag["href"]
        # Extract title
        title_tag = div.find("h2")
        title: Optional[Text] = title_tag.get_text() if title_tag else None

        # More reliable way to extract Description
        # Strategy: find the closest following sibling or div/span
        # after the title that contains text
        description: Optional[Text] = None
        description_tag = div.find("p")
        description = description_tag.get_text(strip=True) if description_tag else None

        if url and title and description:
            result = SearchResult.model_validate(
                {"url": url, "title": title, "description": description}
            )
            search_results.append(result)
        else:
            if debug:
                console.print("")
                console.print(f"Could not parse search result:\n{div=}")
                console.print("")

    return search_results
