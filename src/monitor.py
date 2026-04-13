"""LLM auditor wrapper — budget tracking, quality scoring, and certification."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from llmauditor import Auditor


@dataclass
class MonitorReport:
    """Wraps the raw auditor execution report for convenient access."""
    raw: Any
    cost: float = 0.0
    quality_score: float = 0.0
    passed: bool = True

    def display(self) -> None:
        """Print the auditor report to the terminal via its built-in display."""
        if hasattr(self.raw, "display"):
            self.raw.display()


class DigestMonitor:
    """Manages an LLM auditor instance for the news digest engine.

    Handles budget setup, guard mode, evaluation lifecycle, and per-call
    execution monitoring.
    """

    def __init__(
        self,
        budget_limit: float = 2.00,
        confidence_threshold: int = 65,
        alert_mode: bool = True,
    ):
        self.budget_limit = budget_limit
        self.confidence_threshold = confidence_threshold
        self.alert_mode = alert_mode
        self.auditor = Auditor()
        self._setup()

    def _setup(self) -> None:
        """Configure budget, guard mode, and alert settings on the auditor."""
        self.auditor.set_budget(self.budget_limit)
        self.auditor.guard_mode(self.confidence_threshold)

    def begin_session(self, app_name: str, version: str) -> None:
        """Start an evaluation session for tracking a full pipeline run."""
        self.auditor.start_evaluation(app_name, version)

    def track_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        raw_response: str,
        input_text: str,
    ) -> MonitorReport:
        """Execute a single monitored LLM call through the auditor.

        Args:
            model: Model identifier (e.g. 'gpt-4o-mini').
            input_tokens: Number of prompt tokens.
            output_tokens: Number of completion tokens.
            raw_response: The raw text returned by the LLM.
            input_text: The original prompt text.

        Returns:
            A MonitorReport wrapping the auditor's evaluation.
        """
        report = self.auditor.execute(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            raw_response=raw_response,
            input_text=input_text,
        )
        return MonitorReport(raw=report)

    def end_session(self, output_dir: str = "reports") -> Optional[str]:
        """Finish the evaluation and export certification artifacts.

        Args:
            output_dir: Directory for exported reports.

        Returns:
            Path to the exported report directory, or None on failure.
        """
        try:
            eval_report = self.auditor.end_evaluation()
            eval_report.export_all(output_dir)
            return output_dir
        except Exception as exc:
            print(f"[monitor] Warning: certification export failed: {exc}")
            return None

    def get_budget_status(self) -> Dict[str, Any]:
        """Return current budget utilization from the auditor.

        Returns:
            Dict with keys: budget_limit, cumulative_cost, executions.
        """
        return self.auditor.get_budget_status()
