import re
from parser import parse_error
from ml_model import ml_predict


def _fix_beginner(step_lines: list) -> str:
    """Format multi-step fix for beginner mode."""
    return "\n".join(f"  Step {i+1}: {s}" for i, s in enumerate(step_lines))


def analyze_error(error_msg: str, beginner: bool = False) -> dict:
    parsed = parse_error(error_msg)
    error = parsed.cleaned
    candidates = []

    def add(type_, cause, fix_steps, score, why):
        fix = _fix_beginner(fix_steps) if beginner else fix_steps[0]
        candidates.append({
            "type": type_,
            "cause": cause,
            "fix": fix,
            "fix_steps": fix_steps,
            "confidence": score,
            "why": why,
        })

    # --- Rule-based candidates ---
    if parsed.missing_module:
        mod = parsed.missing_module
        add("Dependency Error",
            f"Missing Python package '{mod}'",
            [f"Open your terminal",
             f"Run: pip install {mod}",
             f"If that fails, try: pip3 install {mod}",
             f"Re-run your script"],
            95,
            f"Matched 'no module named' pattern — extracted '{mod}'")

    if "importerror" in error and not parsed.missing_module:
        add("Dependency Error",
            "Module import failed — wrong name or not installed",
            ["Check the exact package name on pypi.org",
             "Run: pip install <package>",
             "Verify the import statement spelling"],
            80,
            "Detected 'ImportError' without a module name")

    if "syntaxerror" in error:
        add("Syntax Error",
            "Invalid Python syntax — code cannot be parsed",
            ["Look at the line number in the traceback",
             "Check for missing colons after if/for/def/class",
             "Check for unmatched brackets or quotes",
             "Fix indentation errors"],
            90,
            "Detected 'SyntaxError'")

    if "typeerror" in error or "unsupported operand type" in error or "cannot concatenate" in error:
        if parsed.type_mismatch:
            t1, t2 = parsed.type_mismatch
            add("Type Error",
                f"Incompatible types: '{t1}' and '{t2}'",
                [f"Identify which variable has type '{t2}'",
                 f"Convert it: int(x), str(x), or float(x)",
                 f"Example: result = {t1}_var + {t1}({t2}_var)"],
                92,
                f"Detected type mismatch between '{t1}' and '{t2}'")
        else:
            add("Type Error",
                "Incompatible data types used together",
                ["Print type(variable) to inspect each variable",
                 "Convert to matching types before the operation",
                 "Use int(), str(), float(), or list() to cast"],
                85,
                "Detected 'TypeError'")

    if parsed.has_file_error:
        add("File Error",
            "File not found or incorrect path",
            ["Check the file path is correct (use absolute path to be safe)",
             "Run: ls (Linux/Mac) or dir (Windows) to list files",
             "Make sure the file exists before opening it",
             "Use os.path.exists(path) to guard the open call"],
            88,
            "Detected 'No such file' pattern")

    if parsed.math_error == "division_by_zero":
        add("Math Error",
            "Attempted to divide a number by zero",
            ["Find the denominator in your division operation",
             "Add a check: if denominator != 0: before dividing",
             "Or use: result = a / b if b != 0 else 0"],
            95,
            "Detected 'division by zero'")

    if parsed.missing_key:
        key = parsed.missing_key
        add("Key Error",
            f"Key '{key}' not found in dictionary",
            [f"Check if '{key}' exists: if '{key}' in my_dict:",
             f"Use .get() safely: my_dict.get('{key}', default_value)",
             f"Print my_dict.keys() to see what keys exist"],
            88,
            f"Extracted missing key: '{key}'")
    elif "keyerror" in error:
        add("Key Error",
            "Key not found in dictionary",
            ["Use dict.get(key, default) instead of dict[key]",
             "Check dict.keys() to see available keys",
             "Guard with: if key in my_dict:"],
            85,
            "Detected 'KeyError'")

    if parsed.has_index_error:
        add("Index Error",
            "List/tuple index is out of valid range",
            ["Print len(your_list) to see its actual length",
             "Valid indices are 0 to len(list)-1",
             "Use: if index < len(my_list): before accessing",
             "Use enumerate() in loops instead of manual indexing"],
            85,
            "Detected 'index out of range' pattern")

    if "nameerror" in error:
        m = re.search(r"name '([^']+)' is not defined", error)
        name = m.group(1) if m else "variable"
        add("Name Error",
            f"Variable or function '{name}' used before it was defined",
            [f"Make sure '{name}' is defined before this line",
             f"Check for typos in the variable name",
             f"If it's a function, define it above the call site"],
            88,
            f"Detected undefined name: '{name}'")

    if "attributeerror" in error:
        add("Attribute Error",
            "Accessing a method or property that doesn't exist on this object",
            ["Print type(your_object) to confirm what type it is",
             "Use dir(your_object) to list all valid attributes",
             "Check for typos in the attribute name"],
            85,
            "Detected 'AttributeError'")

    if "recursionerror" in error:
        add("Recursion Error",
            "Function called itself too many times (infinite recursion)",
            ["Add a base case to your recursive function",
             "Ensure the base case is reachable",
             "Or rewrite using a loop instead of recursion"],
            90,
            "Detected 'RecursionError'")

    if "valueerror" in error:
        add("Value Error",
            "Correct type but invalid value (e.g. converting 'abc' to int)",
            ["Validate input before converting: if text.isdigit():",
             "Wrap in try/except ValueError to handle bad input",
             "Print the value before the failing operation"],
            82,
            "Detected 'ValueError'")

    # --- ML prediction ---
    ml_label, ml_conf = ml_predict(parsed.cleaned)
    add(
        ml_label,
        "Predicted using machine learning on error text patterns",
        ["Review the full traceback for context",
         "Search the error message on Stack Overflow",
         "Check the docs for the library involved"],
        int(ml_conf * 100),
        "ML (TF-IDF + Naive Bayes) model prediction"
    )

    if not candidates:
        add("Unknown Error",
            "Could not identify the error type",
            ["Copy the full traceback into a web search",
             "Check Stack Overflow for similar messages",
             "Add print() statements before the crash line to inspect state"],
            50,
            "No rule or ML pattern matched")

    best = max(candidates, key=lambda x: x["confidence"])
    alternatives = sorted(
        [c for c in candidates if c is not best],
        key=lambda x: x["confidence"],
        reverse=True
    )

    return {
        "best": best,
        "alternatives": alternatives,
        "parsed": parsed,
    }
