from app.services.security import redact_text

def redact_pii(text: str) -> tuple[str, bool]:
    return redact_text(text)
