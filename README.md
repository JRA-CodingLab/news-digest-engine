# 📰 News Digest Engine

[![CI](https://github.com/JRA-CodingLab/news-digest-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/JRA-CodingLab/news-digest-engine/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AI-powered daily news aggregation, summarization, and briefing system** with built-in LLM usage monitoring, budget tracking, and quality certification.

---

## Features

- 📡 **Multi-source RSS fetching** — BBC, CNN, Reuters, AP, NPR (configurable)
- 🤖 **AI Summarization** — Concise summaries via OpenAI GPT-4o-mini
- 📊 **Importance Ranking** — Articles ranked by a news-editor AI prompt
- 📝 **Daily Briefing** — Natural-language briefing in a news-anchor style
- 💰 **Budget Monitoring** — Track LLM costs with configurable spend limits
- 🛡️ **Quality Auditing** — Confidence thresholds and certification via llmauditor
- 🖥️ **Rich CLI** — Beautiful terminal output with panels, tables, and progress
- 🌐 **Streamlit Dashboard** — Interactive web interface with metrics

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/JRA-CodingLab/news-digest-engine.git
cd news-digest-engine
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run

**Terminal (Rich CLI):**
```bash
python cli.py
```

**Web Dashboard (Streamlit):**
```bash
streamlit run dashboard.py
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `LLMAUDITOR_BUDGET_LIMIT` | `2.00` | Maximum USD spend per session |
| `LLMAUDITOR_CONFIDENCE_THRESHOLD` | `65` | Minimum quality score (0-100) |
| `LLMAUDITOR_ALERT_MODE` | `true` | Enable auditor alerts |

## Architecture

```
RSS Feeds → feedparser → Fetch Articles
    → OpenAI GPT-4o-mini → Summarize (monitored)
    → OpenAI GPT-4o-mini → Rank (monitored)
    → OpenAI GPT-4o-mini → Briefing (monitored)
    → Rich CLI / Streamlit Dashboard → Display
    → llmauditor → Certification Report
```

## Project Structure

```
├── src/
│   ├── config.py          # Environment-based settings
│   ├── feed_reader.py     # RSS fetching & parsing
│   ├── summarizer.py      # AI article summarization
│   ├── ranker.py          # AI importance ranking
│   ├── briefing.py        # Daily briefing generation
│   ├── news_engine.py     # Main orchestrator
│   └── monitor.py         # LLM auditor wrapper
├── dashboard.py           # Streamlit web UI
├── cli.py                 # Rich terminal entry point
├── tests/                 # Unit tests
├── reports/               # Generated certification reports
└── .env.example           # Configuration template
```

## Testing

```bash
python -m pytest tests/ -v
```

## License

[MIT](LICENSE) © 2026 Juan Ruiz Alonso
