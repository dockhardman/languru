import re
import time
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Text, Union, cast

from diskcache import Cache
from googlesearch import search as google_search
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Playwright
from playwright_stealth import stealth_sync
from rich.style import Style
from yarl import URL

from languru.config import console, logger
from languru.types.web.documents import HtmlDocument
from languru.utils.html_parser import html_to_markdown, parse_html_main_content
from languru.utils.md_parser import clean_markdown_links

if TYPE_CHECKING:
    from googlesearch import SearchResult


class CrawlerClient:

    def __init__(
        self,
        *,
        cache_dirpath: Optional[Text] = None,
        screenshot_dirpath: Optional[Text] = None,
        debug: bool = False,
    ):
        self.cache_dirpath = cache_dirpath
        self.screenshot_dirpath = screenshot_dirpath
        self.debug = debug

        self.web_cache = Cache(self.get_web_cache_dirpath(cache_dirpath))

    def search(
        self,
        query: Text,
        num_results: int = 5,
        lang: Text = "zh-TW",
        advanced: bool = True,
        sleep_interval: int = 0,
        region: Text = "zh-TW",
    ) -> List["HtmlDocument"]:
        out: List["HtmlDocument"] = []
        for _res in google_search(
            query,
            num_results=num_results,
            lang=lang,
            advanced=advanced,
            sleep_interval=sleep_interval,
            region=region,
        ):
            _res = cast("SearchResult", _res)
            out.append(HtmlDocument.from_search_result(_res))
            if self.debug:
                console.print(f"Fetched url: {_res.url}")
        return out

    def request_url(
        self,
        url: Union[URL, Text],
        *,
        timeout: int = 30000,
        is_stealth: bool = False,
        cache: Optional["Cache"] = None,
    ) -> Optional[Text]:
        url = str(url)
        cache = cache or self.web_cache

        if url in cache and cache[url]:
            logger.debug(f"Cache hit for '{url}'")
            return cache[url]  # type: ignore

        with sync_playwright() as p:
            p = cast(Playwright, p)
            with p.chromium.launch(headless=False) as browser:
                context = browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    java_script_enabled=True,
                    timezone_id="America/New_York",
                    geolocation={"latitude": 40.7128, "longitude": -74.0060},
                    permissions=["geolocation"],
                    color_scheme="no-preference",
                )
                page = context.new_page()
                if is_stealth:
                    stealth_sync(page)

                try:
                    page.goto(str(url), timeout=timeout, wait_until="domcontentloaded")
                    self._simulate_human_behavior(page, timeout=timeout)

                    # Check for CAPTCHA
                    self._simulate_captcha(page)

                    content = page.content()
                    self._debug_print(content, title=f"Content of '{url}'")

                    page.screenshot(
                        type="jpeg",
                        path=self.get_img_filepath(self.screenshot_dirpath),
                    )
                    cache[url] = content
                    return content

                except PlaywrightTimeoutError:
                    console.print_exception()
                    page.screenshot(
                        type="jpeg",
                        path=self.get_img_filepath(self.screenshot_dirpath),
                    )
                    return None

    def as_markdown(self, html_content: Text) -> Optional[Text]:
        if not html_content:
            return None

        html_main_content = parse_html_main_content(html_content)

        if html_main_content:
            markdown_content = html_to_markdown(html_main_content)
            markdown_content = clean_markdown_links(markdown_content)
            self._debug_print(markdown_content, title="Parsed Markdown Content")
            return markdown_content

        console.print("Can not parse html content.")
        return None

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

    def _simulate_human_behavior(self, page: "Page", timeout: int = 3000):
        # Wait for the network to be idle
        page.wait_for_load_state("domcontentloaded", timeout=timeout)
        # Scroll the page
        page.evaluate(
            """
            window.scrollTo(0, 200);
            """
        )
        # Wait a bit more for any scrolling-triggered content
        page.wait_for_timeout(3000)

    def _simulate_captcha(self, page: "Page"):
        content = page.content()
        # Check for CAPTCHA
        if re.search(r"verifying you are human", content, re.IGNORECASE) or re.search(
            r"check you are human", content, re.IGNORECASE
        ):
            console.print("CAPTCHA detected. Please solve it manually.")
            page.pause()
            # Optionally, wait for user input before continuing
            input("Press Enter after you've completed the verification...")

    def _debug_print(
        self, content: Text, title: Text = "Title", truncate: int = 204700
    ):
        if self.debug:
            tag_style = Style(color="green", underline=True, bold=True)
            content = content[:truncate]
            console.print(f"\n<{title}>\n", style=tag_style)
            console.print(content)
            console.print(f"\n</{title}>\n", style=tag_style)
