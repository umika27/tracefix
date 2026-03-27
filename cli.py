import typer
from engine import analyze_error

app = typer.Typer()

def display_analysis(result):
    best = result["best"]

    print("\n------------------------------")
    print("TRACEFIX ANALYSIS")
    print("------------------------------\n")

    print(f"Error Type  : {best['type']}")
    print(f"Cause       : {best['cause']}")
    print(f"Fix         : {best['fix']}")
    print(f"Confidence  : {best['confidence']}%\n")

    print("Reasoning:")
    print(f"- {best['why']}")

    if result["alternatives"]:
        print("\nOther Possibilities:")
        for alt in result["alternatives"]:
            print(f"- {alt['type']} ({alt['confidence']}%)")

    print("\n------------------------------\n")


@app.command()
def tracefix(error_message: str):
    result = analyze_error(error_message)
    display_analysis(result)


@app.command()
def run(file: str):
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, file],
        capture_output=True,
        text=True
    )

    error_output = result.stderr.strip() if result.stderr else result.stdout.strip()

    if error_output:
        print("\n⚠️ Error detected while running file.\n")
        analysis = analyze_error(error_output)
        display_analysis(analysis)
    else:
        print("No errors found. Program ran successfully.")


if __name__ == "__main__":
    app()