import re
from app.services.guardrails import GuardrailDecision
CREDENTIAL_PLACEHOLDER = "[REDACTED_CREDENTIAL]"
_CREDENTIAL_PATTERNS = [
    re.compile(r"\b(password|passcode|pin|api[_ -]?key|secret|token)\b\s*[:=]?\s*\S+", re.IGNORECASE),
]

def redact_credentials(message: str) -> tuple[str, bool]:
    redacted = message
    changed = False
    for pattern in _CREDENTIAL_PATTERNS:
        redacted, count = pattern.subn(lambda m: f"{m.group(1)} {CREDENTIAL_PLACEHOLDER}", redacted)
        changed = changed or count > 0
    return redacted, changed

class PolicyEngine:
    def evaluate(self, message: str, decision: GuardrailDecision) -> GuardrailDecision:
        if "password" in message.lower() and "reset" not in message.lower():
            return GuardrailDecision(False, True, "Credential handling requires secure workflow.")
        return decision
policy_engine = PolicyEngine()
