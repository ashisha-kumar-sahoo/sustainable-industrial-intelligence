"""Safety monitoring tab inside the Operations page."""

from components.domain_panel import domain


def safety(dark: bool) -> None:
    domain("safety", dark)
