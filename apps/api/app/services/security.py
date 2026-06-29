from __future__ import annotations
import re
from typing import Any

REDACTION = "[REDACTED]"
_PATTERNS = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"),
    re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b(?:acct|account|routing|iban|swift|tax[_ -]?id|ssn|ein)\s*(?:number|no\.)?\s*[:=]?[\s#-]*[A-Za-z0-9-]{4,}\b", re.I),
]
_FALSE_POSITIVE_CARD = re.compile(r"\b(?:\d{4}[ -]){2,4}\d{1,4}\b")

def _mask_match(m: re.Match[str]) -> str:
    s = m.group(0)
    digits = re.sub(r"\D", "", s)
    # Avoid redacting short date/order-ish examples; cards/accounts are handled at 13+ digits.
    if len(digits) and len(digits) < 10 and not re.search(r"api|secret|token|password|account|routing|ssn", s, re.I):
        return s
    return REDACTION

def redact_text(text: str | None) -> tuple[str, bool]:
    if not text:
        return text or "", False
    out = text; changed = False
    for p in _PATTERNS:
        out, n = p.subn(_mask_match, out)
        changed = changed or n > 0
    return out, changed

def sanitize(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)[0]
    if isinstance(value, list):
        return [sanitize(v) for v in value]
    if isinstance(value, tuple):
        return tuple(sanitize(v) for v in value)
    if isinstance(value, dict):
        return {str(k): sanitize(v) for k, v in value.items()}
    return value
