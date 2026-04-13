"""Article summarization using OpenAI with auditor monitoring."""

from typing import List

from openai import OpenAI

from .config import EngineConfig
from .feed_reader import Article
from .monitor import DigestMonitor

SUMMARIZE_SYSTEM_PROMPT = (
    "You are a professional news summarizer. Condense the following article "
    "into a clear, concise summary preserving the key facts."
)


def summarize_article(
    article: Article,
    client: OpenAI,
    config: EngineConfig,
    monitor: DigestMonitor,
) -> Article:
    """Summarize a single article via OpenAI and track the call with the auditor.

    Args:
        article: The article to summarize.
        client: Initialized OpenAI client.
        config: Engine configuration.
        monitor: Auditor monitor instance.

    Returns:
        The same article with its ``ai_summary`` field populated.
    """
    user_prompt = f"Title: {article.title}\nSource: {article.source}\n\n{article.summary}"

    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": SUMMARIZE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=config.summarize_max_tokens,
        temperature=config.summarize_temperature,
    )

    result_text = response.choices[0].message.content or ""
    usage = response.usage

    # Track through auditor
    monitor.track_call(
        model=config.model,
        input_tokens=usage.prompt_tokens if usage else 0,
        output_tokens=usage.completion_tokens if usage else 0,
        raw_response=result_text,
        input_text=user_prompt,
    )

    article.ai_summary = result_text.strip()
    return article


def summarize_articles(
    articles: List[Article],
    client: OpenAI,
    config: EngineConfig,
    monitor: DigestMonitor,
) -> List[Article]:
    """Summarize a batch of articles, skipping failures gracefully.

    Args:
        articles: List of articles to summarize.
        client: Initialized OpenAI client.
        config: Engine configuration.
        monitor: Auditor monitor instance.

    Returns:
        The same list of articles with ``ai_summary`` populated where possible.
    """
    for article in articles:
        try:
            summarize_article(article, client, config, monitor)
        except Exception as exc:
            print(f"[summarizer] Warning: could not summarize '{article.title}': {exc}")
            article.ai_summary = article.summary  # fallback to raw summary
    return articles
