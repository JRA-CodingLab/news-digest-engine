"""Article ranking by importance using OpenAI with auditor monitoring."""

from typing import List

from openai import OpenAI

from .config import EngineConfig
from .feed_reader import Article
from .monitor import DigestMonitor

RANK_SYSTEM_PROMPT = (
    "You are a seasoned news editor. Given a numbered list of article titles and "
    "summaries, return ONLY a comma-separated list of the article numbers ordered "
    "from most important to least important. No explanations."
)


def _build_rank_prompt(articles: List[Article]) -> str:
    """Build the numbered article list for the ranking prompt."""
    lines = []
    for idx, article in enumerate(articles, start=1):
        summary_text = article.ai_summary or article.summary
        lines.append(f"{idx}. [{article.source}] {article.title}: {summary_text[:120]}")
    return "\n".join(lines)


def _parse_ranking(raw: str, total: int) -> List[int]:
    """Parse the comma-separated ranking response into a list of 1-based indices.

    Handles messy LLM output by filtering to valid indices only.
    """
    ranking: List[int] = []
    for token in raw.replace("\n", ",").split(","):
        token = token.strip().rstrip(".")
        if token.isdigit():
            num = int(token)
            if 1 <= num <= total and num not in ranking:
                ranking.append(num)
    return ranking


def rank_articles(
    articles: List[Article],
    client: OpenAI,
    config: EngineConfig,
    monitor: DigestMonitor,
) -> List[Article]:
    """Rank articles by importance using OpenAI and return them in ranked order.

    Each article's ``rank_score`` is set to its position (1 = most important).

    Args:
        articles: Summarized articles to rank.
        client: Initialized OpenAI client.
        config: Engine configuration.
        monitor: Auditor monitor instance.

    Returns:
        Articles sorted from most to least important.
    """
    if not articles:
        return articles

    user_prompt = _build_rank_prompt(articles)

    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": RANK_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=config.rank_max_tokens,
        temperature=config.rank_temperature,
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

    ranking = _parse_ranking(result_text, len(articles))

    # Assign rank scores and reorder
    ranked: List[Article] = []
    for position, idx in enumerate(ranking, start=1):
        article = articles[idx - 1]
        article.rank_score = position
        ranked.append(article)

    # Append any articles the LLM missed at the end
    seen = set(ranking)
    for idx, article in enumerate(articles, start=1):
        if idx not in seen:
            article.rank_score = len(ranked) + 1
            ranked.append(article)

    return ranked
