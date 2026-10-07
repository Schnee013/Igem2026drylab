"""Deterministic single-season economic demo for test-guided nematode control."""

from .break_even import break_even_analysis
from .config import Evidence, Model, Treatment, load_density, load_model
from .economics import Result, evaluate
from .loss import relative_yield_fraction, yield_loss_fraction
from .reporting import (
    build_diagnostic_report,
    format_html_report,
    format_html_report_en,
    format_text_report,
    open_report_in_browser,
    write_diagnostic_report,
    write_english_html_report,
)

__all__ = [
    "Evidence",
    "Model",
    "Treatment",
    "Result",
    "load_model",
    "load_density",
    "relative_yield_fraction",
    "yield_loss_fraction",
    "evaluate",
    "break_even_analysis",
    "build_diagnostic_report",
    "format_text_report",
    "format_html_report",
    "format_html_report_en",
    "open_report_in_browser",
    "write_diagnostic_report",
    "write_english_html_report",
]
