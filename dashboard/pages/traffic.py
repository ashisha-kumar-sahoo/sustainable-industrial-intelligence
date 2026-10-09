"""Traffic monitoring tab inside the Operations page."""

from components.domain_panel import domain


def traffic(dark: bool) -> None:
    domain("traffic", dark)
