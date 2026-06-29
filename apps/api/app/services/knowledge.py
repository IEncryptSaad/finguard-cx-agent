from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException, status
from app.models.schemas import KnowledgeArticle
from app.services.audit import log_event

_ARTICLES: dict[str, KnowledgeArticle] = {}
_SEEDED = False
_ALLOWED_EXTENSIONS = {".txt", ".md", ".markdown", ".pdf", ".docx"}
_MAX_UPLOAD_BYTES = 2 * 1024 * 1024


def seed_articles():
    global _SEEDED
    if _SEEDED or _ARTICLES:
        return
    create_article(
        "Card dispute basics",
        "We can help file a dispute and may request transaction details, never full card numbers.",
        ["dispute", "card"],
    )
    _SEEDED = True


def create_article(title: str, body: str, tags: list[str] | None = None) -> KnowledgeArticle:
    a = KnowledgeArticle(id=str(uuid4()), title=title.strip(), body=body.strip(), tags=tags or [])
    _ARTICLES[a.id] = a
    log_event("knowledge.created", {"article_id": a.id})
    return a


def list_articles() -> list[KnowledgeArticle]:
    seed_articles()
    return list(_ARTICLES.values())


def update_article(article_id: str, title: str, body: str, tags: list[str] | None = None) -> KnowledgeArticle:
    if article_id not in _ARTICLES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge article not found")
    a = KnowledgeArticle(id=article_id, title=title.strip(), body=body.strip(), tags=tags or [])
    _ARTICLES[article_id] = a
    log_event("knowledge.updated", {"article_id": article_id})
    return a


def delete_article(article_id: str) -> None:
    if article_id not in _ARTICLES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge article not found")
    _ARTICLES.pop(article_id)
    log_event("knowledge.deleted", {"article_id": article_id})


def search_articles(query: str) -> list[KnowledgeArticle]:
    seed_articles()
    q = query.lower().strip()
    log_event("knowledge.searched", {"query": q})
    if not q:
        return list_articles()
    return [a for a in _ARTICLES.values() if q in a.title.lower() or q in a.body.lower() or any(q in t.lower() for t in a.tags)]


def ingest_document(filename: str, content: bytes) -> KnowledgeArticle:
    suffix = Path(filename).suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported document type")
    if len(content) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Document exceeds 2 MB limit")

    text = ""
    if suffix in (".txt", ".md", ".markdown"):
        text = content.decode("utf-8", errors="ignore")
    elif suffix == ".pdf":
        text = content.decode("latin-1", errors="ignore")[:20000]
    elif suffix == ".docx":
        import io
        import re
        import zipfile

        with zipfile.ZipFile(io.BytesIO(content)) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
            text = re.sub(r"<[^>]+>", " ", xml)
    return create_article(Path(filename).stem, text[:20000], [suffix.lstrip(".") or "document"])


seed_articles()
