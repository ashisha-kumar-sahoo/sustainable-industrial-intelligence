"""Equipment monitoring tab inside the Operations page."""

from components.domain_panel import domain


def equipment(dark: bool) -> None:
    domain("equipment", dark)
