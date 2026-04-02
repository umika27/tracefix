"""
runner.py — Embed TraceFix directly in code: catch exceptions and auto-analyze.

Usage: import runner at the top of your script, or run this file directly
       to see a live demo.
"""
import traceback as _tb
from engine import analyze_error
from display import display_analysis
from memory import store


def run_safely(fn):
    """
    Decorator: wrap any function so exceptions are caught and analyzed.

    Example:
        @run_safely
        def my_code():
            x = 10 + "hello"
        my_code()
    """
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            error_message = _tb.format_exc()
            print(f"\n  Error detected in '{fn.__name__}'\n")
            result = analyze_error(error_message)
            display_analysis(result, source=fn.__name__)
            store(error_message, result["best"]["type"],
                  result["best"]["confidence"], result["best"]["fix_steps"][0])
    return wrapper


# ── Demo (run this file directly to see TraceFix in action) ──────────────
if __name__ == "__main__":

    @run_safely
    def demo_type_error():
        x = 10 + "hello"

    @run_safely
    def demo_key_error():
        d = {"name": "Alice"}
        print(d["age"])

    @run_safely
    def demo_index_error():
        lst = [1, 2, 3]
        print(lst[10])

    print("=" * 60)
    print("  TraceFix Runner — live demo")
    print("=" * 60)

    demo_type_error()
    demo_key_error()
    demo_index_error()
