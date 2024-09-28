import time
from pathlib import Path
from typing import List, Optional, Text, cast

from bs4 import BeautifulSoup
from diskcache import Cache
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Playwright
from playwright_stealth import stealth_sync
from pydantic import BaseModel
from rich.style import Style
from yarl import URL

from languru.config import console


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
        **kwargs,
    ):
        self.timeout_ms = timeout_ms
        self._cache = Cache(self.get_web_cache_dirpath(cache_dirpath))
        self._screenshot_dirpath = screenshot_dirpath
        self.debug = debug

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
                page = context.new_page()
                if is_stealth:
                    stealth_sync(page)

                try:
                    page.goto(
                        str(self._google_home_url),
                        timeout=timeout_ms,
                        wait_until="domcontentloaded",
                    )
                    self._simulate_human_behavior(page, timeout_ms=timeout_ms)

                    # Input text into the search box
                    search_box = page.locator('textarea[name="q"]')
                    search_box.fill(query)

                    # Click the search button
                    search_button = page.get_by_role(
                        "button", name="Google Search"
                    ).first
                    search_button.wait_for(state="visible")
                    search_button.scroll_into_view_if_needed()
                    if search_button.count() == 0:
                        search_button = page.locator('input[name="btnK"]').first
                        search_button.wait_for(state="visible")

                    search_button.click(timeout=1000, force=True)

                    # Wait for the results page to load
                    page.wait_for_load_state("domcontentloaded")
                    # page.wait_for_selector("#search")

                    # Wait for the search results to load
                    page.wait_for_selector("div.g", state="visible", timeout=10000)
                    self._simulate_human_behavior(page, timeout_ms=timeout_ms)

                    # Get the page content
                    content = page.content()

                    # Parse the search results
                    search_results = self.parse_search_results(
                        self.drop_no_used_attrs(content)
                    )

                    if self.screenshot_dirpath:
                        page.screenshot(
                            type="jpeg",
                            path=self.get_img_filepath(self.screenshot_dirpath),
                        )
                    self.cache[query] = search_results
                    return search_results[:num_results]

                except PlaywrightTimeoutError:
                    console.print_exception()
                    if self.screenshot_dirpath:
                        page.screenshot(
                            type="jpeg",
                            path=self.get_img_filepath(self.screenshot_dirpath),
                        )
                    return []

    def parse_search_results(self, html_content: Text) -> List["SearchResult"]:
        soup = BeautifulSoup(html_content, "html.parser")
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
                if self.debug:
                    console.print("")
                    console.print(f"Could not parse search result:\n{div=}")
                    console.print("")

        return search_results

    def drop_no_used_attrs(self, html_content: Text) -> Text:
        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup.find_all():
            if "jsname" in tag.attrs:
                del tag["jsname"]
            if "data-ved" in tag.attrs:
                del tag["data-ved"]
            if "data-csiid" in tag.attrs:
                del tag["data-csiid"]
            if "data-atf" in tag.attrs:
                del tag["data-atf"]
            if "ping" in tag.attrs:
                del tag["ping"]
            if "src" in tag.attrs:
                del tag["src"]
            if "jsaction" in tag.attrs:
                del tag["jsaction"]
            if "jscontroller" in tag.attrs:
                del tag["jscontroller"]
            if "style" in tag.attrs:
                del tag["style"]

            if "class" in tag.attrs:
                filtered_classes = [
                    cls for cls in tag["class"] if not (len(cls) == 6 and cls.isalnum())
                ]
                if filtered_classes:
                    tag["class"] = filtered_classes
                else:
                    del tag["class"]

        return str(soup)

    def drop_all_styles(self, html_content: Text) -> Text:
        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup.find_all():
            # Check if the tag has a 'style' attribute
            if "style" in tag.attrs:
                # Remove the 'style' attribute
                del tag["style"]
        return str(soup)

    def get_web_cache_dirpath(self, dirpath: Optional[Text] = None) -> Path:
        if dirpath is None:
            _dirpath = Path.home().joinpath(".languru/data/cache/web_cache")
            _dirpath.mkdir(parents=True, exist_ok=True)
        else:
            _dirpath = Path(dirpath)
        return _dirpath

    def get_img_filepath(
        self, dirpath: Optional[Text] = None, postfix: Optional[Text] = None
    ) -> Path:
        if dirpath is None:
            _dirpath = Path.home().joinpath(".languru/data/screenshot")
            _dirpath.mkdir(parents=True, exist_ok=True)
        else:
            _dirpath = Path(dirpath)
        if postfix is None:
            postfix = str(int(time.time() * 1000))
        return _dirpath.joinpath(f"screenshot-{postfix}.jpg")

    def _simulate_human_behavior(self, page: "Page", timeout_ms: int = 3000):
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

    def _debug_print(self, content: Text, title: Text = "Title", truncate: int = 200):
        if self.debug:
            tag_style = Style(color="green", underline=True, bold=True)
            content = content[:truncate]
            console.print(f"\n<{title}>\n", style=tag_style)
            console.print(content)
            console.print(f"\n</{title}>\n", style=tag_style)
