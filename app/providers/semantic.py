import httpx
from app.models import Paper

def search(query,year_from,year_to,limit):
    params={"query":query,"limit":min(limit,20),"fields":"title,abstract,authors,year,externalIds,url,openAccessPdf,citationCount"}
    with httpx.Client(timeout=30,follow_redirects=True) as c:
        r=c.get("https://api.semanticscholar.org/graph/v1/paper/search",params=params,headers={"User-Agent":"ResearchAgent/3.0"})
        r.raise_for_status();data=r.json()
    out=[]
    for x in data.get("data",[]):
        y=x.get("year")
        if y and not(year_from<=y<=year_to):continue
        ids=x.get("externalIds") or {};oa=x.get("openAccessPdf") or {}
        out.append(Paper(id=x.get("paperId",""),title=x.get("title") or "Untitled",
            authors=[a.get("name") for a in (x.get("authors") or [])[:8]],year=y,doi=ids.get("DOI"),
            url=x.get("url"),pdf_url=oa.get("url"),abstract=x.get("abstract") or "",
            cited_by=x.get("citationCount") or 0,source="Semantic Scholar",full_text_available=bool(oa.get("url"))))
    return out
