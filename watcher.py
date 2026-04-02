"""
watcher.py — Watch a folder for new .log/.txt files and auto-analyze errors.
"""
import time
import os
import sys
from pathlib import Path
from engine import analyze_error
from memory import store
from display import display_analysis

WATCHED_EXTENSIONS = {".log", ".txt", ".err"}


def _extract_errors(content: str) -> list:
    """Pull error-looking lines from file content."""
    error_keywords = ["error", "exception", "traceback", "failed", "fatal"]
    lines = content.splitlines()
    chunks = []
    current = []
    for line in lines:
        low = line.lower()
        if any(k in low for k in error_keywords):
            current.append(line)
        else:
            if current:
                chunks.append(" | ".join(current))
                current = []
    if current:
        chunks.append(" | ".join(current))
    return chunks or [content[:300]]


def watch(folder: str, interval: int = 2):
    folder_path = Path(folder)
    if not folder_path.is_dir():
        print(f"[tracefix watcher] ERROR: '{folder}' is not a directory.")
        sys.exit(1)

    seen = set(folder_path.glob("**/*"))
    print(f"\n[tracefix watcher] Watching: {folder_path.resolve()}")
    print(f"[tracefix watcher] Extensions: {', '.join(WATCHED_EXTENSIONS)}")
    print(f"[tracefix watcher] Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(interval)
            current = set(folder_path.glob("**/*"))
            new_files = current - seen
            seen = current

            for f in sorted(new_files):
                if f.suffix.lower() not in WATCHED_EXTENSIONS:
                    continue
                if not f.is_file():
                    continue

                print(f"\n[tracefix watcher] New file detected: {f.name}")
                try:
                    content = f.read_text(errors="ignore").strip()
                    if not content:
                        continue
                    errors = _extract_errors(content)
                    for err_text in errors[:3]:
                        result = analyze_error(err_text)
                        display_analysis(result, source=f"watcher:{f.name}")
                        store(
                            err_text,
                            result["best"]["type"],
                            result["best"]["confidence"],
                            result["best"]["fix_steps"][0],
                        )
                except Exception as e:
                    print(f"[tracefix watcher] Could not read {f.name}: {e}")
    except KeyboardInterrupt:
        print("\n[tracefix watcher] Stopped.")
