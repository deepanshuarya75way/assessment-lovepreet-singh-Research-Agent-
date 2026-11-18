import re,httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models import Paper,Evidence
from app.config import EMBEDDING_MODEL,MAX_PDF_MB

STOP={"what","which","how","are","the","and","for","with","from","into","recent","using","use","used","their","this","that","about","between","than","does","can","have","has","been","were","was","is","in","of","to","a","an","research"}

def terms(q):return [x for x in re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}",q.lower()) if x not in STOP][:25]

def rank(q,papers):
    docs=[(p.title+" "+p.abstract).strip() for p in papers]
    if not docs or not any(docs):return papers
    v=TfidfVectorizer(stop_words="english",ngram_range=(1,2),max_features=20000)
    m=v.fit_transform(docs+[q]);scores=cosine_similarity(m[-1],m[:-1]).ravel()
    mx=max(scores) if len(scores) else 1
    for p,s in zip(papers,scores):
        p.relevance=round(float(s),4)
        p.quality=round(min(1,(0.7*float(s)/(mx or 1)) + 0.3*min(1,p.cited_by/100)),4)
    return sorted(papers,key=lambda p:(p.relevance,p.cited_by),reverse=True)

def pdf_text(url):
    if not url:return ""
    try:
        import fitz
        with httpx.Client(timeout=45,follow_redirects=True,headers={"User-Agent":"ResearchAgent/3.0"}) as c:
            r=c.get(url);r.raise_for_status()
            if len(r.content)>MAX_PDF_MB*1024*1024:return ""
        d=fitz.open(stream=r.content,filetype="pdf")
        return re.sub(r"\s+"," "," ".join(p.get_text() for p in d))[:90000]
    except Exception:return ""

def evidence(q,p,text,k=5):
    src=text or p.abstract
    if not src:return []
    qset=set(terms(q));rows=[]
    for s in re.split(r"(?<=[.!?])\s+",src):
        if 70<=len(s)<=700:
            overlap=len(qset & set(re.findall(r"[a-z]{3,}",s.lower())))
            if overlap:rows.append((overlap,s.strip()))
    rows.sort(reverse=True)
    return [Evidence(paper_id=p.id,title=p.title,quote=s,url=p.url,score=float(sc)) for sc,s in rows[:k]]

def hybrid_rank(q,items):
    # Optional dense semantic retrieval. TF-IDF remains the guaranteed fallback.
    try:
        from sentence_transformers import SentenceTransformer
        model=SentenceTransformer(EMBEDDING_MODEL)
        docs=[q]+[x[0] for x in items]
        emb=model.encode(docs,normalize_embeddings=True)
        import numpy as np
        sims=np.dot(emb[1:],emb[0])
        for item,sc in zip(items,sims):item[1]=0.55*item[1]+0.45*float(sc)
        return sorted(items,key=lambda x:x[1],reverse=True)
    except Exception:return sorted(items,key=lambda x:x[1],reverse=True)
