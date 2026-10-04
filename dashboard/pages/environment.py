"""Environment page. Moved from pages.environment."""
from components.domain_panel import domain
from components.header import page_header


def environment(dark): page_header("🌿 Environment"); domain("environment", dark)
