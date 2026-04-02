"""
memory.py — Error log storage, retrieval, and similarity search.
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / ".tracefix" / "error_log.json"


def _load() -> list:
    if LOG_FILE.exists():
        try:
            return json.loads(LOG_FILE.read_text())
        except Exception:
            return []
    return []


def _save(entries: list):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text(json.dumps(entries, indent=2))


def store(error: str, prediction: str, confidence: int, fix: str):
    """Append one error record to the log."""
    entries = _load()
    entries.append({
        "timestamp": datetime.now().isoformat(),
        "error": error[:500],
        "prediction": prediction,
        "confidence": confidence,
        "fix": fix,
    })
    _save(entries)


def _token_overlap(a: str, b: str) -> float:
    """Simple Jaccard similarity on word tokens."""
    ta = set(re.findall(r"[a-z0-9_]+", a.lower()))
    tb = set(re.findall(r"[a-z0-9_]+", b.lower()))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def find_similar(error: str, top_n: int = 3) -> list:
    """Return the most similar past errors from the log."""
    entries = _load()
    if not entries:
        return []
    scored = []
    for entry in entries:
        score = _token_overlap(error, entry["error"])
        if score > 0.1:
            scored.append((score, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:top_n]]


def get_stats() -> dict:
    entries = _load()
    if not entries:
        return {"total": 0}
    from collections import Counter
    counts = Counter(e["prediction"] for e in entries)
    avg_conf = sum(e["confidence"] for e in entries) / len(entries)
    return {
        "total": len(entries),
        "by_type": dict(counts.most_common()),
        "avg_confidence": round(avg_conf, 1),
        "log_path": str(LOG_FILE),
    }


def export_csv(out_path: str = "error_log.csv"):
    """Export log to CSV for retraining."""
    entries = _load()
    if not entries:
        print("No entries to export.")
        return
    import csv
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp", "error", "prediction", "confidence", "fix"])
        w.writeheader()
        w.writerows(entries)
    print(f"Exported {len(entries)} entries to {out_path}")
