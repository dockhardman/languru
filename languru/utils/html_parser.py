import re
from typing import TYPE_CHECKING, Optional, Text
from urllib.parse import unquote

from languru.config import console

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


def html_to_markdown(html: Text) -> Text:
    """
    Convert HTML content to Markdown format.

    Parameters
    ----------
    html : Text
        The HTML content to be converted.

    Returns
    -------
    Text
        The converted Markdown content.
    """

    # Convert headers
    markdown = re.sub(r"<h2.*?>(.*?)</h2>", r"\n## \1\n", html)
    markdown = re.sub(r"<h3.*?>(.*?)</h3>", r"\n### \1\n", markdown)
    # Convert paragraphs
    markdown = re.sub(r"<p.*?>(.*?)</p>", r"\n\1\n", markdown)
    # Convert bold text
    markdown = re.sub(r"<b>(.*?)</b>", r"**\1**", markdown)
    markdown = re.sub(r"<strong>(.*?)</strong>", r"**\1**", markdown)
    # Convert links
    markdown = re.sub(r'<a.*?href="(.*?)".*?>(.*?)</a>', r"[\2](\1)", markdown)
    # Remove superscript references
    markdown = re.sub(r"<sup.*?>.*?</sup>", "", markdown)
    # Remove any remaining HTML tags
    markdown = re.sub(r"<.*?>", "", markdown)
    # Clean up extra whitespace
    markdown = re.sub(r"\n\s*\n", "\n\n", markdown)
    markdown = markdown.strip()
    return markdown


def parse_html_main_content(
    html_content: Text, *, url: Optional[Text] = None
) -> Optional[Text]:
    """
    Extract the main content from HTML.

    This function uses BeautifulSoup to parse the provided HTML content
    and attempts to find the main content within various common HTML
    structures.

    Parameters
    ----------
    html_content : Text
        The HTML content from which to extract the main content.

    Returns
    -------
    Optional[Text]
        The extracted main content as HTML if found, otherwise None.
    """

    from bs4 import BeautifulSoup

    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove all script tags
    soup = remove_javascript(soup)
    soup = remove_font(soup)

    for a in soup.find_all("a", href=True):
        a["href"] = unquote(a["href"])

    main_content = find_main_content(soup)

    if main_content:
        # Extract text
        text = main_content.get_text(separator="\n", strip=True)

        # Clean up the text
        text = re.sub(r"\n+", "\n", text)  # Remove multiple newlines
        text = re.sub(r"\s+", " ", text)  # Replace multiple spaces with single space
        text = text.strip()

        console.print(f"HTML main content length: {len(text)}")
        return text
    else:
        console.print(f"No main content found on the page: {url}")
        return None


def remove_font(soup: "BeautifulSoup") -> "BeautifulSoup":
    for tag in soup.find_all(True):
        if tag.has_attr("style"):
            del tag["style"]
        if tag.has_attr("font"):
            del tag["font"]
    return soup


def remove_javascript(soup: "BeautifulSoup") -> "BeautifulSoup":
    # Remove all script tags
    for script in soup(["script", "style"]):
        script.decompose()

    # Remove inline JavaScript
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr.startswith("on") or (
                isinstance(tag.get(attr), str) and tag[attr].startswith("javascript:")
            ):
                del tag[attr]

    # Remove any remaining JavaScript code within HTML tags
    for tag in soup.find_all(True):
        if tag.string:
            tag.string = re.sub(r"javascript:", "", tag.string)

    return soup


def clean_up_content(content_block):
    # Decompose less relevant tags
    for unwanted in content_block.select(
        "script, style, nav, header, footer, aside, form"
    ):
        unwanted.decompose()
    return content_block


def find_main_content(soup: "BeautifulSoup"):
    # Use CSS selectors to match multiple possible content holders
    content_selectors = [
        "main",  # Prioritizing semantic tags
        "article",  # Prioritizing semantic tags
        '[role="main"]',  # Prioritizing semantic tags
        ".post",  # Common content class names
        ".article",  # Common content class names
        ".content",  # Common content class names
        ".entry",  # Common content class names
        'div[class*="content"]',  # Wildcard matches for content-related ids/classes
        'div[id*="content"]',  # Wildcard matches for content-related ids/classes
        # "#content",
        # "#main-content",
        # ".article-content",
        # ".blog-post-content",
        # ".content",
        # ".entry-content",
        # ".main-content",
        # ".news-article",
        # ".post-content",
        # "article",
        # "main",
        # '[role="main"]',
    ]
    # Try to find the main content using the selectors
    for selector in content_selectors:
        main_content = soup.select_one(selector)
        if main_content and len(main_content.get_text(strip=True)) > 200:
            return clean_up_content(main_content)

    # Fallback to analyzing large text blocks if no main content is detected
    potential_blocks = [
        tag
        for tag in soup.find_all(["div", "section", "article"])
        if len(tag.get_text(strip=True)) > 200
        and not tag.find(["nav", "header", "footer", "aside", "form"])
    ]
    if potential_blocks:
        main_content = max(
            potential_blocks, key=lambda tag: len(tag.get_text(strip=True))
        )
        return clean_up_content(main_content)

    return None