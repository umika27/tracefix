"""
cli.py — TraceFix CLI entry point.

Commands:
  tracefix analyze "error message"   — analyze an error string
  tracefix run <file.py>             — run a Python file and catch errors
  tracefix watch <folder>            — watch a folder for new error files
  tracefix stats                     — show error memory stats
  tracefix export                    — export error log to CSV
  tracefix similar "error message"   — find similar past errors
"""
import typer
import sys
import subprocess
import traceback

from engine import analyze_error
from display import display_analysis, display_stats, c, BOLD, CYAN, GREEN, GREY, RED
from memory import store, get_stats, export_csv, find_similar

app = typer.Typer(
    name="tracefix",
    help="TraceFix — Hybrid ML + rule-based Python error analyzer.",
    add_completion=False,
)


def _run_analysis(error_text: str, beginner: bool, source: str = ""):
    result = analyze_error(error_text, beginner=beginner)
    display_analysis(result, source=source)
    best = result["best"]
    store(error_text, best["type"], best["confidence"], best["fix_steps"][0])
    return result


@app.command("analyze")
def cmd_analyze(
    error_message: str = typer.Argument(..., help="The error message to analyze"),
    beginner: bool = typer.Option(False, "--beginner", "-b", help="Show step-by-step fixes"),
):
    """Analyze a Python error message directly."""
    _run_analysis(error_message, beginner=beginner)


@app.command("run")
def cmd_run(
    file: str = typer.Argument(..., help="Python file to run"),
    beginner: bool = typer.Option(False, "--beginner", "-b", help="Step-by-step fixes"),
):
    """Run a Python file and auto-analyze any errors."""
    print(f"\n  {c('Running', BOLD)} {file} ...\n")
    result = subprocess.run(
        [sys.executable, file],
        capture_output=True,
        text=True,
    )
    stderr = result.stderr.strip()
    stdout = result.stdout.strip()
    error_output = stderr or stdout

    if result.returncode == 0 and not stderr:
        print(f"  {c('No errors — ran successfully.', GREEN)}\n")
        return

    print(f"  {c('Error detected:', BOLD, RED)}\n")
    # Print the raw traceback first
    raw = (stderr or stdout)
    for line in raw.splitlines():
        print(f"  {c(line, GREY)}")
    print()
    _run_analysis(raw, beginner=beginner, source=file)


@app.command("watch")
def cmd_watch(
    folder: str = typer.Argument(".", help="Folder to watch for error files"),
    interval: int = typer.Option(2, "--interval", "-i", help="Poll interval in seconds"),
    beginner: bool = typer.Option(False, "--beginner", "-b", help="Step-by-step fixes"),
):
    """Watch a folder for new log/error files and auto-analyze them."""
    from watcher import watch
    watch(folder, interval=interval)


@app.command("stats")
def cmd_stats():
    """Show error memory statistics."""
    stats = get_stats()
    display_stats(stats)


@app.command("export")
def cmd_export(
    output: str = typer.Option("error_log.csv", "--output", "-o", help="Output CSV path"),
):
    """Export error log to CSV for retraining."""
    export_csv(output)


@app.command("similar")
def cmd_similar(
    error_message: str = typer.Argument(..., help="Error message to find similar past errors for"),
):
    """Find similar errors from your error memory."""
    results = find_similar(error_message, top_n=5)
    print()
    if not results:
        print(f"  {c('No similar errors found in memory.', GREY)}")
        print(f"  Tip: run more analyses to build up your error history.\n")
        return
    print(f"  {c('Similar past errors', BOLD, CYAN)}\n")
    for i, r in enumerate(results, 1):
        short = r["error"][:70].replace("\n", " ")
        print(f"  {c(str(i), BOLD, CYAN)}.  {short!r}")
        print(f"      Type       : {c(r['prediction'], BOLD)}")
        print(f"      Confidence : {r['confidence']}%")
        print(f"      Fix        : {r['fix']}")
        print(f"      When       : {r['timestamp'][:19]}")
        print()


if __name__ == "__main__":
    app()
