# 📰 News Digest Engine

[![CI](https://github.com/JRA-CodingLab/news-digest-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/JRA-CodingLab/news-digest-engine/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deployed on Render](https://img.shields.io/badge/deployed-Render-46E3B7.svg)](https://news-digest-engine.onrender.com/docs)

**AI-powered daily news aggregation, summarization, and briefing system** with built-in LLM usage monitoring, budget tracking, and quality certification.

## 🚀 Live Demo

**API is deployed and publicly accessible:**

- 🔗 **Swagger UI:** [news-digest-engine.onrender.com/docs](https://news-digest-engine.onrender.com/docs)
- 📊 **Dashboard:** [news-digest-engine.onrender.com/dashboard](https://news-digest-engine.onrender.com/dashboard)

**Try it now:**
```bash
curl https://news-digest-engine.onrender.com/digest
```

**Deployment Stack:** Docker + Render (free tier) + GitHub CI/CD auto-deploy

---

## Features

- 📡 **Multi-source RSS fetching** — 8 configurable news sources
- 🤖 **AI Summarization** — Concise summaries via OpenAI GPT-4o-mini
- 📊 **Importance Ranking** — Articles ranked by relevance score
- 📝 **Daily Digest** — Date-filtered news briefings
- 💰 **Budget Monitoring** — Track LLM costs with configurable limits
- 🚨 **Quality Auditing** — Confidence thresholds and certification
- 🌐 **Web Dashboard** — Visual news feed with sentiment indicators

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/digest` | Today's top articles (or `?date=YYYY-MM-DD`) |
| `GET` | `/articles` | Paginated list with category/source filters |
| `GET` | `/articles/{id}` | Single article detail |
| `POST` | `/ingest` | Trigger RSS ingestion |
| `GET` | `/feeds` | Configured RSS feeds |
| `GET` | `/metrics` | Pipeline stats + sentiment distribution |
| `GET` | `/dashboard` | Visual news dashboard |

## Tech Stack

Python 3.10+ • FastAPI • feedparser • OpenAI • Rich CLI • Streamlit • Docker

## License

[MIT](LICENSE) © 2026 Juan Ruiz Alonso
