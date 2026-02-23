from __future__ import annotations

from crewai.tools import tool


@tool
def search_web(query: str) -> str:
  """Search the web for information on a given query."""
  try:
    from duckduckgo_search import DDGS
  except ImportError:
    return (
      "duckduckgo_search is not installed. "
      "Install it with: pip install duckduckgo_search"
    )

  try:
    results = DDGS().text(query, max_results=5)
    if not results:
      return f"No results found for: {query}"

    formatted = []
    for i, r in enumerate(results, 1):
      title = r.get("title", "No title")
      url = r.get("href", "No URL")
      snippet = r.get("body", "No snippet")
      formatted.append(f"{i}. {title}\n   URL: {url}\n   {snippet}")
    return "\n\n".join(formatted)
  except Exception as e:
    return f"Error searching the web: {e}"


@tool
def scrape_webpage(url: str) -> str:
  """Scrape and extract text content from a webpage URL."""
  try:
    import requests
  except ImportError:
    return "requests is not installed. Install it with: pip install requests"

  try:
    response = requests.get(url, timeout=15, headers={
      "User-Agent": "Mozilla/5.0 (compatible; ResearchCrew/1.0)"
    })
    response.raise_for_status()
  except Exception as e:
    return f"Error fetching {url}: {e}"

  try:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
      tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
  except ImportError:
    # Fallback: basic tag stripping
    import re

    text = re.sub(r"<[^>]+>", " ", response.text)
    text = re.sub(r"\s+", " ", text).strip()

  if len(text) > 5000:
    text = text[:5000] + "\n\n[Content truncated at 5000 characters]"
  return text
