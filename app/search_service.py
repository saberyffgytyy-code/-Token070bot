import re
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

SENSITIVE_PATTERNS = (
    "password",
    "passwd",
    "passcode",
    "private message",
    "private messages",
    "phone records",
    "phone number",
    "sms",
    "text messages",
    "ssn",
    "social security",
    "credit card",
    "bank account",
    "leaked password",
    "leak",
    "breach",
    "secret chat",
    "personal data",
)


def validate_search_query(query: str) -> str:
    if query is None:
        raise ValueError("Search query is missing.")

    cleaned = " ".join(str(query).split())
    if not cleaned:
        raise ValueError("Search query cannot be empty.")
    if len(cleaned) > 200:
        raise ValueError("Search query is too long. Please keep it under 200 characters.")
    if cleaned.startswith(("http://", "https://", "@", "/")):
        raise ValueError("Only safe text searches are allowed.")

    normalized = cleaned.lower()
    if any(pattern in normalized for pattern in SENSITIVE_PATTERNS):
        raise ValueError("This request is blocked because it could involve sensitive personal data or unauthorized private information.")

    return cleaned


def search_public_sources(query: str):
    cleaned = validate_search_query(query)
    safe_source = "duckduckgo-public"
    url = "https://html.duckduckgo.com/html/?q=" + quote_plus(cleaned)

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; secure-search-bot/1.0)"},
        timeout=20,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    items = []
    for result in soup.select("div.result")[:5]:
        link_tag = result.select_one("a.result-link")
        snippet_tag = result.select_one("a.result-snippet") or result.select_one("div.result-snippet")

        if not link_tag:
            continue

        title = link_tag.get_text(" ", strip=True)
        href = link_tag.get("href")
        snippet = snippet_tag.get_text(" ", strip=True) if snippet_tag else "No summary available."

        if href and title and href.startswith(("http://", "https://")):
            items.append({
                "title": title,
                "url": href,
                "snippet": snippet,
            })

    if not items:
        return []

    return {"source": safe_source, "items": items}
