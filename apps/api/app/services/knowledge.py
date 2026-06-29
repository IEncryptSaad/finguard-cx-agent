from uuid import uuid4
from app.models.schemas import KnowledgeArticle
_ARTICLES: dict[str, KnowledgeArticle] = {}
def seed_articles():
    if not _ARTICLES:
        create_article("Card dispute basics", "We can help file a dispute and may request transaction details, never full card numbers.", ["dispute", "card"])
def create_article(title: str, body: str, tags: list[str] | None = None) -> KnowledgeArticle:
    a=KnowledgeArticle(id=str(uuid4()), title=title, body=body, tags=tags or []) ; _ARTICLES[a.id]=a; return a
def list_articles() -> list[KnowledgeArticle]: seed_articles(); return list(_ARTICLES.values())
def update_article(article_id: str, title: str, body: str, tags: list[str] | None = None) -> KnowledgeArticle:
    a=KnowledgeArticle(id=article_id,title=title,body=body,tags=tags or []); _ARTICLES[article_id]=a; return a
def delete_article(article_id: str) -> None: _ARTICLES.pop(article_id, None)
