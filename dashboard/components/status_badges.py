"""Severity badges/colour classes. EMO moved from pages.py; SEVERITY_CLASS is the mapping that was inlined in kpi_html."""
EMO = {"HIGH": "🔴", "MEDIUM": "🟡", "NORMAL": "🟢", "LOW": "🟢"}
SEVERITY_CLASS = {"HIGH": "critical", "MEDIUM": "warning", "NORMAL": "normal"}  # KPI card border class


def badge(sv): return f"{EMO[sv]} {sv}"


def alert_class(sv): return "critical" if sv == "HIGH" else "warning"  # alert card left-border class
