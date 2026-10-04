"""Facility AI assistant (Member 6 service). Moved unchanged from data_service.ask.
POSTs to ASSISTANT_URL when set; otherwise returns the clearly-labelled sample keyword answer built from the alerts."""
import config
from utils import fname, post_json
from services.alert_service import alerts


def ask(q):
    """Member 6 assistant. POST ASSISTANT_URL {question} -> {answer, evidence}. Fallback = sample keyword answer (clearly labelled)."""
    if config.assistant_url(): return post_json(config.assistant_url(), {"question": q})
    a = alerts(); hit = a[a.apply(lambda r: any(w in q.lower() for w in (fname(r["facility_id"]).lower(), r["source"])), axis=1)] if len(a) else a
    if hit.empty: return dict(answer="No matching alert found in the sample data.", evidence="", sample=True)
    t = hit.iloc[0]; return dict(answer=t["insight_text"] + " Suggested action: " + t["recommendation"], evidence=f"Actual {t['evidence_actual']} vs expected {t['evidence_expected']}", sample=True)
