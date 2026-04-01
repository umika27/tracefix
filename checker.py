import ast


def check_syntax(filepath: str):
    """
    Attempts to parse the file without executing it.
    Returns a structured error dict if a compile-time error is found, else None.
    """
    try:
        with open(filepath, "r") as f:
            source = f.read()
        ast.parse(source, filename=filepath)
        return None  # No compile-time errors

    except IndentationError as e:
        return {
            "type": "IndentationError",
            "message": str(e),
            "line": e.lineno,
            "offset": e.offset,
            "text": e.text.strip() if e.text else "N/A",
            "file": filepath,
        }

    except SyntaxError as e:
        return {
            "type": "SyntaxError",
            "message": str(e),
            "line": e.lineno,
            "offset": e.offset,
            "text": e.text.strip() if e.text else "N/A",
            "file": filepath,
        }

    except FileNotFoundError:
        return {
            "type": "FileNotFoundError",
            "message": f"No such file: '{filepath}'",
            "line": None,
            "offset": None,
            "text": "N/A",
            "file": filepath,
        }

    except Exception as e:
        return {
            "type": type(e).__name__,
            "message": str(e),
            "line": None,
            "offset": None,
            "text": "N/A",
            "file": filepath,
        }