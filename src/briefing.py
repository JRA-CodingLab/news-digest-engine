"""Daily briefing generation using OpenAI with auditor monitoring."""

from typing import List

from openai import OpenAI

from .config import EngineConfig
from .feed_reader import Article
from .monitor import DigestMonitor

BRIEFING_SYSTEM_PROMPT = (
    "You are a professional news anchor. Write a concise, conversational daily "
    "briefing based on the top news stories provided. Use a warm, informative tone "
    "and highlight the most important developments."
)


def _build_briefing_prompt(articles: List[Article], top_n: int = 5) -> str:
    """Compose the prompt for briefing generation from the top-ranked articles."""
    top_articles = articles[:top_n]
    lines = []
    for idx, article in enumerate(top_articles, start=1):
        summary_text = article.ai_summary or article.summary
        lines.append(f"{idx}. [{article.source}] {article.title}\n   {summary_text}")
    return "Today's top stories:\n\n" + "\n\n".join(lines)


def generate_briefing(
    articles: List[Article],
    client: OpenAI,
    config: EngineConfig,
    monitor: DigestMonitor,
    top_n: int = 5,
) -> str:
    """Generate a natural-language daily briefing from the top ranked articles.

    Args:
        articles: Ranked articles (most important first).
        client: Initialized OpenAI client.
        config: Engine configuration.
        monitor: Auditor monitor instance.
        top_n: How many top articles to include in the briefing.

    Returns:
        The generated briefing text.
    """
    if not articles:
        return "No articles available for today's briefing."

    user_prompt = _build_briefing_prompt(articles, top_n)

    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": BRIEFING_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=config.briefing_max_tokens,
        temperature=config.briefing_temperature,
    )

    result_text = response.choices[0].message.content or ""
    usage = response.usage

    monitor.track_call(
        model=config.model,
        input_tokens=usage.prompt_tokens if usage else 0,
        output_tokens=usage.completion_tokens if usage else 0,
        raw_response=result_text,
        input_text=user_prompt,
    )

    return result_text.strip()
