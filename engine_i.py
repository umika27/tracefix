import re


def compute_confidence(base: int, signals: list) -> int:
    """
    base    : starting confidence for this error type (reflects how unambiguous the pattern is)
    signals : list of booleans — each True means an additional supporting signal was found
              (e.g. extracted a module name, matched two type tokens, etc.)
    Returns a score capped at 99.
    """
    bonus = sum(5 for s in signals if s)
    return min(base + bonus, 99)


def analyze_error(error_msg):
    error = error_msg.lower()
    candidates = []

    def add_candidate(type_, cause, fix, score, why):
        candidates.append({
            "type": type_,
            "cause": cause,
            "fix": fix,
            "confidence": score,
            "why": why
        })

    # --- No module named ---
    if "no module named" in error:
        match = re.search(r"no module named ['\"]?([a-zA-Z0-9_]+)['\"]?", error)
        module = match.group(1) if match else None
        module_label = f"'{module}'" if module else "unknown package"
        score = compute_confidence(base=80, signals=[
            module is not None,           # extracted the module name
            "no module named" in error,   # exact phrase match (always true here, but explicit)
        ])
        add_candidate(
            "Dependency Error",
            f"Missing Python package {module_label}",
            f"Run: pip install {module}" if module else "Run: pip install <package-name>",
            score,
            f"Detected 'no module named'" + (f" and extracted module name '{module}'" if module else ", but could not extract module name")
        )

    # --- ImportError (generic, no module named not present) ---
    if "importerror" in error and "no module named" not in error:
        has_cannot_import = "cannot import" in error
        score = compute_confidence(base=70, signals=[has_cannot_import])
        add_candidate(
            "Dependency Error",
            "Module import failed",
            "Check that the package is installed and the import statement is correct",
            score,
            "Detected 'ImportError'" + (", also found 'cannot import'" if has_cannot_import else "")
        )

    # --- SyntaxError ---
    if "syntaxerror" in error:
        line_match = re.search(r"line (\d+)", error)
        has_line = line_match is not None
        score = compute_confidence(base=80, signals=[has_line])
        line_info = f" at line {line_match.group(1)}" if has_line else ""
        add_candidate(
            "Syntax Error",
            f"Invalid syntax in code{line_info}",
            "Check for missing colons, unmatched brackets, or incorrect indentation",
            score,
            "Detected 'SyntaxError'" + (f" with line reference ({line_match.group(1)})" if has_line else ", no line number found")
        )

    # --- IndentationError ---
    if "indentationerror" in error or "unexpected indent" in error or "expected an indented block" in error:
        line_match = re.search(r"line (\d+)", error)
        has_line = line_match is not None
        score = compute_confidence(base=82, signals=[has_line])
        line_info = f" at line {line_match.group(1)}" if has_line else ""
        add_candidate(
            "Indentation Error",
            f"Incorrect indentation{line_info}",
            "Fix indentation — use consistent spaces or tabs, not both",
            score,
            "Detected 'IndentationError' or unexpected indent keyword"
        )

    # --- TypeError ---
    if "typeerror" in error or "unsupported operand type" in error or "cannot concatenate" in error:
        match = re.search(r"'([^']+)' and '([^']+)'", error)
        has_operand = "unsupported operand type" in error
        if match:
            t1, t2 = match.groups()
            score = compute_confidence(base=80, signals=[True, has_operand])
            add_candidate(
                "Type Error",
                f"Incompatible types: '{t1}' and '{t2}'",
                f"Convert values to a compatible type (e.g., int({t2}) or str({t1}))",
                score,
                f"Detected type mismatch between '{t1}' and '{t2}'" + (" via unsupported operand" if has_operand else "")
            )
        else:
            score = compute_confidence(base=70, signals=[has_operand])
            add_candidate(
                "Type Error",
                "Incompatible data types used in operation",
                "Check variable types and ensure they are compatible for the operation",
                score,
                "Detected 'TypeError' but could not extract specific type names"
            )

    # --- FileNotFoundError ---
    if "no such file" in error or "filenotfounderror" in error:
        path_match = re.search(r"['\"]([^'\"]+\.[a-zA-Z0-9]+)['\"]", error)
        has_path = path_match is not None
        score = compute_confidence(base=80, signals=[has_path])
        path_info = f" ('{path_match.group(1)}')" if has_path else ""
        add_candidate(
            "File Error",
            f"File not found or incorrect path{path_info}",
            "Verify the file path exists, check spelling and working directory",
            score,
            "Detected 'No such file'" + (f", extracted path '{path_match.group(1)}'" if has_path else "")
        )

    # --- ZeroDivisionError ---
    if "division by zero" in error or "zerodivisionerror" in error:
        score = compute_confidence(base=90, signals=[
            "division by zero" in error,
            "zerodivisionerror" in error,
        ])
        add_candidate(
            "Math Error",
            "Division by zero",
            "Ensure the denominator is not zero before dividing (e.g., add an `if divisor != 0` guard)",
            score,
            "Detected explicit 'division by zero' pattern"
        )

    # --- KeyError ---
    if "keyerror" in error:
        key_match = re.search(r"keyerror: ['\"]?([^'\"]+)['\"]?", error)
        has_key = key_match is not None
        score = compute_confidence(base=75, signals=[has_key])
        key_info = f" for key '{key_match.group(1)}'" if has_key else ""
        add_candidate(
            "Key Error",
            f"Key not found in dictionary{key_info}",
            "Use dict.get(key) or check `if key in dict` before accessing",
            score,
            "Detected 'KeyError'" + (f", extracted key '{key_match.group(1)}'" if has_key else ", no specific key extracted")
        )

    # --- IndexError ---
    if "indexerror" in error or "list index out of range" in error:
        index_match = re.search(r"index (\d+)", error)
        has_index = index_match is not None
        score = compute_confidence(base=75, signals=[
            has_index,
            "list index out of range" in error,
        ])
        index_info = f" (index {index_match.group(1)})" if has_index else ""
        add_candidate(
            "Index Error",
            f"List or sequence index out of range{index_info}",
            "Check the length of the list before indexing, or use a try/except block",
            score,
            "Detected 'IndexError'" + (f", referenced index {index_match.group(1)}" if has_index else "")
        )

    # --- AttributeError ---
    if "attributeerror" in error:
        attr_match = re.search(r"has no attribute ['\"]([^'\"]+)['\"]", error)
        has_attr = attr_match is not None
        score = compute_confidence(base=75, signals=[has_attr])
        attr_info = f" '{attr_match.group(1)}'" if has_attr else ""
        add_candidate(
            "Attribute Error",
            f"Object has no attribute{attr_info}",
            "Check the object type and verify the attribute/method name is correct",
            score,
            "Detected 'AttributeError'" + (f", missing attribute '{attr_match.group(1)}'" if has_attr else "")
        )

    # --- NameError ---
    if "nameerror" in error or "name " in error and "is not defined" in error:
        name_match = re.search(r"name ['\"]([^'\"]+)['\"] is not defined", error)
        has_name = name_match is not None
        score = compute_confidence(base=78, signals=[has_name])
        name_info = f" '{name_match.group(1)}'" if has_name else ""
        add_candidate(
            "Name Error",
            f"Variable or function{name_info} used before definition",
            "Ensure the variable is defined before use, check for typos in the name",
            score,
            "Detected 'NameError'" + (f", undefined name '{name_match.group(1)}'" if has_name else "")
        )

    # --- RecursionError ---
    if "recursionerror" in error or "maximum recursion depth" in error:
        score = compute_confidence(base=88, signals=[
            "maximum recursion depth" in error
        ])
        add_candidate(
            "Recursion Error",
            "Maximum recursion depth exceeded",
            "Add a base case to your recursive function, or consider an iterative approach",
            score,
            "Detected 'RecursionError' or maximum recursion depth message"
        )

    # --- PermissionError ---
    if "permissionerror" in error or "permission denied" in error:
        score = compute_confidence(base=82, signals=["permission denied" in error])
        add_candidate(
            "Permission Error",
            "Insufficient permissions to access file or resource",
            "Check file/folder permissions, or run with elevated privileges if appropriate",
            score,
            "Detected 'PermissionError' or 'permission denied'"
        )

    # --- MemoryError ---
    if "memoryerror" in error:
        score = compute_confidence(base=85, signals=[])
        add_candidate(
            "Memory Error",
            "Program ran out of available memory",
            "Reduce data size, use generators instead of lists, or process data in chunks",
            score,
            "Detected 'MemoryError'"
        )

    # --- Unknown fallback ---
    if not candidates:
        add_candidate(
            "Unknown Error",
            "Could not identify error from known patterns",
            "Review the full error message and traceback manually",
            30,
            "No matching pattern found in error message"
        )

    best = max(candidates, key=lambda x: x["confidence"])
    return {
        "best": best,
        "alternatives": sorted(candidates, key=lambda x: x["confidence"], reverse=True)[1:]
    }


# --------- TEST BLOCK ---------
if __name__ == "__main__":
    import sys as _sys
    # Allow running directly: python engine_i.py
    # (relative imports won't work in this mode, but the module is self-contained)
    error_input = input("Enter error message: ")
    result = analyze_error(error_input)
    best = result["best"]

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("TRACEFIX ANALYSIS")
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