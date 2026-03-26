import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedError:
    raw: str
    cleaned: str
    tokens: list[str]
    error_type: str = "unknown"
    missing_module: Optional[str] = None
    missing_key: Optional[str] = None
    type_mismatch: Optional[tuple[str, str]] = None
    math_error: Optional[str] = None
    has_file_error: bool = False
    has_index_error: bool = False
    extra: dict = field(default_factory=dict)

    def __str__(self) -> str:
        lines = [
            f"  raw          : {self.raw!r}",
            f"  cleaned      : {self.cleaned!r}",
            f"  tokens       : {self.tokens}",
            f"  error_type   : {self.error_type}",
        ]
        if self.missing_module:
            lines.append(f"  missing_mod  : {self.missing_module}")
        if self.missing_key:
            lines.append(f"  missing_key  : {self.missing_key}")
        if self.type_mismatch:
            lines.append(f"  type_mismatch: {self.type_mismatch[0]!r} vs {self.type_mismatch[1]!r}")
        if self.math_error:
            lines.append(f"  math_error   : {self.math_error}")
        if self.has_file_error:
            lines.append(f"  file_error   : True")
        if self.has_index_error:
            lines.append(f"  index_error  : True")
        if self.extra:
            lines.append(f"  extra        : {self.extra}")
        return "\n".join(lines)


KNOWN_ERROR_TYPES: tuple[str, ...] = (
    "modulenotfounderror",
    "filenotfounderror",
    "zerodivisionerror",
    "recursionerror",
    "memoryerror",
    "runtimeerror",
    "stopiteration",
    "typeerror",
    "syntaxerror",
    "importerror",
    "keyerror",
    "indexerror",
    "valueerror",
    "attributeerror",
    "nameerror",
    "oserror",
    "ioerror",
)


def clean_error(text: str) -> str:
    """Lowercase, collapse whitespace, and strip the raw error string."""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> list[str]:
    """Return alphanumeric/underscore tokens from *text*."""
    return re.findall(r"[a-zA-Z0-9_]+", text)


def _detect_error_type(text: str, result: ParsedError) -> None:
    for err in KNOWN_ERROR_TYPES:
        if err in text:
            result.error_type = err
            return


def _detect_missing_module(text: str, result: ParsedError) -> None:
    m = re.search(r"no module named ['\"]?([a-zA-Z0-9_.]+)['\"]?", text)
    if m:
        result.missing_module = m.group(1)


def _detect_missing_key(text: str, result: ParsedError) -> None:
    m = re.search(r"keyerror:\s*['\"]?([a-zA-Z0-9_]+)['\"]?", text)
    if m:
        result.missing_key = m.group(1)


def _detect_type_mismatch(text: str, result: ParsedError) -> None:
    m = re.search(r"'([^']+)'\s+and\s+'([^']+)'", text)
    if m:
        result.type_mismatch = (m.group(1), m.group(2))


def _detect_math_errors(text: str, result: ParsedError) -> None:
    if "division by zero" in text or "zerodivisionerror" in text:
        result.math_error = "division_by_zero"


def _detect_file_error(text: str, result: ParsedError) -> None:
    if "no such file" in text or "filenotfounderror" in text:
        result.has_file_error = True


def _detect_index_error(text: str, result: ParsedError) -> None:
    if "index out of range" in text:
        result.has_index_error = True


_EXTRACTORS = (
    _detect_error_type,
    _detect_missing_module,
    _detect_missing_key,
    _detect_type_mismatch,
    _detect_math_errors,
    _detect_file_error,
    _detect_index_error,
)


def parse_error(raw_error: str) -> ParsedError:
    """
    Full pipeline: raw → cleaned → tokens → structured ParsedError.

    >>> r = parse_error("ModuleNotFoundError: No module named 'pandas'")
    >>> r.error_type
    'modulenotfounderror'
    >>> r.missing_module
    'pandas'
    """
    if not isinstance(raw_error, str):
        raise TypeError(f"raw_error must be str, got {type(raw_error).__name__!r}")

    cleaned = clean_error(raw_error)
    tokens = tokenize(cleaned)
    result = ParsedError(raw=raw_error, cleaned=cleaned, tokens=tokens)

    for extractor in _EXTRACTORS:
        extractor(cleaned, result)

    return result


def _main() -> None:
    raw = input("Enter error message: ").strip()
    if not raw:
        print("No input provided.")
        return

    result = parse_error(raw)
    print("\n--- PARSER OUTPUT ---\n")
    print(result)
    print("\n---------------------\n")


if __name__ == "__main__":
    _main()