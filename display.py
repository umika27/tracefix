"""
display.py — All terminal output for TraceFix.
Uses only stdlib — no rich, no colorama needed (ANSI codes work on all modern terminals).
"""
import os
import sys

# ANSI colors
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
GREY   = "\033[90m"

_NO_COLOR = not sys.stdout.isatty() or os.environ.get("NO_COLOR")

def c(text, *codes):
    if _NO_COLOR:
        return text
    return "".join(codes) + text + RESET

def _bar(confidence: int) -> str:
    filled = round(confidence / 5)
    empty = 20 - filled
    col = GREEN if confidence >= 80 else YELLOW if confidence >= 50 else RED
    bar = c("█" * filled, col) + c("░" * empty, GREY)
    return f"[{bar}] {confidence}%"

def _rule(char="─", width=60):
    return c(char * width, GREY)

def _header(title: str):
    print()
    print(_rule("═"))
    print(c(f"  TRACEFIX  ", BOLD, CYAN) + c(f"  {title}", BOLD, WHITE))
    print(_rule("═"))
    print()

def display_analysis(result: dict, source: str = ""):
    best = result["best"]
    parsed = result.get("parsed")

    _header("Analysis" + (f"  ·  {source}" if source else ""))

    # Confidence bar
    print(f"  {c('Confidence', BOLD)}  {_bar(best['confidence'])}")
    print()

    # Core fields
    rows = [
        ("Type",   c(best["type"], BOLD, YELLOW)),
        ("Cause",  best["cause"]),
        ("Why",    c(best["why"], DIM)),
    ]
    for label, val in rows:
        print(f"  {c(label, BOLD):<22}{val}")
    print()

    # Fix block
    print(f"  {c('Fix', BOLD, GREEN)}")
    print(_rule("─", 60))
    for line in best["fix_steps"]:
        idx = best["fix_steps"].index(line) + 1
        print(f"  {c(str(idx), BOLD, CYAN)}.  {line}")
    print(_rule("─", 60))

    # Similar past errors
    if parsed:
        from memory import find_similar
        similar = find_similar(parsed.raw)
        if similar:
            print()
            print(f"  {c('Similar past errors', BOLD, BLUE)}")
            for s in similar[:2]:
                short = s["error"][:60].replace("\n", " ")
                print(f"  {c('↻', CYAN)}  {short!r}")
                print(f"     {c('→', GREY)} {s['prediction']} ({s['confidence']}%)")

    # Alternatives
    alts = [a for a in result.get("alternatives", []) if a["confidence"] >= 30]
    if alts:
        print()
        print(f"  {c('Other possibilities', BOLD)}")
        for alt in alts[:3]:
            print(f"  {c('·', GREY)} {alt['type']:<28} {_bar(alt['confidence'])}")

    print()
    print(_rule("═"))
    print()


def display_stats(stats: dict):
    _header("Error Memory Stats")
    if stats["total"] == 0:
        print(f"  {c('No errors logged yet.', DIM)}")
        print(f"  Run any tracefix command to start building your history.\n")
        return
    print(f"  {c('Total errors logged', BOLD):<30}{stats['total']}")
    print(f"  {c('Average confidence', BOLD):<30}{stats['avg_confidence']}%")
    print(f"  {c('Log file', BOLD):<30}{c(stats['log_path'], DIM)}")
    print()
    print(f"  {c('Breakdown by type', BOLD)}")
    print(_rule("─", 50))
    for t, count in stats["by_type"].items():
        bar_len = round(count / stats["total"] * 30)
        bar = c("█" * bar_len, CYAN)
        print(f"  {t:<28} {bar}  {count}")
    print()
    print(_rule("═"))
    print()
