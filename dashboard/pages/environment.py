"""Environment monitoring page."""

from components.domain_panel import domain
from components.header import page_header


def environment(dark: bool) -> None:
    page_header("🌿 Environment")
    domain("environment", dark)
