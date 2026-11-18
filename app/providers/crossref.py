import httpx
def enrich(doi):
    if not doi:return {}
    try:
        with httpx.Client(timeout=15,follow_redirects=True) as c:
            r=c.get("https://api.crossref.org/works/"+doi,headers={"User-Agent":"ResearchAgent/3.0"})
            if r.status_code!=200:return {}
            return r.json().get("message",{})
    except Exception:return {}
