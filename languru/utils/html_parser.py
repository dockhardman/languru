import re
from typing import Optional, Text
from urllib.parse import unquote

from bs4 import BeautifulSoup, Comment

from languru.config import console
from languru.utils.common import debug_print_banner


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


def drop_no_used_attrs(html_content: "Text | BeautifulSoup") -> Text:
    from bs4 import BeautifulSoup

    soup = (
        BeautifulSoup(html_content, "html.parser")
        if isinstance(html_content, Text)
        else html_content
    )
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


def drop_all_styles(html_content: "Text | BeautifulSoup") -> Text:
    from bs4 import BeautifulSoup

    soup = (
        BeautifulSoup(html_content, "html.parser")
        if isinstance(html_content, Text)
        else html_content
    )
    for tag in soup.find_all():
        # Check if the tag has a 'style' attribute
        if "style" in tag.attrs:
            # Remove the 'style' attribute
            del tag["style"]
    return str(soup)


def drop_all_tags(html_content: "Text | BeautifulSoup") -> Text:
    from bs4 import BeautifulSoup

    soup = (
        BeautifulSoup(html_content, "html.parser")
        if isinstance(html_content, Text)
        else html_content
    )
    # Drop <script> and other tags
    for tag in soup.find_all(["script", "style", "link", "meta", "svg", "path"]):
        tag.decompose()  # Remove the tag from the soup

    # Find all tags that contain 'css' in their name or attributes
    css_tags = soup.find_all(lambda tag: "css" in tag.name.lower())
    for tag in css_tags:
        tag.decompose()

    return str(soup)


def drop_all_comments(html_content: "Text | BeautifulSoup") -> Text:
    from bs4 import BeautifulSoup

    soup = (
        BeautifulSoup(html_content, "html.parser")
        if isinstance(html_content, Text)
        else html_content
    )
    for tag in soup.find_all(text=lambda text: isinstance(text, Comment)):
        tag.extract()

    return str(soup)


def as_markdown(
    html_content: Text, *, url: Optional[Text] = None, debug: bool = True
) -> Optional[Text]:
    from languru.utils.md_parser import clean_markdown_links

    if not html_content:
        return None

    html_main_content = parse_html_main_content(html_content, url=url)

    if html_main_content:
        markdown_content = html_to_markdown(html_main_content)
        markdown_content = clean_markdown_links(markdown_content)
        debug_print_banner(
            markdown_content, title="Parsed Markdown Content", debug=debug
        )
        return markdown_content

    console.print("Can not parse html content.")
    return None
