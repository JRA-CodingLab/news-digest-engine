#!/usr/bin/env python3
"""Streamlit web dashboard for news-digest-engine."""

import streamlit as st

from src.config import EngineConfig
from src.feed_reader import fetch_all_feeds
from src.summarizer import summarize_articles
from src.ranker import rank_articles
from src.briefing import generate_briefing
from src.monitor import DigestMonitor

from openai import OpenAI


def create_sidebar(config: EngineConfig) -> EngineConfig:
    """Render sidebar controls and return updated config."""
    st.sidebar.title("⚙️ Settings")
    config.budget_limit = st.sidebar.slider(
        "Budget Limit ($)", 0.50, 10.0, config.budget_limit, step=0.25
    )
    config.confidence_threshold = st.sidebar.slider(
        "Confidence Threshold", 0, 100, config.confidence_threshold
    )
    config.model = st.sidebar.selectbox(
        "Model", ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"], index=0
    )
    return config


def main() -> None:
    """Streamlit app entry point."""
    st.set_page_config(page_title="News Digest Engine", page_icon="📰", layout="wide")
    st.title("📰 News Digest Engine")
    st.caption("AI-powered daily news aggregation, summarization & briefing")

    config = EngineConfig()
    config = create_sidebar(config)

    # Validate API key
    if not config.openai_api_key:
        st.error("⚠️ OPENAI_API_KEY not set. Add it to your `.env` file.")
        st.stop()

    client = OpenAI(api_key=config.openai_api_key)
    monitor = DigestMonitor(
        budget_limit=config.budget_limit,
        confidence_threshold=config.confidence_threshold,
        alert_mode=config.alert_mode,
    )

    if st.button("🚀 Run News Digest", type="primary"):
        monitor.begin_session(config.app_name, config.app_version)

        # --- Fetch ---
        with st.spinner("📡 Fetching RSS feeds..."):
            articles = fetch_all_feeds(config)
        st.success(f"Retrieved {len(articles)} articles from {len(config.feeds)} sources")

        # --- Summarize ---
        with st.spinner("🤖 Summarizing articles..."):
            articles = summarize_articles(articles, client, config, monitor)

        # --- Rank ---
        with st.spinner("📊 Ranking articles..."):
            articles = rank_articles(articles, client, config, monitor)

        # --- Brief ---
        with st.spinner("📝 Generating briefing..."):
            briefing = generate_briefing(articles, client, config, monitor)

        # --- Display briefing ---
        st.header("📝 Daily Briefing")
        st.markdown(briefing)
        st.divider()

        # --- Articles table ---
        st.header("📋 Top Articles")
        for article in articles[:10]:
            with st.expander(
                f"#{article.rank_score or '-'} [{article.source}] {article.title}"
            ):
                st.write(article.ai_summary or article.summary)
                st.markdown(f"[Read full article]({article.link})")

        st.divider()

        # --- Budget metrics ---
        st.header("💰 Auditor Metrics")
        budget = monitor.get_budget_status()
        col1, col2, col3 = st.columns(3)
        col1.metric("Budget Limit", f"${budget.get('budget_limit', 0):.2f}")
        col2.metric("Cost So Far", f"${budget.get('cumulative_cost', 0):.4f}")
        col3.metric("API Calls", budget.get("executions", 0))

        # --- Certification ---
        report_path = monitor.end_session("reports")
        if report_path:
            st.success(f"✅ Certification report exported to `{report_path}/`")

    # Footer
    st.sidebar.divider()
    st.sidebar.info("Built with ❤️ by Juan Ruiz Alonso")


if __name__ == "__main__":
    main()
