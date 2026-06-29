from pathlib import Path
from uuid import uuid4
from app.models.schemas import KnowledgeArticle
from app.services.audit import log_event
_ARTICLES: dict[str, KnowledgeArticle] = {}
def seed_articles():
    if not any(a.title == "Card dispute basics" for a in _ARTICLES.values()):
        create_article("Card dispute basics", "We can help file a dispute and may request transaction details, never full card numbers.", ["dispute", "card"])
def create_article(title: str, body: str, tags: list[str] | None = None) -> KnowledgeArticle:
    a=KnowledgeArticle(id=str(uuid4()), title=title.strip(), body=body.strip(), tags=tags or []) ; _ARTICLES[a.id]=a; log_event("knowledge.created", {"article_id": a.id}); return a
def list_articles() -> list[KnowledgeArticle]: seed_articles(); return list(_ARTICLES.values())
def update_article(article_id: str, title: str, body: str, tags: list[str] | None = None) -> KnowledgeArticle:
    a=KnowledgeArticle(id=article_id,title=title.strip(),body=body.strip(),tags=tags or []); _ARTICLES[article_id]=a; log_event("knowledge.updated", {"article_id": article_id}); return a
def delete_article(article_id: str) -> None: _ARTICLES.pop(article_id, None); log_event("knowledge.deleted", {"article_id": article_id})
def search_articles(query: str) -> list[KnowledgeArticle]:
    seed_articles(); q=query.lower().strip(); log_event("knowledge.searched", {"query": q})
    if not q: return list_articles()
    return [a for a in _ARTICLES.values() if q in a.title.lower() or q in a.body.lower() or any(q in t.lower() for t in a.tags)]
def ingest_document(filename: str, content: bytes) -> KnowledgeArticle:
    suffix = Path(filename).suffix.lower(); text = ""
    if suffix in (".txt", ".md", ".markdown"):
        text = content.decode("utf-8", errors="ignore")
    elif suffix == ".pdf":
        text = content.decode("latin-1", errors="ignore")[:20000]
    elif suffix == ".docx":
        import zipfile, io, re
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
            text = re.sub(r"<[^>]+>", " ", xml)
    else:
        raise ValueError("Unsupported document type")
    return create_article(Path(filename).stem, text[:20000], [suffix.lstrip('.') or 'document'])
