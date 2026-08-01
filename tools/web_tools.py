"""
Web Fetching and Scraping Automation Tools.
"""

import urllib.request
import urllib.parse
import re
from agent.tools import tool

@tool
def fetch_webpage_content(url: str) -> str:
    """
    Fetch raw HTML text content from a web URL and extract plain text text.

    Args:
        url: The web URL to fetch (e.g. 'https://en.wikipedia.org/wiki/Python').

    Returns:
        Extracted text content from the webpage.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python-Automation-Agent/1.0'
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')

        # Basic HTML strip via regex
        clean_text = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        clean_text = re.sub(r'<style.*?>.*?</style>', '', clean_text, flags=re.DOTALL | re.IGNORECASE)
        clean_text = re.sub(r'<.*?>', ' ', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        if len(clean_text) > 3000:
            return clean_text[:3000] + "... [content truncated]"
        return clean_text if clean_text else "Page returned no readable text content."
    except Exception as e:
        return f"Failed to fetch web URL '{url}': {str(e)}"


@tool
def search_web(query: str) -> str:
    """
    Search the web for information using DuckDuckGo HTML search.

    Args:
        query: Search query string (e.g. 'Python 3.12 release notes').

    Returns:
        List of relevant search result snippets and URLs.
    """
    try:
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python-Agent/1.0'
        }

        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')

        # Extract search results snippet text
        results = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.DOTALL)
        links = re.findall(r'<a class="result__url[^>]*href="([^"]+)"', html, re.DOTALL)

        if not results:
            return f"No direct search results found for query '{query}'."

        formatted = [f"Search Results for '{query}':"]
        for idx, (snippet, link) in enumerate(zip(results[:5], links[:5]), 1):
            clean_snippet = re.sub(r'<.*?>', '', snippet).strip()
            formatted.append(f"{idx}. {clean_snippet}\n   URL: {link.strip()}\n")

        return "\n".join(formatted)
    except Exception as e:
        return f"Web search encountered an error: {str(e)}"
