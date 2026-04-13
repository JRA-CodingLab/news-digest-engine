"""Main orchestrator — fetch → summarize → rank → brief → display → certify."""

from datetime import datetime
from typing import Dict, Any, List, Optional

from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track

from .config import EngineConfig
from .feed_reader import Article, fetch_all_feeds
from .summarizer import summarize_articles
from .ranker import rank_articles
from .briefing import generate_briefing
from .monitor import DigestMonitor


class NewsDigestEngine:
    """End-to-end news digest pipeline with auditor monitoring.

    Usage::

        engine = NewsDigestEngine()
        engine.run()
    """

    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig()
        self.config.validate()

        self.client = OpenAI(api_key=self.config.openai_api_key)
        self.monitor = DigestMonitor(
            budget_limit=self.config.budget_limit,
            confidence_threshold=self.config.confidence_threshold,
            alert_mode=self.config.alert_mode,
        )
        self.console = Console()

        self.articles: List[Article] = []
        self.briefing_text: str = ""

    # ------------------------------------------------------------------
    # Pipeline stages
    # ------------------------------------------------------------------

    def fetch(self) -> List[Article]:
        """Stage 1: Fetch articles from all configured RSS feeds."""
        self.console.print("[bold cyan]📡 Fetching RSS feeds...[/bold cyan]")
        self.articles = fetch_all_feeds(self.config)
        self.console.print(
            f"  ✓ Retrieved [green]{len(self.articles)}[/green] articles "
            f"from {len(self.config.feeds)} sources"
        )
        return self.articles

    def summarize(self) -> List[Article]:
        """Stage 2: Summarize each article with OpenAI (monitored)."""
        self.console.print("[bold cyan]🤖 Summarizing articles...[/bold cyan]")
        self.articles = summarize_articles(
            self.articles, self.client, self.config, self.monitor
        )
        done = sum(1 for a in self.articles if a.ai_summary)
        self.console.print(f"  ✓ Summarized [green]{done}[/green] articles")
        return self.articles

    def rank(self) -> List[Article]:
        """Stage 3: Rank articles by importance (monitored)."""
        self.console.print("[bold cyan]📊 Ranking articles...[/bold cyan]")
        self.articles = rank_articles(
            self.articles, self.client, self.config, self.monitor
        )
        self.console.print("  ✓ Articles ranked by importance")
        return self.articles

    def brief(self) -> str:
        """Stage 4: Generate a daily briefing (monitored)."""
        self.console.print("[bold cyan]📝 Generating daily briefing...[/bold cyan]")
        self.briefing_text = generate_briefing(
            self.articles, self.client, self.config, self.monitor
        )
        self.console.print("  ✓ Briefing generated")
        return self.briefing_text

    def display(self) -> None:
        """Stage 5: Render results in the terminal with rich panels & tables."""
        # Briefing panel
        self.console.print()
        self.console.print(
            Panel(
                self.briefing_text or "No briefing available.",
                title="[bold green]📰 Daily News Briefing[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )

        # Articles table
        table = Table(title="Top Articles", show_lines=True)
        table.add_column("#", style="bold", width=4)
        table.add_column("Source", style="cyan", width=16)
        table.add_column("Title", style="white", min_width=30)
        table.add_column("Summary", style="dim", max_width=60)

        for article in self.articles[:10]:
            table.add_row(
                str(article.rank_score or "-"),
                article.source,
                article.title,
                (article.ai_summary or article.summary)[:120] + "…",
            )

        self.console.print(table)

        # Budget status
        status = self.monitor.get_budget_status()
        self.console.print()
        self.console.print(
            Panel(
                f"Budget: ${status.get('cumulative_cost', 0):.4f} / "
                f"${status.get('budget_limit', 0):.2f}  |  "
                f"Calls: {status.get('executions', 0)}",
                title="[bold yellow]💰 Auditor Budget Status[/bold yellow]",
                border_style="yellow",
            )
        )

    def certify(self, output_dir: str = "reports") -> Optional[str]:
        """Stage 6: Export auditor certification report."""
        self.console.print("[bold cyan]📋 Generating certification...[/bold cyan]")
        path = self.monitor.end_session(output_dir)
        if path:
            self.console.print(f"  ✓ Report exported to [green]{path}/[/green]")
        return path

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def run(self, output_dir: str = "reports") -> Dict[str, Any]:
        """Execute the complete news digest pipeline.

        Returns:
            Summary dict with article count, briefing, and budget status.
        """
        started = datetime.utcnow()
        self.monitor.begin_session(self.config.app_name, self.config.app_version)

        self.fetch()
        self.summarize()
        self.rank()
        briefing = self.brief()
        self.display()
        self.certify(output_dir)

        elapsed = (datetime.utcnow() - started).total_seconds()
        self.console.print(
            f"\n[bold green]✅ Pipeline complete in {elapsed:.1f}s[/bold green]"
        )

        return {
            "articles": len(self.articles),
            "briefing": briefing,
            "budget": self.monitor.get_budget_status(),
            "elapsed_seconds": elapsed,
        }
