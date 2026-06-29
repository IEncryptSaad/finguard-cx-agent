import re
from app.services.guardrails import GuardrailDecision
from app.services.security import redact_text
CREDENTIAL_PLACEHOLDER = "[REDACTED_CREDENTIAL]"
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
