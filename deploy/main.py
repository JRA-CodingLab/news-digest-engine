"""
News Digest Engine - Mock LLM Pipeline API
Author: Juan Ruiz Alonso
Standalone FastAPI service with pre-generated tech/AI news articles.
No external API calls - fully self-contained for CV showcase.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="News Digest Engine", description="AI-powered news aggregation pipeline. Mock deployment for CV showcase.", version="1.0.0", docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

_BASE = datetime(2026, 4, 13, 12, 0, 0)
_RAW = [
("OpenAI Launches GPT-5 with Real-Time Reasoning","TechCrunch","AI & ML","positive",0.97,"OpenAI has unveiled GPT-5, featuring real-time chain-of-thought reasoning and multimodal understanding."),
("Google Cloud Cuts Pricing on GPU Instances by 30%","ZDNet","Cloud","positive",0.88,"Google Cloud announced a 30% price reduction on A100 and H100 GPU instances for ML training."),
("Critical Log4j-Style Vulnerability Found in urllib3","Ars Technica","Security","negative",0.95,"Security researchers disclosed a critical RCE vulnerability in urllib3 affecting millions of Python apps."),
("Rust 2.0 Released with Async-First Design","Hacker News","Dev Tools","positive",0.82,"Rust reaches version 2.0 with native async/await as a first-class citizen and improved compile times."),
("Meta Open-Sources Llama 4 with 400B Parameters","VentureBeat","Open Source","positive",0.94,"Meta releases Llama 4 under Apache 2.0 license. Early benchmarks show it competing with proprietary models."),
("Anthropic Raises $5B at $60B Valuation","TechCrunch","Startups","positive",0.85,"Claude-maker Anthropic closed a $5B funding round led by Google and Spark Capital."),
("Apple Silicon M5 Ultra Benchmarks Leak","The Verge","Hardware","neutral",0.76,"Leaked benchmarks suggest M5 Ultra achieves 2.3x the neural engine throughput of M4 Ultra."),
("AWS Introduces Serverless Vector Database","ZDNet","Cloud","positive",0.89,"AWS launched a fully serverless vector database service integrated with Bedrock for RAG apps."),
("GitHub Copilot Gets Agent Mode","Ars Technica","Dev Tools","positive",0.91,"GitHub Copilot's new agent mode can edit multiple files and run terminal commands autonomously."),
("European AI Act Enforcement Begins","MIT Technology Review","AI & ML","negative",0.87,"The EU AI Act enforcement started with three companies receiving fines for high-risk AI systems."),
("Kubernetes 1.34 Simplifies Service Mesh","Hacker News","Dev Tools","positive",0.73,"K8s 1.34 introduces native service mesh primitives, reducing the need for Istio."),
("Cloudflare Reports 45% Increase in DDoS","Wired","Security","negative",0.84,"Cloudflare's quarterly report shows 45% YoY increase in DDoS attacks with AI botnets."),
("Stripe Launches AI Fraud Detection","VentureBeat","Startups","positive",0.79,"Stripe introduced a free AI fraud detection tier for startups under $1M annually."),
("NVIDIA H200 on Azure Spot Instances","ZDNet","Cloud","positive",0.86,"Azure now offers H200 GPUs as spot instances at up to 70% discount."),
("PostgreSQL 18 Adds JSON Schema Validation","Hacker News","Dev Tools","positive",0.74,"PostgreSQL 18 introduces built-in JSON Schema validation with partial indexing support."),
("Deepfake Detection Accuracy Drops to 62%","MIT Technology Review","AI & ML","negative",0.92,"Stanford study reveals deepfake detectors now achieve only 62% accuracy on latest models."),
("Docker Desktop Goes Free for Individuals","The Verge","Open Source","positive",0.81,"Docker reversed its licensing, making Desktop free for individual developers."),
("Samsung 12nm GAA for Edge AI","Wired","Hardware","neutral",0.71,"Samsung demonstrated 12nm Gate-All-Around process for edge AI inference with 40% lower power."),
("Vercel Open-Sources Full Monorepo Stack","TechCrunch","Open Source","positive",0.78,"Vercel open-sourced Turbopack and Turborepo under MIT license."),
("Chrome V8 Zero-Day Exploited in Wild","Ars Technica","Security","negative",0.96,"Google confirmed an actively exploited zero-day in Chrome's V8 engine. Emergency patches released."),
("Mistral Releases Codestral-2","VentureBeat","AI & ML","positive",0.90,"Mistral launched Codestral-2 with 128K context for code, outperforming GPT-4 on multi-file tasks."),
("Reddit Publishes Recommendation Algorithm","Hacker News","AI & ML","neutral",0.68,"Reddit's ML team published their hybrid recommendation system combining collaborative filtering and GNNs."),
("Fly.io Raises $100M","TechCrunch","Startups","positive",0.77,"Edge computing platform Fly.io raised $100M Series C to challenge AWS Lambda."),
("Linux Kernel 6.12 Drops 32-bit x86","Ars Technica","Open Source","neutral",0.65,"Linux 6.12 removes 32-bit x86 support, citing minimal usage."),
("Tesla Optimus Uses GPT Planning","Wired","AI & ML","positive",0.83,"Tesla's Optimus robots now use GPT-based task planning for household chores."),
("Datadog Adds AI Root Cause Analysis","ZDNet","Dev Tools","positive",0.75,"Datadog launched an AI assistant for automatic root cause analysis of incidents."),
("Palo Alto Acquires Orca for $2B","TechCrunch","Security","neutral",0.72,"Palo Alto Networks acquired Orca Security for $2B, consolidating CNAPP market."),
("OpenSSF Releases SLSA v2.0","Hacker News","Security","positive",0.80,"SLSA v2.0 framework released for software supply chain security. GitHub Actions supports it natively."),
("Hugging Face Hits 1M Public Models","MIT Technology Review","Open Source","positive",0.88,"Hugging Face now hosts over 1 million public ML models, becoming the de facto AI hub."),
("Intel Gaudi 3 Matches H100 on Inference","The Verge","Hardware","positive",0.79,"Intel Gaudi 3 shows competitive inference vs H100 at 40% lower cost."),
]

class Article(BaseModel):
    id: str; title: str; source: str; category: str; sentiment: str; relevance_score: float; summary: str; published_at: str; ingested_at: str

class DigestResponse(BaseModel):
    date: str; article_count: int; articles: list[Article]; categories: dict[str, int]; top_sources: list[str]

class ServiceInfo(BaseModel):
    service: str = "News Digest Engine"; author: str = "Juan Ruiz Alonso"; version: str = "1.0.0"; status: str = "healthy"
    description: str = "AI-powered news aggregation with LLM summarization and relevance ranking."
    mode: str = "mock_demo"; endpoints: list[str] = ["/digest","/articles","/ingest","/feeds","/metrics","/dashboard"]; docs: str = "/docs"

class FeedInfo(BaseModel):
    name: str; url: str; category: str; active: bool = True

class HealthResponse(BaseModel):
    status: str = "healthy"; articles_indexed: int; last_ingestion: str; version: str = "1.0.0"

_articles: list[dict] = []
for i, (t, s, c, se, sc, su) in enumerate(_RAW):
    d = i % 7; h = (i*3) % 24; pub = _BASE - timedelta(days=d, hours=h)
    _articles.append({"id": f"art_{i+1:03d}", "title": t, "source": s, "category": c, "sentiment": se, "relevance_score": sc, "summary": su, "published_at": pub.isoformat()+"Z", "ingested_at": (pub+timedelta(minutes=15)).isoformat()+"Z"})

_m = {"ingest_calls": 0, "digest_calls": 0, "served": 0}

@app.get("/", response_model=ServiceInfo, tags=["Health"])
async def root(): return ServiceInfo()

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health(): return HealthResponse(articles_indexed=len(_articles), last_ingestion=_articles[-1]["ingested_at"] if _articles else "never")

@app.get("/digest", tags=["Digest"])
async def digest(date: Optional[str] = Query(None)):
    _m["digest_calls"] += 1
    target = datetime.strptime(date, "%Y-%m-%d").date() if date else _BASE.date()
    arts = sorted([a for a in _articles if datetime.fromisoformat(a["published_at"].replace("Z","")).date() == target], key=lambda x: x["relevance_score"], reverse=True)
    _m["served"] += len(arts)
    cats = {}; srcs = set()
    for a in arts: cats[a["category"]] = cats.get(a["category"],0)+1; srcs.add(a["source"])
    return DigestResponse(date=str(target), article_count=len(arts), articles=[Article(**a) for a in arts], categories=cats, top_sources=sorted(srcs))

@app.get("/articles", tags=["Articles"])
async def list_articles(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), category: Optional[str] = None):
    f = [a for a in _articles if not category or a["category"].lower() == category.lower()]
    return {"total": len(f), "skip": skip, "limit": limit, "articles": [Article(**a) for a in f[skip:skip+limit]]}

@app.get("/articles/{article_id}", tags=["Articles"])
async def get_article(article_id: str):
    for a in _articles:
        if a["id"] == article_id: return Article(**a)
    raise HTTPException(404, f"Article '{article_id}' not found.")

@app.post("/ingest", tags=["Pipeline"])
async def ingest():
    _m["ingest_calls"] += 1
    nid = f"art_{len(_articles)+1:03d}"
    na = {"id": nid, "title": f"Breaking: AI Development #{len(_articles)+1}", "source": "TechCrunch", "category": "AI & ML", "sentiment": "positive", "relevance_score": round(0.7+(len(_articles)%3)*0.1, 2), "summary": f"New development #{len(_articles)+1} demonstrating continuous ingestion.", "published_at": datetime.utcnow().isoformat()+"Z", "ingested_at": datetime.utcnow().isoformat()+"Z"}
    _articles.append(na)
    return {"message": "Ingestion completed.", "new_articles": 1, "total_articles": len(_articles), "article": Article(**na)}

@app.get("/feeds", tags=["Pipeline"])
async def feeds():
    fs = [FeedInfo(name="TechCrunch AI",url="https://techcrunch.com/feed/",category="AI & ML"),FeedInfo(name="Ars Technica",url="https://feeds.arstechnica.com/arstechnica/technology-lab",category="Dev Tools"),FeedInfo(name="The Verge",url="https://www.theverge.com/rss/index.xml",category="Hardware"),FeedInfo(name="Hacker News",url="https://hnrss.org/best",category="Open Source"),FeedInfo(name="Wired",url="https://www.wired.com/feed/rss",category="Security"),FeedInfo(name="MIT Tech Review",url="https://www.technologyreview.com/feed/",category="AI & ML"),FeedInfo(name="VentureBeat",url="https://venturebeat.com/feed/",category="Startups"),FeedInfo(name="ZDNet",url="https://www.zdnet.com/rss.xml",category="Cloud")]
    return {"feeds": [f.dict() for f in fs], "total": len(fs), "note": "Mock - feeds are simulated."}

@app.get("/metrics", tags=["System"])
async def metrics():
    cats = {}; sents = {"positive":0,"neutral":0,"negative":0}
    for a in _articles: cats[a["category"]]=cats.get(a["category"],0)+1; sents[a["sentiment"]]+=1
    return {"pipeline": {"total_articles": len(_articles), "avg_relevance": round(sum(a["relevance_score"] for a in _articles)/max(len(_articles),1),3), "categories": cats, "sentiments": sents}, "api": _m, "feeds": 8}

@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
async def dashboard():
    cards = ""
    for a in sorted(_articles, key=lambda x: x["relevance_score"], reverse=True)[:15]:
        sc = "#4caf50" if a["sentiment"]=="positive" else ("#ff9800" if a["sentiment"]=="neutral" else "#f44336")
        cards += f"<div class='c'><div class='h'><span class='s'>{a['source']}</span><span class='t'>{a['category']}</span></div><h3>{a['title']}</h3><p>{a['summary']}</p><div class='m'><span class='sc'>Score: {a['relevance_score']}</span><span style='color:{sc}'>{a['sentiment'].upper()}</span><span>{a['published_at'][:10]}</span></div></div>"
    return f"<html><head><title>News Digest</title><style>*{{box-sizing:border-box}}body{{font-family:sans-serif;background:#0d1117;color:#c9d1d9;padding:24px}}h1{{color:#58a6ff;text-align:center}}h1 span{{color:#8b949e;font-size:.5em;display:block}}.sub{{text-align:center;color:#8b949e;margin-bottom:32px}}.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:16px;max-width:1200px;margin:0 auto}}.c{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px}}.c:hover{{border-color:#58a6ff}}.h{{display:flex;justify-content:space-between;margin-bottom:8px}}.s{{color:#58a6ff;font-weight:600;font-size:.85em}}.t{{background:#21262d;color:#8b949e;padding:2px 10px;border-radius:12px;font-size:.8em}}.c h3{{margin:8px 0;font-size:1.05em;color:#f0f6fc}}.c p{{color:#8b949e;font-size:.9em;line-height:1.5}}.m{{display:flex;justify-content:space-between;font-size:.8em;color:#8b949e;margin-top:8px}}.sc{{color:#f0883e;font-weight:600}}.st{{display:flex;justify-content:center;gap:48px;margin-bottom:32px}}.n{{text-align:center}}.n .v{{font-size:2.2em;color:#58a6ff;font-weight:700}}.n .l{{color:#8b949e;font-size:.85em}}</style></head><body><h1>News Digest Engine<span>by Juan Ruiz Alonso</span></h1><p class='sub'>AI news aggregation + LLM summarization + relevance ranking</p><div class='st'><div class='n'><div class='v'>{len(_articles)}</div><div class='l'>Articles</div></div><div class='n'><div class='v'>8</div><div class='l'>RSS Feeds</div></div><div class='n'><div class='v'>7</div><div class='l'>Categories</div></div></div><div class='g'>{cards}</div><p style='text-align:center;margin-top:32px;color:#484f58'>Open <a href='/docs' style='color:#58a6ff'>/docs</a> for interactive API testing</p></body></html>"

if __name__ == "__main__":
    import os, uvicorn
    uvicorn.run("deploy.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))