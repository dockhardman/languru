import time
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, List, Optional, Text, Union, cast

from diskcache import Cache
from playwright.sync_api import BrowserContext
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Playwright
from playwright_stealth import stealth_sync
from yarl import URL

from languru.config import console
from languru.types.web.documents import HtmlDocument
from languru.utils._playwright import simulate_captcha, simulate_human_behavior
from languru.utils.common import debug_print_banner
from languru.utils.html_parser import as_markdown, drop_no_used_attrs
from languru.web.remote.google_search import google_search_with_page

cache = Cache(Path.home().joinpath(".languru/data/cache/web_cache"))


@contextmanager
def browser_context():
    with sync_playwright() as p:
        p = cast(Playwright, p)
        with p.chromium.launch(
            headless=False,
            args=[
                "--start-maximized",
                "--disable-features=DownloadBubble",
                "--mute-audio",
            ],
        ) as browser:
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                java_script_enabled=True,
                timezone_id="America/New_York",
                geolocation={"latitude": 40.7128, "longitude": -74.0060},
                permissions=["geolocation"],
                color_scheme="no-preference",
                accept_downloads=False,
            )
            yield context


def request_with_page(
    url: Union[URL, Text],
    browser_context: "BrowserContext",
    *,
    timeout_ms: int = 30000,
    is_stealth: bool = False,
    screenshot_filepath: Optional[Union[Path, Text]] = None,
    cache_result: Cache = cache,
    close_page: Optional[bool] = None,
    debug: bool = False,
    default_path_num: int = 0,
) -> Optional[Text]:

    content: Optional[Text] = None
    if browser_context.pages:
        page = browser_context.pages[default_path_num]
    else:
        page = browser_context.new_page()
    if is_stealth:
        stealth_sync(page)

    try:
        page.goto(str(url), timeout=timeout_ms, wait_until="domcontentloaded")
        simulate_human_behavior(page, timeout_ms=timeout_ms)

        # Check for CAPTCHA
        simulate_captcha(page)

        content = page.content()
        content = drop_no_used_attrs(content)
        if debug:
            debug_print_banner(content, title=f"Content of '{url}'")

        if screenshot_filepath:
            page.screenshot(
                type="jpeg",
                path=screenshot_filepath,
            )
        cache_result[url] = content

    except PlaywrightTimeoutError:
        console.print_exception()
        if screenshot_filepath:
            page.screenshot(type="jpeg", path=screenshot_filepath)

    try:
        if close_page:
            page.close()
    except Exception:
        pass
    return content


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

    def search_with_context(
        self,
        query: Text,
        context: "BrowserContext",
        *args,
        num_results: int = 10,
        timeout_ms: int = 30000,
        is_stealth: bool = False,
        filter_out_urls: Callable[[Text], bool] = lambda x: False,
        sleep_interval: int = 0,
        **kwargs,
    ) -> List["HtmlDocument"]:
        out: List["HtmlDocument"] = []
        query = query.replace('"', "").replace("'", "").strip()
        if not query:
            raise ValueError("Query is empty")

        # Search google home page with browser
        google_search_results = google_search_with_page(
            query,
            browser_context=context,
            num_results=num_results,
            screenshot_filepath=None,
            cache_result=self.web_cache,
        )
        for _gg_res in google_search_results[:num_results]:
            if filter_out_urls(_gg_res.url):
                continue

            html_doc = HtmlDocument.from_search_result(_gg_res)

            # Request url content with browser
            html_doc.html_content = request_with_page(
                html_doc.url,
                browser_context=context,
                timeout_ms=timeout_ms,
                is_stealth=is_stealth,
                screenshot_filepath=None,
                cache_result=self.web_cache,
                debug=self.debug,
            )
            if html_doc.html_content:
                html_doc.markdown_content = as_markdown(
                    html_doc.html_content, url=html_doc.url, debug=self.debug
                )
            else:
                console.print(f"Failed to get content from {html_doc.url}")

            out.append(html_doc)

            if sleep_interval > 0:
                time.sleep(sleep_interval)

        return out

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
