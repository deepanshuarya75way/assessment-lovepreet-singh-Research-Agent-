from app.models import Claim

def build_claims(analyses):
    claims=[]
    idx=1
    for i,a in enumerate(analyses,1):
        if a.findings and a.findings!="Not confidently extracted.":
            ev=a.evidence[:3]
            support=bool(ev)
            claims.append(Claim(
                id=f"C{idx}",
                claim=a.findings[:500],
                paper_ids=[a.paper_id],
                evidence=ev,
                status="Supported" if support else "Partially Supported",
                confidence=min(0.95,0.55+0.1*len(ev)) if support else 0.4,
                reason="Directly linked to retrieved evidence snippets." if support else "Finding extracted without enough direct evidence."
            ))
            idx+=1
    return claims
