from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_similarity(papers):
    if not papers:
        return {"nodes": [], "edges": []}
    docs=[(p.title+" "+p.abstract).strip() for p in papers]
    try:
        v=TfidfVectorizer(stop_words="english",ngram_range=(1,2),max_features=12000)
        m=v.fit_transform(docs)
        sim=cosine_similarity(m)
    except Exception:
        return {"nodes":[{"id":f"P{i+1}","label":p.title[:60]} for i,p in enumerate(papers)],"edges":[]}
    edges=[]
    for i in range(len(papers)):
        for j in range(i+1,len(papers)):
            score=float(sim[i,j])
            if score >= 0.18:
                edges.append({"source":f"P{i+1}","target":f"P{j+1}","weight":round(score,3)})
    return {
        "nodes":[{"id":f"P{i+1}","label":p.title[:60],"year":p.year,"quality":p.quality} for i,p in enumerate(papers)],
        "edges":edges
    }
