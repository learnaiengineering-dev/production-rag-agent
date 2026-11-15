"""Turn raw feedback into something you can act on.

A thumbs-down tells you an answer was wrong. It does not tell you WHY, so you
can't fix anything from it. The fix is to capture a reason you can COUNT (an
enum, not free text) plus which part of the answer was wrong. Then the same
complaints point straight at the thing to fix."""
import csv
from collections import Counter

# the only reasons a user can pick - an enum, so you can aggregate them
REASONS = ["missing_source", "wrong_fact", "wrong_format", "outdated", "off_topic"]

# which part of your system each reason points at
FIX_AREA = {
    "missing_source": "retrieval & citations",
    "wrong_fact":     "the source data (or retrieval)",
    "wrong_format":   "output parsing / schema",
    "outdated":       "re-indexing / freshness",
    "off_topic":      "routing / retrieval",
}


def load(path):
    rows = list(csv.DictReader(open(path, newline="")))
    for r in rows:
        assert r["rating"] in ("up", "down"), f"{r['id']}: rating must be up/down"
        if r["rating"] == "down":
            assert r["reason"] in REASONS, f"{r['id']}: reason must be one of {REASONS}"
    return rows


def bare_summary(events):
    """All a thumbs-only system can tell you."""
    total = len(events)
    down = sum(1 for e in events if e["rating"] == "down")
    return {"total": total, "down": down, "down_rate": down / total}


def structured_summary(events):
    """Count the downvotes by reason, and point each at a fix."""
    downs = [e for e in events if e["rating"] == "down"]
    by_reason = Counter(e["reason"] for e in downs)
    top, top_n = by_reason.most_common(1)[0]
    return {
        "downs": len(downs),
        "by_reason": by_reason,
        "top_reason": top,
        "top_n": top_n,
        "fix_area": FIX_AREA[top],
    }


def aggregatability(events):
    """Why the reason has to be an enum: free text can't be counted.
    Compare distinct free-text strings vs enum buckets among the downvotes."""
    downs = [e for e in events if e["rating"] == "down"]
    free_text = {e["raw_reason"].strip().lower() for e in downs}
    enum_buckets = {e["reason"] for e in downs}
    return {"downs": len(downs), "distinct_free_text": len(free_text), "enum_buckets": len(enum_buckets)}
