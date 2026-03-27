import re
from parser import parse_error
from ml_model import ml_predict
def analyze_error(error_msg):
    parsed = parse_error(error_msg)
    error = parsed.cleaned

    candidates = []
    def add_candidate(type_, cause, fix, score, why):
        candidates.append({
            "type": type_,
            "cause": cause,
            "fix": fix,
            "confidence": score,
            "why": why
        })
    if "no module named" in error:
        match = re.search(r"no module named ['\"]?([a-zA-Z0-9_]+)['\"]?", error)
        module = match.group(1) if match else "package"

        add_candidate(
            "Dependency Error",
            f"Missing Python package '{module}'",
            f"Run: pip install {module}",
            95,
            f"Detected 'no module named' and extracted '{module}'"
        )

    if "importerror" in error:
        add_candidate(
            "Dependency Error",
            "Module import failed",
            "Check installation and import statement",
            80,
            "Detected 'ImportError'"
        )
    if "syntaxerror" in error:
        add_candidate(
            "Syntax Error",
            "Invalid syntax in code",
            "Check for missing colons, brackets, or indentation",
            90,
            "Detected 'SyntaxError'"
        )
    if "typeerror" in error or "unsupported operand type" in error or "cannot concatenate" in error:        
        match = re.search(r"'([^']+)' and '([^']+)'", error)
        if match:
            t1, t2 = match.groups()
            add_candidate(
                "Type Error",
                f"Incompatible types: {t1} and {t2}",
                f"Convert values to same type (e.g., int({t2}) or str({t1}))",
                92,
                f"Detected mismatch between '{t1}' and '{t2}'"
            )
        else:
            add_candidate(
                "Type Error",
                "Incompatible data types",
                "Check variable types",
                85,
                "Detected 'TypeError'"
            )

    if "no such file" in error:
        add_candidate(
            "File Error",
            "File not found or incorrect path",
            "Verify file path and existence",
            88,
            "Detected 'No such file'"
        )

    if "division by zero" in error:
        add_candidate(
            "Math Error",
            "Division by zero",
            "Ensure denominator is not zero",
            95,
            "Detected division by zero"
        )
    if "keyerror" in error:
        add_candidate(
            "Data Error",
            "Key not found in dictionary",
            "Check if key exists before accessing",
            85,
            "Detected 'KeyError'"
        )
    if "indexerror" in error:
        add_candidate(
            "Index Error",
            "Index out of range",
            "Ensure index is within valid bounds",
            85,
            "Detected 'IndexError'"
        )
    # 🔹 ML prediction
    ml_label, ml_conf = ml_predict(parsed.cleaned)
    add_candidate(
        ml_label,
        "Predicted using machine learning",
        "Suggested fix based on learned patterns",
        int(ml_conf * 100),
        "ML model prediction"
)
    if not candidates:
        add_candidate(
            "Unknown Error",
            "Could not identify error",
            "Review full error message manually",
            50,
            "No matching pattern found"
        )
    best = max(candidates, key=lambda x: x["confidence"])

    return {
        "best": best,
        "alternatives": sorted(candidates, key=lambda x: x["confidence"], reverse=True)[1:]
    }


# --------- TEST BLOCK ---------
if __name__ == "__main__":
    error_input = input("Enter error message: ")
    result = analyze_error(error_input)

    best = result["best"]

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 TRACEFIX ANALYSIS")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    print(f"📌 Type       : {best['type']}")
    print(f"⚠️ Cause      : {best['cause']}")
    print(f"🛠️ Fix        : {best['fix']}")
    print(f"📊 Confidence : {best['confidence']}%")
    print(f"💡 Why        : {best['why']}")

    if result["alternatives"]:
        print("\n🔁 Other Possible Causes:")
        for alt in result["alternatives"]:
            print(f" - {alt['type']} ({alt['confidence']}%)")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n")