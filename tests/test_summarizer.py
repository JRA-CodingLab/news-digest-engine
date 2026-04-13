"""Tests for article summarization — mocks OpenAI and auditor calls."""

import unittest
from unittest.mock import patch, MagicMock

from src.config import EngineConfig
from src.feed_reader import Article
from src.summarizer import summarize_article, summarize_articles


def _mock_openai_response(content="Mocked summary.", prompt_tokens=50, completion_tokens=30):
    """Build a minimal OpenAI-style ChatCompletion response."""
    usage = MagicMock()
    usage.prompt_tokens = prompt_tokens
    usage.completion_tokens = completion_tokens

    message = MagicMock()
    message.content = content

    choice = MagicMock()
    choice.message = message

    response = MagicMock()
    response.choices = [choice]
    response.usage = usage
    return response


def _make_article(**overrides):
    defaults = {
        "title": "Test Article",
        "link": "https://example.com/article",
        "summary": "Original summary text.",
        "source": "Test Source",
    }
    defaults.update(overrides)
    return Article(**defaults)


class TestSummarizeArticle(unittest.TestCase):
    """Test single article summarization."""

    def setUp(self):
        self.config = EngineConfig(openai_api_key="test-key")
        self.client = MagicMock()
        self.monitor = MagicMock()
        self.monitor.track_call.return_value = MagicMock()

    def test_populates_ai_summary(self):
        self.client.chat.completions.create.return_value = _mock_openai_response(
            "AI-generated summary."
        )
        article = _make_article()
        result = summarize_article(article, self.client, self.config, self.monitor)

        self.assertEqual(result.ai_summary, "AI-generated summary.")
        self.client.chat.completions.create.assert_called_once()

    def test_calls_monitor_track(self):
        self.client.chat.completions.create.return_value = _mock_openai_response()
        article = _make_article()
        summarize_article(article, self.client, self.config, self.monitor)

        self.monitor.track_call.assert_called_once()
        call_kwargs = self.monitor.track_call.call_args
        self.assertEqual(call_kwargs.kwargs["model"], "gpt-4o-mini")
        self.assertEqual(call_kwargs.kwargs["input_tokens"], 50)
        self.assertEqual(call_kwargs.kwargs["output_tokens"], 30)

    def test_strips_whitespace(self):
        self.client.chat.completions.create.return_value = _mock_openai_response(
            "  Padded summary.  "
        )
        article = _make_article()
        result = summarize_article(article, self.client, self.config, self.monitor)
        self.assertEqual(result.ai_summary, "Padded summary.")


class TestSummarizeArticles(unittest.TestCase):
    """Test batch summarization with error handling."""

    def setUp(self):
        self.config = EngineConfig(openai_api_key="test-key")
        self.client = MagicMock()
        self.monitor = MagicMock()
        self.monitor.track_call.return_value = MagicMock()

    def test_summarizes_multiple(self):
        self.client.chat.completions.create.return_value = _mock_openai_response("Summary.")
        articles = [_make_article(title=f"Art {i}") for i in range(3)]
        results = summarize_articles(articles, self.client, self.config, self.monitor)

        self.assertEqual(len(results), 3)
        for a in results:
            self.assertEqual(a.ai_summary, "Summary.")

    def test_fallback_on_api_error(self):
        self.client.chat.completions.create.side_effect = Exception("API down")
        article = _make_article(summary="Original text")
        results = summarize_articles([article], self.client, self.config, self.monitor)

        # Should fall back to original summary
        self.assertEqual(results[0].ai_summary, "Original text")

    def test_empty_list(self):
        results = summarize_articles([], self.client, self.config, self.monitor)
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
