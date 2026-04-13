#!/usr/bin/env python3
"""Rich terminal CLI entry point for news-digest-engine."""

import sys

from rich.console import Console

from src.config import EngineConfig
from src.news_engine import NewsDigestEngine


def main() -> None:
    """Run the full news digest pipeline from the command line."""
    console = Console()
    console.print(
        "[bold magenta]"
        "╔══════════════════════════════════════╗\n"
        "║   📰  News Digest Engine  v1.0.0    ║\n"
        "╚══════════════════════════════════════╝"
        "[/bold magenta]"
    )

    try:
        config = EngineConfig()
        engine = NewsDigestEngine(config)
        result = engine.run()

        console.print(
            f"\n[dim]Processed {result['articles']} articles in "
            f"{result['elapsed_seconds']:.1f}s[/dim]"
        )
    except ValueError as exc:
        console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        sys.exit(130)
    except Exception as exc:
        console.print(f"[bold red]Fatal error:[/bold red] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
