from typing import Callable, Coroutine, List, Literal, Sequence

from languru.types.web.search import SearchResult
from languru.web.remote.bing import search_with_page as bing_search_with_page
from languru.web.remote.duckduckgo import (
    search_with_page as duckduckgo_search_with_page,
)
from languru.web.remote.google_search import search_with_page as google_search_with_page
from languru.web.remote.yahoo_search import search_with_page as yahoo_search_with_page


def get_search_engines(
    search_engines: Sequence[Literal["google", "bing", "yahoo", "duckduckgo"]]
) -> List[Callable[..., Coroutine[None, None, List["SearchResult"]]]]:
    search_engines_list = []
    if "google" in search_engines:
        search_engines_list.append(google_search_with_page)
    if "bing" in search_engines:
        search_engines_list.append(bing_search_with_page)
    if "yahoo" in search_engines:
        search_engines_list.append(yahoo_search_with_page)
    if "duckduckgo" in search_engines:
        search_engines_list.append(duckduckgo_search_with_page)
    if not search_engines_list:
        raise ValueError("No search engines provided")
    return search_engines_list
