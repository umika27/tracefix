"""
tracefix/hook.py

This module replaces sys.excepthook so that any unhandled exception
automatically gets analyzed by tracefix. It is loaded silently on
every Python startup once tracefix is installed.
"""

import sys
import traceback as _traceback


def _tracefix_excepthook(exc_type, exc_value, exc_tb):
    # Format the full traceback into a single string, same as what you'd see in the terminal
    error_lines = _traceback.format_exception(exc_type, exc_value, exc_tb)
    error_message = "".join(error_lines)

    # Print the original traceback first so the user still sees it
    sys.stderr.write(error_message)

    # Now run tracefix analysis on top of it
    try:
        from .engine_i import analyze_error
    except ImportError:
        # If engine can't be imported for any reason, fail silently —
        # we never want the hook itself to crash the user's program output
        return

    result = analyze_error(error_message)
    best = result["best"]

    sys.stderr.write("\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    sys.stderr.write(" TRACEFIX AUTO-ANALYSIS\n")
    sys.stderr.write("━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
    sys.stderr.write(f" Type       : {best['type']}\n")
    sys.stderr.write(f" Cause      : {best['cause']}\n")
    sys.stderr.write(f" Fix        : {best['fix']}\n")
    sys.stderr.write(f" Confidence : {best['confidence']}%\n")
    sys.stderr.write(f" Why        : {best['why']}\n")

    if result["alternatives"]:
        sys.stderr.write("\n🔁 Other Possible Causes:\n")
        for alt in result["alternatives"]:
            sys.stderr.write(f"  - {alt['type']} ({alt['confidence']}%)\n")

    sys.stderr.write("\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")


def activate():
    """Replace sys.excepthook with tracefix's hook."""
    sys.excepthook = _tracefix_excepthook