import html2text
import logging
import openai
import re
import requests
import sys
import warnings

from bs4 import BeautifulSoup

from typing import Optional, Union, List
from contextlib import contextmanager

html2text_markdown_converter = html2text.HTML2Text()
html2text_markdown_converter.wrap_links = False
html2text_markdown_converter.ignore_links = False
html2text_markdown_converter.body_width = 0  # Disable line wrapping

SYSTEMPROMPT = (
    "I have scraped a webpage, converted it from HTML into Markdown format, "
    "and enumerated its lines with line numbers. What kind of page is this? "
    "Is it primarily human-readable content? Is it an index or table of "
    "contents that refers the reader to other material? Is it an article? "
    "Is it a whole series of articles? Be descriptive."
)
PROMPT_HUMAN_READABLE_CHECK = (
    "Is this content human-readable? Please respond with one word: Yes or No."
)
PROMPT_LINE_FILTER = """
The scrape includes a lot of unimportant "boilerplate" text that isn't relevant to the substance or content of the page. These unimportant lines include things like navigation menus, copyright notices, affiliate links, user login links, and so on. I'd like your help filtering out these unimportant non-content lines.

Go through each line of the scrape (they're numbered for your convenience). For each line, label it with a one- or two-word description, followed by a dash, followed by either "keep" or "discard".

If a line is blank, ignore it entirely. Skip over it in your output.

Here's an example of what your response should look like (note that in this example, line 4 was a blank line, hence why it was omitted):
1. Header logo - discard
2. Title - keep
3. Menu link - discard
5. Menu link - discard
6. Body text - keep
7. Body text - keep
8. Advertisement - discard
etc.
"""


# With the help of this function, we can prevent urllib3 from spewing obnoxious
# warnings about SSL certificates and other HTTP-related stuff while fetching URLs.
@contextmanager
def suppress_warnings():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield


# Fix a ridiculous formatting error in which sometimes links get double slashes.
def _remove_double_slashes(url: str):
    m = re.match(r"^(\w+)\:(/*)(.*)", url)
    if not m:
        # Doesn't start with a protocol designator. Doesn't look like a URL.
        return url

    protocol = m.group(1)

    s = m.group(3)
    s = re.sub(r"/+", "/", s)

    retval = f"{protocol}://{s}"
    return retval


def _get_page_as_markdown(url: str, logger: logging.Logger) -> str:
    if not url:
        return
    url = f"{url}"
    url = _remove_double_slashes(url)

    response = None

    try:
        # Get the site's presumed base URL from the URL itself.
        url_proto, url_therest = url.split("//")
        url_domain = url_therest.split("/")[0]
        base_url = f"{url_proto}//{url_domain}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.126 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

        with suppress_warnings():
            response = requests.get(
                url,
                timeout=60,
                verify=False,
                headers=headers,
            )
    except Exception:
        # Log the exception with traceback
        logger.exception("Exception in _get_page_as_markdown while fetching page")
        return None

    if not response:
        logger.warning(f"No content retrieved from URL: {url}")
        return None

    if response.status_code != 200:
        logger.warning(f"Fetch failed for URL: {url}")
        return None

    # Look for an HTML tag to confirm that this is in fact HTML content.
    # Look for a <base> tag to get the base URL.
    # If it doesn't exist, just keep the base URL that was gleaned from the target URL.
    try:
        content = response.content.decode("utf-8", errors="ignore")
        soup = BeautifulSoup(content, "html.parser")

        html_tag = soup.find("html")
        if not html_tag:
            logger.warning("_get_page_as_markdown failed because no html tag")
            return None

        base_tag = soup.find("base")
        if base_tag:
            base_url = base_tag["href"]
    except Exception:
        # Log the exception with traceback
        logger.exception("Exception in _get_page_as_markdown while parsing HTML")
        return None

    html_content = response.text
    html2text_markdown_converter.baseurl = base_url

    markdown_content = None
    try:
        markdown_content = html2text_markdown_converter.handle(html_content)
    except Exception:
        # Log the exception with traceback
        logger.exception("Exception in _get_page_as_markdown while converting HTML")
        return None

    if not markdown_content:
        return None

    # We'll now strip lines and consolidate whitespace.
    lines = markdown_content.splitlines()
    lines = [line.strip() for line in lines]
    markdown_content = "\n".join(lines)
    markdown_content = re.sub(r"\n\n\n+", "\n\n", markdown_content)

    return markdown_content


def _call_gpt(
    conversation: Union[str, dict, List[dict]],
    openai_client: openai.OpenAI,
) -> str:
    if isinstance(conversation, str):
        conversation = [{"role": "user", "content": conversation}]
    elif isinstance(conversation, dict):
        conversation = [conversation]

    answer_full = ""
    while True:
        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            temperature=0,
        )

        answer = completion.choices[0].message.content
        answer_full += answer + "\n"

        conversation.append({"role": "assistant", "content": answer})

        if completion.choices[0].finish_reason == "length":
            continue

        break

    answer_full = answer_full.strip()
    return answer_full


def webpage2content(
    url: str,
    openai_client: openai.OpenAI,
    logger: Optional[logging.Logger] = None,
):
    if not logger:
        logger = logging.getLogger(__name__)

    markdown = _get_page_as_markdown(url, logger=logger)
    if not markdown:
        return None

    if not isinstance(markdown, str):
        logger.error("markdown somehow came back as something other than a string.")
        return None

    markdown = markdown.strip()
    if not markdown:
        return None

    mdlines = markdown.splitlines()
    mdlines = [f"{linenum+1}. {linetext}" for linenum, linetext in enumerate(mdlines)]
    markdown_with_linenums = "\n".join(mdlines)

    conversation = [
        {"role": "system", "content": SYSTEMPROMPT},
        {"role": "user", "content": markdown_with_linenums},
    ]

    try:
        # First, we get the AI to describe the page to us in its own words.
        # We are uninterested in this answer. We just want it to have this conversation
        # with itself so that it knows what's going to be important in subsequent steps.
        gptreply_page_description = _call_gpt(
            conversation=conversation,
            openai_client=openai_client,
        )
        logger.debug(
            f"webpage2content asked GPT to describe the page at {url}.\n\n{gptreply_page_description}"
        )

        # Next, we simply ask it whether or not the content is human-readable.
        conversation.append({"role": "user", "content": PROMPT_HUMAN_READABLE_CHECK})
        gptreply_is_human_readable = _call_gpt(
            conversation=conversation,
            openai_client=openai_client,
        )

        is_human_readable = "yes" in gptreply_is_human_readable.lower()
        if not is_human_readable:
            logger.warning(f"Page at URL {url} is not human-readable")
            return None

    except Exception:
        # Log the exception with traceback
        logger.exception("Exception in webpage2content while determining content type")
        return None

    try:
        conversation.append({"role": "user", "content": PROMPT_LINE_FILTER})
        gptreply_line_filtration = _call_gpt(
            conversation=conversation,
            openai_client=openai_client,
        )

    except Exception:
        # Log the exception with traceback
        logger.exception(
            "Exception in webpage2content while determining which lines to filter"
        )
        return None

    mdlines = markdown.splitlines()
    filterlines = gptreply_line_filtration.splitlines()

    for filterline in filterlines:
        try:
            linenumstr, linetext = filterline.split(".", maxsplit=1)
            linenum = int(linenumstr) - 1

            if linetext.lower().endswith("discard"):
                mdlines[linenum] = ""

        except Exception as ex:
            logger.warning(f"Exception during line filtration: {ex}")
            pass

    markdown = "\n".join(mdlines)
    markdown = re.sub(r"\n\n\n+", "\n\n", markdown)

    return markdown


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: webpage2content <URL> [OPENAI_API_KEY]")
        sys.exit(1)

    url = sys.argv[1]

    OPENAI_API_KEY = None
    if len(sys.argv) > 2:
        OPENAI_API_KEY = sys.argv[2]

    openai_client = None
    if OPENAI_API_KEY:
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    else:
        openai_client = openai.OpenAI()

    try:
        content = webpage2content(url, openai_client=openai_client)
        print(content)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
