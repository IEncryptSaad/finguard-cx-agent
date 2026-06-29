from datetime import datetime, timezone
from difflib import SequenceMatcher
from uuid import uuid4
from app.models.schemas import FeedbackClassification, ProductItem, ProductItemCreate
from app.services.audit import log_event
from app.services.memory import history

_ITEMS: dict[str, ProductItem] = {}
_CLASSIFICATIONS: dict[str, FeedbackClassification] = {}

BUG_TERMS = ("bug", "broken", "error", "crash", "failed", "not working")
FEATURE_TERMS = ("feature", "add", "request", "wish", "enhancement", "roadmap")
COMPLAINT_TERMS = ("angry", "complaint", "bad", "terrible", "slow", "frustrated")
PRAISE_TERMS = ("great", "thanks", "love", "excellent", "helpful")
FRAUD_TERMS = ("fraud", "stolen", "unauthorized")
DISPUTE_TERMS = ("dispute", "chargeback", "transaction")

def _now() -> str: return datetime.now(timezone.utc).isoformat()
def _contains(text: str, terms: tuple[str, ...]) -> bool: return any(t in text.lower() for t in terms)
def classify_text(text: str) -> tuple[str, float, str, str]:
    label = "General Question"; confidence = 0.55; action = "Answer with relevant knowledge and monitor follow-up."
    if _contains(text, FRAUD_TERMS): label, confidence, action = "Fraud", 0.9, "Escalate to a fraud specialist and create a high-priority ticket."
    elif _contains(text, DISPUTE_TERMS): label, confidence, action = "Dispute", 0.86, "Summarize transaction details and route to disputes workflow."
    elif _contains(text, BUG_TERMS): label, confidence, action = "Bug", 0.84, "Create a bug report linked to the conversation."
    elif _contains(text, FEATURE_TERMS): label, confidence, action = "Feature Request", 0.82, "Create or link a feature request for product review."
    elif _contains(text, COMPLAINT_TERMS): label, confidence, action = "Complaint", 0.78, "Notify the support lead and draft an empathetic reply."
    elif _contains(text, PRAISE_TERMS): label, confidence, action = "Praise", 0.76, "Record positive feedback and share with the team."
    sentiment = "positive" if label == "Praise" else "negative" if label in ("Bug", "Complaint", "Fraud", "Dispute") else "neutral"
    return label, confidence, sentiment, action

def classify_conversation(conversation_id: str) -> FeedbackClassification:
    text = "\n".join(m.content for m in history(conversation_id))
    label, confidence, sentiment, action = classify_text(text)
    summary = (text[:220] or "No transcript available").strip()
    item = FeedbackClassification(id=str(uuid4()), conversation_id=conversation_id, category=label, sentiment=sentiment, summary=summary, recommended_action=action, confidence_score=confidence, created_at=_now())
    _CLASSIFICATIONS[conversation_id] = item
    log_event("feedback.classified", {"conversation_id": conversation_id, "category": label, "confidence": confidence})
    return item

def list_classifications() -> list[FeedbackClassification]: return list(_CLASSIFICATIONS.values())
def get_classification(conversation_id: str) -> FeedbackClassification: return _CLASSIFICATIONS.get(conversation_id) or classify_conversation(conversation_id)

def _duplicate_ids(title: str, description: str) -> list[str]:
    target = f"{title} {description}".lower()
    return [i.id for i in _ITEMS.values() if SequenceMatcher(None, target, f"{i.title} {i.description}".lower()).ratio() > 0.72]

def create_product_item(payload: ProductItemCreate) -> ProductItem:
    text = f"{payload.title} {payload.description}"; dups = _duplicate_ids(payload.title, payload.description)
    priority = "high" if _contains(text, FRAUD_TERMS + BUG_TERMS) else payload.priority
    item = ProductItem(id=str(uuid4()), type=payload.type, title=payload.title, description=payload.description, status=payload.status, priority=payload.priority, labels=payload.labels, owner=payload.owner, linked_conversations=payload.linked_conversations, attachments=payload.attachments, ai_summary=payload.description[:280], ai_priority_suggestion=priority, duplicate_of=dups[0] if dups else None, created_at=_now(), updated_at=_now())
    _ITEMS[item.id] = item; log_event("product.item_created", {"item_id": item.id, "type": item.type, "duplicate_of": item.duplicate_of}); return item

def list_product_items(type: str | None = None) -> list[ProductItem]: return [i for i in _ITEMS.values() if type is None or i.type == type]
def get_product_item(item_id: str) -> ProductItem: return _ITEMS[item_id]
def product_dashboard() -> dict:
    items = list_product_items(); return {"open": [i for i in items if i.status == "open"], "in_progress": [i for i in items if i.status == "in_progress"], "completed": [i for i in items if i.status in ("completed", "closed")], "recently_reported": sorted(items, key=lambda i: i.created_at, reverse=True)[:10]}
