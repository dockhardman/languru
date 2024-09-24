import re
from typing import Optional, Text
from urllib.parse import unquote

from languru.config import console


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


def parse_html_main_content(html_content: Text) -> Optional[Text]:
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
    for a in soup.find_all("a", href=True):
        a["href"] = unquote(a["href"])
    main_content = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", class_="article-content")
        or soup.find("div", class_="post-content")
        or soup.find("div", class_="entry-content")
        or soup.find("div", class_="content")
        or soup.find("div", class_="main-content")
        or soup.find("div", id="content")
        or soup.find("div", id="main-content")
        or soup.find("div", class_="article")
        or soup.find("div", class_="post")
        or soup.find("div", class_="entry")
        or soup.find("section", class_="article-content")
        or soup.find("section", class_="post-content")
        or soup.find("div", class_="article-body")
        or soup.find("div", class_="post-body")
        or soup.find("div", class_="story-content")
        or soup.find("div", id="article-content")
        or soup.find("div", class_="article-main")
        or soup.find("div", class_="blog-post")
        or soup.find("div", class_="blog-post-content")
        or soup.find("div", class_="news-article")
        or soup.find("div", class_="single-post")
        or soup.find("div", class_="story-body")
        or soup.find("div", class_="post-container")
        or soup.find("div", class_="post-text")
        or soup.find("div", class_="rich-text")
        or soup.find("div", class_="page-content")
        or soup.find("div", class_="cms-content")
        or soup.find("div", class_="mw-parser-output")  # for Wikipedia
        or soup.find("div", class_="bodyContent")  # for some wikis
        or soup.find("div", id="bodyContent")  # for some wikis
        or soup.find("div", id="main_content")
        or soup.find("div", id="main_body")
        or soup.find("div", class_="body")
        or soup.find("div", id="article_show_content")
        or soup.find("id", class_="article_show_content")
    )
    if main_content:
        content_elements = main_content.find_all(  # type: ignore
            ["p", "h1", "h2", "h3"]
        )
        html_main_content = "".join(str(elem) for elem in content_elements)
        console.print(f"HTML main content length: {len(html_main_content)}")
        return html_main_content
    else:
        console.print("No main content found on the page.")
        return None
