import httpx
from app.models import Paper
from app.config import OPENALEX_API_KEY

def _abstract(idx):
    if not idx:return ""
    a=[]
    for w,ps in idx.items():
        for p in ps:a.append((p,w))
    return " ".join(w for _,w in sorted(a))[:12000]

def search(query,year_from,year_to,limit):
    params={"search":query,"filter":f"from_publication_date:{year_from}-01-01,to_publication_date:{year_to}-12-31","per-page":min(limit,50),"sort":"relevance_score:desc"}
    if OPENALEX_API_KEY:params["api_key"]=OPENALEX_API_KEY
    with httpx.Client(timeout=30,follow_redirects=True) as c:
        r=c.get("https://api.openalex.org/works",params=params,headers={"User-Agent":"ResearchAgent/3.0"})
        r.raise_for_status();data=r.json()
    out=[]
    for x in data.get("results",[]):
        oa=x.get("open_access") or {};best=x.get("best_oa_location") or {};primary=x.get("primary_location") or {}
        pdf=best.get("pdf_url") or primary.get("pdf_url") or oa.get("oa_url")
        out.append(Paper(id=x.get("id","").split("/")[-1],title=x.get("display_name") or "Untitled",
            authors=[a.get("author",{}).get("display_name") for a in x.get("authorships",[])[:8] if a.get("author")],
            year=x.get("publication_year"),doi=(x.get("doi") or "").replace("https://doi.org/","") or None,
            url=x.get("doi") or x.get("id"),pdf_url=pdf,abstract=_abstract(x.get("abstract_inverted_index")),
            cited_by=x.get("cited_by_count") or 0,source="OpenAlex",full_text_available=bool(pdf)))
    return out
