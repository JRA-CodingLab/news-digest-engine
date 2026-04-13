"""Tests for article ranking — mocks OpenAI and auditor calls."""

import unittest
from unittest.mock import MagicMock

from src.config import EngineConfig
from src.feed_reader import Article
from src.ranker import rank_articles, _parse_ranking, _build_rank_prompt


def _mock_openai_response(content="3, 1, 2", prompt_tokens=80, completion_tokens=10):
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


def _make_article(title="Article", source="Source", summary="Summary text."):
    return Article(
        title=title,
        link="https://example.com",
        summary=summary,
        source=source,
        ai_summary=f"AI: {summary}",
    )


class TestParseRanking(unittest.TestCase):
    """Test ranking response parsing."""

    def test_simple_comma_separated(self):
        result = _parse_ranking("3, 1, 2", 3)
        self.assertEqual(result, [3, 1, 2])

    def test_handles_newlines(self):
        result = _parse_ranking("2\n1\n3", 3)
        self.assertEqual(result, [2, 1, 3])

    def test_filters_out_of_range(self):
        result = _parse_ranking("1, 5, 2", 3)
        self.assertEqual(result, [1, 2])

    def test_removes_duplicates(self):
        result = _parse_ranking("1, 1, 2, 2, 3", 3)
        self.assertEqual(result, [1, 2, 3])

    def test_handles_trailing_dots(self):
        result = _parse_ranking("1., 2., 3.", 3)
        self.assertEqual(result, [1, 2, 3])

    def test_empty_string(self):
        result = _parse_ranking("", 3)
        self.assertEqual(result, [])

    def test_garbage_input(self):
        result = _parse_ranking("The most important articles are...", 3)
        self.assertEqual(result, [])


class TestBuildRankPrompt(unittest.TestCase):
    """Test prompt construction."""

    def test_numbered_list(self):
        articles = [
            _make_article("First", "BBC"),
            _make_article("Second", "CNN"),
        ]
        prompt = _build_rank_prompt(articles)
        self.assertIn("1.", prompt)
        self.assertIn("2.", prompt)
        self.assertIn("[BBC]", prompt)
        self.assertIn("[CNN]", prompt)


class TestRankArticles(unittest.TestCase):
    """Test full ranking pipeline with mocked OpenAI."""

    def setUp(self):
        self.config = EngineConfig(openai_api_key="test-key")
        self.client = MagicMock()
        self.monitor = MagicMock()
        self.monitor.track_call.return_value = MagicMock()

    def test_returns_ranked_order(self):
        self.client.chat.completions.create.return_value = _mock_openai_response("3, 1, 2")
        articles = [
            _make_article("First"),
            _make_article("Second"),
            _make_article("Third"),
        ]
        ranked = rank_articles(articles, self.client, self.config, self.monitor)

        self.assertEqual(len(ranked), 3)
        self.assertEqual(ranked[0].rank_score, 1)
        self.assertEqual(ranked[0].title, "Third")  # index 3 = Third
        self.assertEqual(ranked[1].title, "First")  # index 1 = First
        self.assertEqual(ranked[2].title, "Second")  # index 2 = Second

    def test_handles_partial_ranking(self):
        """LLM only ranks some articles — missing ones appended at end."""
        self.client.chat.completions.create.return_value = _mock_openai_response("2")
        articles = [_make_article("A"), _make_article("B"), _make_article("C")]
        ranked = rank_articles(articles, self.client, self.config, self.monitor)

        self.assertEqual(len(ranked), 3)
        self.assertEqual(ranked[0].title, "B")  # Only B was ranked

    def test_empty_list(self):
        ranked = rank_articles([], self.client, self.config, self.monitor)
        self.assertEqual(ranked, [])

    def test_calls_monitor(self):
        self.client.chat.completions.create.return_value = _mock_openai_response("1")
        articles = [_make_article()]
        rank_articles(articles, self.client, self.config, self.monitor)
        self.monitor.track_call.assert_called_once()


if __name__ == "__main__":
    unittest.main()
