"""RSS feed fetching and article extraction from multiple news sources."""

from dataclasses import dataclass, field
from typing import List, Optional

import feedparser
from bs4 import BeautifulSoup

from .config import EngineConfig, FeedSource


@dataclass
class Article:
    """Represents a single news article parsed from an RSS feed."""
    title: str
    link: str
    summary: str
    source: str
    ai_summary: Optional[str] = None
    rank_score: Optional[int] = None


def _clean_html(raw_html: str) -> str:
    """Strip HTML tags from a string, returning plain text."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def fetch_feed(source: FeedSource) -> List[Article]:
    """Parse a single RSS feed and return a list of Article objects.

    Args:
        source: The feed source to fetch.

    Returns:
        List of articles extracted from the feed.
    """
    articles: List[Article] = []
    parsed = feedparser.parse(source.url)

    for entry in parsed.entries:
        title = entry.get("title", "Untitled")
        link = entry.get("link", "")
        raw_summary = entry.get("summary", entry.get("description", ""))
        clean_summary = _clean_html(raw_summary)

        articles.append(
            Article(
                title=title,
                link=link,
                summary=clean_summary[:500],  # cap at 500 chars
                source=source.name,
            )
        )

    return articles


def fetch_all_feeds(config: EngineConfig) -> List[Article]:
    """Fetch articles from every configured RSS feed.

    Args:
        config: Engine configuration containing feed list.

    Returns:
        Combined list of articles from all feeds.
    """
    all_articles: List[Article] = []
    for feed_source in config.feeds:
        try:
            articles = fetch_feed(feed_source)
            all_articles.extend(articles)
        except Exception as exc:
            # Log but don't crash — one bad feed shouldn't kill the pipeline
            print(f"[feed_reader] Warning: failed to fetch {feed_source.name}: {exc}")
    return all_articles
