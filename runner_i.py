import traceback
from .engine_i import analyze_error


def run_user_code():
    # Example code with error — swap this out with whatever you want to test
    x = 10 + "hello"  # TypeError


if __name__ == "__main__":
    try:
        run_user_code()
    except Exception as e:
        error_message = traceback.format_exc()

        print("\n⚠️  ERROR DETECTED AUTOMATICALLY\n")

        result = analyze_error(error_message)
        best = result["best"]

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("TRACEFIX AUTO ANALYSIS")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        print(f" Type       : {best['type']}")
        print(f" Cause      : {best['cause']}")
        print(f" Fix        : {best['fix']}")
        print(f" Confidence : {best['confidence']}%")
        print(f" Why        : {best['why']}")

        if result["alternatives"]:
            print("\n🔁 Other Possible Causes:")
            for alt in result["alternatives"]:
                print(f"  - {alt['type']} ({alt['confidence']}%)")

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n")