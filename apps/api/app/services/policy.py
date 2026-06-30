import re
from app.services.guardrails import GuardrailDecision
from typing import Any
from app.services.security import redact_text, sanitize
CREDENTIAL_PLACEHOLDER = "[REDACTED_CREDENTIAL]"
_CREDENTIAL_KEY_PATTERN = re.compile(r"(?:password|passcode|pin|api[_ -]?key|secret|token|private[_ -]?key)", re.IGNORECASE)
_CREDENTIAL_PATTERNS = [
    re.compile(
        r"\b((?:reset\s+)?(?:password|passcode|pin)|api[_ -]?key|secret|token)\b"
        r"\s*(?:(?:is|as|to|for)\b|[:=])?\s*\S+",
        re.IGNORECASE,
    ),
]

def redact_credentials(message: str) -> tuple[str, bool]:
    redacted = message
    changed = False
    for pattern in _CREDENTIAL_PATTERNS:
        redacted, count = pattern.subn(lambda m: f"{m.group(1)} {CREDENTIAL_PLACEHOLDER}", redacted)
        changed = changed or count > 0
    if changed:
        return redacted, True
    more, more_changed = redact_text(redacted)
    return more, more_changed

class PolicyEngine:
    def evaluate(self, message: str, decision: GuardrailDecision) -> GuardrailDecision:
        if "password" in message.lower() and "reset" not in message.lower():
            return GuardrailDecision(False, True, "Credential handling requires secure workflow.")
        return decision
policy_engine = PolicyEngine()

def sanitize_sensitive(value: Any) -> Any:
    if isinstance(value, str):
        return redact_credentials(value)[0]
    if isinstance(value, list):
        return [sanitize_sensitive(v) for v in value]
    if isinstance(value, tuple):
        return tuple(sanitize_sensitive(v) for v in value)
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            skey = str(key)
            if isinstance(item, str) and _CREDENTIAL_KEY_PATTERN.search(skey):
                sanitized[skey] = CREDENTIAL_PLACEHOLDER
            else:
                sanitized[skey] = sanitize_sensitive(item)
        return sanitize(sanitized)
    return value
