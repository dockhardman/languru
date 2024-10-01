import time
from pathlib import Path
from typing import List, Optional, Text, Union, cast

from bs4 import BeautifulSoup
from diskcache import Cache
from playwright.sync_api import BrowserContext
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Playwright
from playwright_stealth import stealth_sync
from pydantic import BaseModel
from yarl import URL

from languru.config import console
from languru.utils._playwright import (
    get_page,
    handle_captcha_page,
    simulate_human_behavior,
    try_close_page,
)
from languru.utils.bs import drop_no_used_attrs
from languru.utils.crawler import escape_query

cache = Cache(Path.home().joinpath(".languru/data/cache/web_cache"))


def google_search_with_page(
    query: Text,
    browser_context: "BrowserContext",
    *,
    num_results: int = 10,
    is_stealth: bool = False,
    timeout_ms: int = 60000,
    google_home_url: Text | URL = URL("https://www.google.com").with_query(
        {"hl": "en", "sa": "X"}
    ),
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
            str(google_home_url),
            timeout=timeout_ms,
            wait_until="domcontentloaded",
        )
        simulate_human_behavior(page, timeout_ms=timeout_ms)

        # Input text into the search box
        search_box = page.locator('textarea[name="q"]')
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
            page.wait_for_selector("div.g", state="visible", timeout=10000)
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
    result_divs = soup.find_all("div", class_="g")

    for div in result_divs:
        # Extract URL
        a_tag = div.find("a")
        if not a_tag or "href" not in a_tag.attrs:  # No URL found
            continue
        url: Optional[Text] = a_tag["href"]
        # Extract title
        title_tag = soup.find("h3")
        title: Optional[Text] = title_tag.get_text() if title_tag else None

        # More reliable way to extract Description
        # Strategy: find the closest following sibling or div/span
        # after the title that contains text
        description: Optional[Text] = None
        # Step 1: Find all span tags
        span_tags = div.find_all("span")
        matching_spans = [
            span.text.strip().strip(" .\n").strip()
            for span in span_tags
            if span.text.strip().endswith("...")
        ]
        if matching_spans:
            description = "\n".join(matching_spans)
        # Step 2: Look for the first sibling with text
        if not description and title_tag:
            # Look for the first sibling with text
            for sibling in title_tag.find_next_siblings():
                if sibling and sibling.get_text(strip=True):
                    description = sibling.get_text(strip=True)
                    break

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


class SearchResult(BaseModel):
    url: Text
    title: Text
    description: Text


class GoogleSearchRemote:

    def __init__(
        self,
        *args,
        timeout_ms: int = 60000,
        cache_dirpath: Optional[Text] = None,
        screenshot_dirpath: Optional[Text] = None,
        debug: bool = False,
        browser_context: Optional["BrowserContext"] = None,
        **kwargs,
    ):
        self.timeout_ms = timeout_ms
        self._cache = Cache(cache_dirpath) if cache_dirpath else cache
        self._screenshot_dirpath = screenshot_dirpath
        self.debug = debug
        self._external_browser_context = browser_context

        self._google_home_url = URL("https://www.google.com").with_query(
            {"hl": "en", "sa": "X"}
        )

    @property
    def screenshot_dirpath(self) -> Optional[Text]:
        return self._screenshot_dirpath

    @property
    def cache(self) -> Cache:
        return self._cache

    def search(
        self,
        query: Text,
        *,
        num_results: int = 10,
        is_stealth: bool = False,
        timeout_ms: Optional[int] = None,
        with_cache: bool = True,
    ) -> List[SearchResult]:
        query = query.strip()
        if not query:
            raise ValueError("Query is empty")
        query = escape_query(query)
        timeout_ms = timeout_ms or self.timeout_ms

        # Check if the result is cached
        if with_cache and query in self.cache:
            return self.cache[query][:num_results]  # type: ignore

        with sync_playwright() as p:
            p = cast(Playwright, p)

            with p.chromium.launch(
                headless=False,
                args=[
                    "--start-maximized",
                    "--disable-features=DownloadBubble",
                ],
            ) as browser:
                context = browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    java_script_enabled=True,
                    timezone_id="Asia/Taipei",
                    geolocation={
                        "latitude": 25.123122964320714,
                        "longitude": 121.52846200172687,
                    },
                    permissions=["geolocation"],
                    color_scheme="no-preference",
                    accept_downloads=False,
                )

                search_results = google_search_with_page(
                    query,
                    browser_context=context,
                    num_results=num_results,
                    is_stealth=is_stealth,
                    timeout_ms=timeout_ms,
                    google_home_url=self._google_home_url,
                    screenshot_filepath=self.screenshot_filepath(),
                    cache_result=self.cache,
                )
                return search_results

    def screenshot_filepath(self, postfix: Optional[Text] = None) -> Optional[Path]:
        if not self.screenshot_dirpath:
            return None
        postfix = postfix if postfix else str(int(time.time()))
        return Path(self.screenshot_dirpath).joinpath(f"screenshot-{postfix}.png")
