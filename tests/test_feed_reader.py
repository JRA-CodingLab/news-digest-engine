"""Tests for RSS feed parsing — mocks feedparser to avoid network calls."""

import unittest
from unittest.mock import patch, MagicMock

from src.config import EngineConfig, FeedSource
from src.feed_reader import Article, fetch_feed, fetch_all_feeds, _clean_html


def _make_feed_response(entries):
    """Build a minimal feedparser-style response object."""
    mock = MagicMock()
    mock.entries = entries
    return mock


def _make_entry(title="Test Headline", link="https://example.com/1", summary="Some text."):
    """Build a minimal feedparser entry."""
    return {"title": title, "link": link, "summary": summary}


class TestCleanHtml(unittest.TestCase):
    """Test HTML stripping utility."""

    def test_strips_tags(self):
        self.assertEqual(_clean_html("<p>Hello <b>world</b></p>"), "Hello world")

    def test_empty_string(self):
        self.assertEqual(_clean_html(""), "")

    def test_none_input(self):
        self.assertEqual(_clean_html(None), "")

    def test_plain_text_passthrough(self):
        self.assertEqual(_clean_html("already clean"), "already clean")


class TestFetchFeed(unittest.TestCase):
    """Test single feed parsing with mocked feedparser."""

    @patch("src.feed_reader.feedparser.parse")
    def test_returns_articles(self, mock_parse):
        mock_parse.return_value = _make_feed_response([
            _make_entry("Headline A", "https://a.com", "Summary A"),
            _make_entry("Headline B", "https://b.com", "<p>Summary B</p>"),
        ])
        source = FeedSource("Test Source", "https://feeds.example.com/rss")
        articles = fetch_feed(source)

        self.assertEqual(len(articles), 2)
        self.assertIsInstance(articles[0], Article)
        self.assertEqual(articles[0].title, "Headline A")
        self.assertEqual(articles[0].source, "Test Source")
        self.assertEqual(articles[1].summary, "Summary B")  # HTML stripped

    @patch("src.feed_reader.feedparser.parse")
    def test_empty_feed(self, mock_parse):
        mock_parse.return_value = _make_feed_response([])
        source = FeedSource("Empty", "https://feeds.example.com/empty")
        articles = fetch_feed(source)
        self.assertEqual(articles, [])

    @patch("src.feed_reader.feedparser.parse")
    def test_missing_fields_use_defaults(self, mock_parse):
        mock_parse.return_value = _make_feed_response([{}])
        source = FeedSource("Sparse", "https://feeds.example.com/sparse")
        articles = fetch_feed(source)
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, "Untitled")
        self.assertEqual(articles[0].link, "")

    @patch("src.feed_reader.feedparser.parse")
    def test_summary_capped_at_500(self, mock_parse):
        long_text = "x" * 1000
        mock_parse.return_value = _make_feed_response([_make_entry(summary=long_text)])
        source = FeedSource("Long", "https://feeds.example.com/long")
        articles = fetch_feed(source)
        self.assertLessEqual(len(articles[0].summary), 500)


class TestFetchAllFeeds(unittest.TestCase):
    """Test multi-feed fetching with error resilience."""

    @patch("src.feed_reader.feedparser.parse")
    def test_aggregates_from_multiple_feeds(self, mock_parse):
        mock_parse.return_value = _make_feed_response([_make_entry()])
        config = EngineConfig(openai_api_key="test-key")
        config.feeds = [
            FeedSource("A", "https://a.com/rss"),
            FeedSource("B", "https://b.com/rss"),
        ]
        articles = fetch_all_feeds(config)
        self.assertEqual(len(articles), 2)

    @patch("src.feed_reader.feedparser.parse", side_effect=Exception("Network error"))
    def test_handles_feed_failure_gracefully(self, mock_parse):
        config = EngineConfig(openai_api_key="test-key")
        config.feeds = [FeedSource("Bad", "https://bad.com/rss")]
        articles = fetch_all_feeds(config)
        self.assertEqual(articles, [])


if __name__ == "__main__":
    unittest.main()
