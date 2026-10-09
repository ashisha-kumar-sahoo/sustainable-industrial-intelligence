"""Facility AI assistant integration for Member 6."""
import pandas as pd

import config
from utils import fname, post_json
from services.alert_service import alerts


def _endpoint():
    url = config.assistant_url().rstrip("/")
    if url.endswith("/api/ask"):
        return url
    return url + "/api/ask"


def _present(value):
    return value is not None and not pd.isna(value)


def _text(value):
    return "" if not _present(value) else str(value)


def _terms(row):
    terms = []
    try:
        terms.append(fname(row["facility_id"]).lower())
    except (KeyError, ValueError):
        pass
    for column in ("source", "alert_type"):
        candidate = row.get(column)
        if _present(candidate):
            terms.append(_text(candidate).lower())
    return terms


def _evidence(row):
    actual, expected = row.get("evidence_actual"), row.get("evidence_expected")
    if _present(actual) or _present(expected):
        return f"Actual {_text(actual)} vs expected {_text(expected)}"
    value, threshold = row.get("value"), row.get("threshold")
    if _present(value) or _present(threshold):
        return f"Reading {_text(value)} vs threshold {_text(threshold)}"
    deviation = row.get("deviation_pct")
    if _present(deviation):
        return f"Deviation {_text(deviation)}% from baseline"
    return ""


def ask(q):
    """Send the question to Member 6; retain a clearly labelled fallback."""
    try:
        return post_json(_endpoint(), {"question": q})
    except Exception:
        a = alerts()
        query = q.lower()
        hit = a[a.apply(
            lambda r: any(w in query for w in _terms(r)),
            axis=1,
        )] if len(a) else a
        if hit.empty:
            return dict(
                answer="Member 6 assistant service is unavailable. Start the AI assistant service on port 8000.",
                evidence="",
                sample=True,
                connected=False,
            )
        t = hit.iloc[0]
        insight = _text(t.get("insight_text"))
        action = _text(t.get("recommendation"))
        answer = " ".join(
            part for part in (insight, f"Suggested action: {action}" if action else "") if part
        )
        return dict(
            answer=answer or "An active operational alert was found, but no summary text is available.",
            evidence=_evidence(t),
            sample=True,
            connected=False,
        )
