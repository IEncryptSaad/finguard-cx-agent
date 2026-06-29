BLOCKED = ("wire all my money", "bypass kyc", "ignore compliance")
HANDOFF = ("fraud", "lawsuit", "suicide", "chargeback", "dispute", "stolen")
class GuardrailDecision:
    def __init__(self, allowed: bool, handoff_required: bool, reason: str = ""):
        self.allowed = allowed; self.handoff_required = handoff_required; self.reason = reason
def evaluate_message(message: str) -> GuardrailDecision:
    lower = message.lower()
    if any(term in lower for term in BLOCKED):
        return GuardrailDecision(False, True, "Request requires compliance review.")
    return GuardrailDecision(True, any(term in lower for term in HANDOFF), "")
