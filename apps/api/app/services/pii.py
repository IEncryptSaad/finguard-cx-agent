import re
PATTERNS = [re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), re.compile(r"\b(?:\d[ -]*?){13,16}\b"), re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")]
def redact_pii(text: str) -> tuple[str, bool]:
    redacted = text
    changed = False
    for pattern in PATTERNS:
        redacted, count = pattern.subn("[REDACTED]", redacted)
        changed = changed or count > 0
    return redacted, changed
