import typer
from .engine_i import analyze_error
from .checker import check_syntax
from .install import install as _install, uninstall as _uninstall, status as _status

app = typer.Typer()


def display_analysis(result):
    best = result["best"]

    print("\n------------------------------")
    print("TRACEFIX ANALYSIS")
    print("------------------------------\n")
    print(f"Error Type : {best['type']}")
    print(f"Cause      : {best['cause']}")
    print(f"Fix        : {best['fix']}")
    print(f"Confidence : {best['confidence']}%\n")
    print("Reasoning:")
    print(f"  - {best['why']}")

    if result["alternatives"]:
        print("\nOther Possibilities:")
        for alt in result["alternatives"]:
            print(f"  - {alt['type']} ({alt['confidence']}%)")

    print("\n------------------------------\n")


def display_compile_error(error):
    print("\n------------------------------")
    print("TRACEFIX COMPILE-TIME CHECK")
    print("------------------------------\n")
    print(f"Error Type : {error['type']}")
    print(f"File       : {error['file']}")
    print(f"Line       : {error['line'] if error['line'] is not None else 'N/A'}")
    print(f"Offset     : {error['offset'] if error['offset'] is not None else 'N/A'}")
    print(f"Code       : {error['text']}")
    print(f"Message    : {error['message']}")
    print("\n------------------------------\n")


@app.command()
def tracefix(error_message: str):
    """Analyze a pasted error message string."""
    result = analyze_error(error_message)
    display_analysis(result)


@app.command()
def run(file: str):
    """Run a Python file and analyze any runtime errors that occur."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, file],
        capture_output=True,
        text=True
    )

    error_output = result.stderr.strip() if result.stderr else result.stdout.strip()

    if error_output:
        print("\n⚠️  Error detected while running file.\n")
        analysis = analyze_error(error_output)
        display_analysis(analysis)
    else:
        print("\n✅ No errors found. Program ran successfully.\n")


@app.command()
def check(file: str):
    """Check a Python file for compile-time (syntax/indentation) errors without running it."""
    error = check_syntax(file)

    if not error:
        print(f"\n✅ No compile-time errors found in '{file}'.\n")
        return

    display_compile_error(error)


@app.command()
def install():
    """Install the tracefix auto-hook so it activates on every Python run (run once)."""
    _install()


@app.command()
def uninstall():
    """Remove the tracefix auto-hook from your Python environment."""
    _uninstall()


@app.command()
def status():
    """Check whether the tracefix auto-hook is currently installed."""
    _status()


if __name__ == "__main__":
    app()