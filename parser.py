import re


def clean_error(text: str) -> str:
    """
    Normalize error text:
    - lowercase
    - remove extra spaces
    """
    text = text.lower()
    text = text.strip()
    return text


def tokenize(text: str):
    """
    Split text into tokens (words, identifiers)
    """
    tokens = re.findall(r"[a-zA-Z0-9_]+", text)
    return tokens


def extract_features(text: str):
    """
    Extract structured features from error message
    """
    features = {}

    # Detect error type keywords
    error_types = [
        "typeerror",
        "syntaxerror",
        "importerror",
        "keyerror",
        "indexerror",
        "valueerror",
        "attributeerror",
        "nameerror"
    ]

    features["error_type"] = "unknown"
    for err in error_types:
        if err in text:
            features["error_type"] = err
            break

    # Missing module/package
    match = re.search(r"no module named ['\"]?([a-zA-Z0-9_]+)['\"]?", text)
    if match:
        features["missing_module"] = match.group(1)

    # Type mismatch (e.g., 'int' and 'str')
    match = re.search(r"'([^']+)' and '([^']+)'", text)
    if match:
        features["type_1"] = match.group(1)
        features["type_2"] = match.group(2)

    # File not found
    if "no such file" in text:
        features["file_error"] = True

    # Division by zero
    if "division by zero" in text:
        features["math_error"] = "division_by_zero"

    # Key error detection
    match = re.search(r"keyerror: ['\"]?([a-zA-Z0-9_]+)['\"]?", text)
    if match:
        features["missing_key"] = match.group(1)

    # Index error
    if "index out of range" in text:
        features["index_issue"] = True

    return features


def parse_error(raw_error: str):
    """
    Full pipeline:
    raw -> cleaned -> tokens -> features
    """
    cleaned = clean_error(raw_error)
    tokens = tokenize(cleaned)
    features = extract_features(cleaned)

    return {
        "cleaned": cleaned,
        "tokens": tokens,
        "features": features
    }


# --------- TEST BLOCK ---------
if __name__ == "__main__":
    error_input = input("Enter error message: ")

    parsed = parse_error(error_input)

    print("\n--- PARSER OUTPUT ---\n")
    print("Cleaned:", parsed["cleaned"])
    print("Tokens:", parsed["tokens"])
    print("Features:", parsed["features"])
    print("\n----------------------\n")