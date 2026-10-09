"""Facility AI assistant integration for Member 6."""
import config
from utils import fname, post_json
from services.alert_service import alerts


def _endpoint():
    url = config.assistant_url().rstrip("/")
    if url.endswith("/api/ask"):
        return url
    return url + "/api/ask"


def ask(q):
    """Send the question to Member 6; retain a clearly labelled fallback."""
    try:
        return post_json(_endpoint(), {"question": q})
    except Exception:
        a = alerts()
        hit = a[a.apply(
            lambda r: any(
                w in q.lower()
                for w in (fname(r["facility_id"]).lower(), str(r["source"]).lower())
            ),
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
        return dict(
            answer=t["insight_text"] + " Suggested action: " + t["recommendation"],
            evidence=f"Actual {t['evidence_actual']} vs expected {t['evidence_expected']}",
            sample=True,
            connected=False,
        )
