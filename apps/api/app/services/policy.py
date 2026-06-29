from app.services.guardrails import GuardrailDecision
class PolicyEngine:
    def evaluate(self, message: str, decision: GuardrailDecision) -> GuardrailDecision:
        if "password" in message.lower() and "reset" not in message.lower():
            return GuardrailDecision(False, True, "Credential handling requires secure workflow.")
        return decision
policy_engine = PolicyEngine()
