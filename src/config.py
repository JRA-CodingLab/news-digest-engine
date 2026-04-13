"""Configuration management — loads settings from environment variables."""

import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

load_dotenv()


@dataclass
class FeedSource:
    """Represents a single RSS feed source."""
    name: str
    url: str


# Default RSS feeds for news aggregation
DEFAULT_FEEDS: List[FeedSource] = [
    FeedSource("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
    FeedSource("CNN Top Stories", "http://rss.cnn.com/rss/edition.rss"),
    FeedSource("Reuters World", "https://feeds.reuters.com/reuters/worldNews"),
    FeedSource("Associated Press", "https://rsshub.app/apnews/topics/apf-topnews"),
    FeedSource("NPR World", "https://feeds.npr.org/1004/rss.xml"),
]


@dataclass
class EngineConfig:
    """Central configuration for the news digest engine."""

    # OpenAI settings
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: str = "gpt-4o-mini"

    # Auditor budget & quality settings
    budget_limit: float = field(
        default_factory=lambda: float(os.getenv("LLMAUDITOR_BUDGET_LIMIT", "2.00"))
    )
    confidence_threshold: int = field(
        default_factory=lambda: int(os.getenv("LLMAUDITOR_CONFIDENCE_THRESHOLD", "65"))
    )
    alert_mode: bool = field(
        default_factory=lambda: os.getenv("LLMAUDITOR_ALERT_MODE", "true").lower() == "true"
    )

    # Feed sources
    feeds: List[FeedSource] = field(default_factory=lambda: list(DEFAULT_FEEDS))

    # AI operation parameters
    summarize_max_tokens: int = 150
    summarize_temperature: float = 0.2
    rank_max_tokens: int = 100
    rank_temperature: float = 0.1
    briefing_max_tokens: int = 300
    briefing_temperature: float = 0.3

    # Application metadata
    app_name: str = "news-digest-engine"
    app_version: str = "1.0.0"

    def validate(self) -> None:
        """Raise ValueError if critical configuration is missing."""
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required. Set it in your .env file or environment."
            )
