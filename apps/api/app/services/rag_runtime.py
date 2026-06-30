import math, re
from datetime import datetime, timezone
from uuid import uuid4
from app.models.schemas import RagChunk, RagQueryRequest, RagQueryResponse, RagSourceCitation
from app.services.audit import log_event
from app.services.knowledge import list_articles

_CHUNKS: dict[str, RagChunk] = {}
_STATS={'queries':0,'chunks_indexed':0,'last_query_at':None}

def _now(): return datetime.now(timezone.utc).isoformat()
def _tokens(text): return re.findall(r'[a-z0-9]+', text.lower())
def _score(q, text):
    qs=set(_tokens(q)); ts=set(_tokens(text))
    return 0.0 if not qs else len(qs & ts)/math.sqrt(max(1,len(ts)))

def chunk_text(source_id:str, text:str, *, source_type='knowledge_article', max_chars=700, metadata=None, permissions=None):
    words=text.split(); chunks=[]; buf=[]; size=0; idx=0
    for w in words:
        if size+len(w)+1>max_chars and buf:
            chunks.append(_make(source_id, idx, ' '.join(buf), source_type, metadata, permissions)); idx+=1; buf=[]; size=0
        buf.append(w); size+=len(w)+1
    if buf: chunks.append(_make(source_id, idx, ' '.join(buf), source_type, metadata, permissions))
    return chunks

def _make(source_id, idx, text, source_type, metadata, permissions):
    c=RagChunk(id=str(uuid4()), source_id=source_id, source_type=source_type, chunk_index=idx, text=text, metadata=metadata or {}, permissions=permissions or [], created_at=_now())
    _CHUNKS[c.id]=c; return c

def rebuild_index():
    _CHUNKS.clear()
    for a in list_articles(): chunk_text(a.id, a.body, metadata={'title':a.title,'tags':a.tags})
    _STATS['chunks_indexed']=len(_CHUNKS); log_event('rag.index_rebuilt', {'chunks':len(_CHUNKS)}); return list(_CHUNKS.values())

def query_rag(req:RagQueryRequest):
    if not _CHUNKS: rebuild_index()
    _STATS['queries']+=1; _STATS['last_query_at']=_now()
    scored=[]
    for c in _CHUNKS.values():
        if req.allowed_permissions and c.permissions and not set(c.permissions).issubset(set(req.allowed_permissions)): continue
        s=_score(req.query, c.text)
        if s>0: scored.append((s,c))
    scored=sorted(scored, key=lambda x:x[0], reverse=True)[:req.top_k]
    cites=[RagSourceCitation(source_id=c.source_id, chunk_id=c.id, title=c.metadata.get('title'), score=round(s,4), excerpt=c.text[:240]) for s,c in scored]
    answer='No grounded sources matched the query.' if not cites else 'Grounded draft based on retrieved sources: ' + ' '.join(c.excerpt for c in cites[:2])[:600]
    resp=RagQueryResponse(answer=answer, citations=cites, grounded=bool(cites), metadata={'retriever':'local_keyword','embedding_provider':'keyword_fallback','query_at':_STATS['last_query_at']})
    log_event('rag.query', {'query':req.query, 'matches':len(cites), 'grounded':resp.grounded}); return resp

def rag_stats(): return {**_STATS, 'chunks_indexed':len(_CHUNKS), 'embedding_provider':'keyword_fallback'}
