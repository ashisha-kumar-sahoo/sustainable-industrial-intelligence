"""Shared severity labels and CSS classes."""

EMO = {
    "CRITICAL": "🚨",
    "HIGH": "🔴",
    "MEDIUM": "🟠",
    "LOW": "🟡",
    "NORMAL": "🟢",
    "UNKNOWN": "⚪",
}


def badge(severity: str) -> str:
    """Return an emoji and severity label with a safe fallback."""
    normalized = str(severity or "UNKNOWN").upper()
    return f"{EMO.get(normalized, EMO['UNKNOWN'])} {normalized}"


def alert_class(severity: str) -> str:
    """Return a CSS class for alert severity styling."""
    normalized = str(severity or "").upper()
    if normalized in {"CRITICAL", "HIGH"}:
        return "critical"
    if normalized == "MEDIUM":
        return "warning"
    return "normal"
