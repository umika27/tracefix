import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedError:
    raw: str
    cleaned: str
    tokens: list
    error_type: str = "unknown"
    missing_module: Optional[str] = None
    missing_key: Optional[str] = None
    type_mismatch: Optional[tuple] = None
    math_error: Optional[str] = None
    has_file_error: bool = False
    has_index_error: bool = False
    extra: dict = field(default_factory=dict)

    def __str__(self):
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


KNOWN_ERROR_TYPES = (
    "modulenotfounderror", "filenotfounderror", "zerodivisionerror",
    "recursionerror", "memoryerror", "runtimeerror", "stopiteration",
    "typeerror", "syntaxerror", "importerror", "keyerror", "indexerror",
    "valueerror", "attributeerror", "nameerror", "oserror", "ioerror",
    "timeouterror", "connectionerror", "permissionerror",
)


def clean_error(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> list:
    return re.findall(r"[a-zA-Z0-9_]+", text)


def _detect_error_type(text, result):
    for err in KNOWN_ERROR_TYPES:
        if err in text:
            result.error_type = err
            return


def _detect_missing_module(text, result):
    m = re.search(r"no module named ['\"]?([a-zA-Z0-9_.]+)['\"]?", text)
    if m:
        result.missing_module = m.group(1)


def _detect_missing_key(text, result):
    m = re.search(r"keyerror:\s*['\"]?([a-zA-Z0-9_]+)['\"]?", text)
    if m:
        result.missing_key = m.group(1)


def _detect_type_mismatch(text, result):
    m = re.search(r"'([^']+)'\s+and\s+'([^']+)'", text)
    if m:
        result.type_mismatch = (m.group(1), m.group(2))


def _detect_math_errors(text, result):
    if "division by zero" in text or "zerodivisionerror" in text:
        result.math_error = "division_by_zero"


def _detect_file_error(text, result):
    if "no such file" in text or "filenotfounderror" in text:
        result.has_file_error = True


def _detect_index_error(text, result):
    if "index out of range" in text:
        result.has_index_error = True


_EXTRACTORS = (
    _detect_error_type, _detect_missing_module, _detect_missing_key,
    _detect_type_mismatch, _detect_math_errors, _detect_file_error, _detect_index_error,
)


def parse_error(raw_error: str) -> ParsedError:
    if not isinstance(raw_error, str):
        raise TypeError(f"raw_error must be str, got {type(raw_error).__name__!r}")
    cleaned = clean_error(raw_error)
    tokens = tokenize(cleaned)
    result = ParsedError(raw=raw_error, cleaned=cleaned, tokens=tokens)
    for extractor in _EXTRACTORS:
        extractor(cleaned, result)
    return result


def get_ml_text(parsed: ParsedError) -> str:
    return parsed.cleaned
