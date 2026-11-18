import re
from app.agents.state import State
from app.models import PaperAnalysis, Contradiction, ComparisonRow
from app.providers.openalex import search as oa
from app.providers.semantic import search as ss
from app.providers.crossref import enrich
from app.services.retrieval import rank, pdf_text, evidence
from app.services.credibility import score
from app.services.claims import build_claims
from app.services.gaps import build_gaps
from app.services.similarity import build_similarity
from app.services.graph import build_graph
from app.services.llm import json_ask

def planner(s):
    q=s["question"]
    terms=[x for x in re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}",q.lower())
           if x not in {"what","which","how","are","the","and","for","with","from","using","about","recent"}][:12]
    core=" ".join(terms)
    return {"plan":{"objective":q,"sub_questions":[
        "What methods dominate the literature?","Which datasets and metrics are used?",
        "Where do findings agree or disagree?","What limitations and gaps remain?",
        "What can be tested next?"
    ],"sources":["OpenAlex","Semantic Scholar","Crossref"],
    "evidence_policy":"Claims must map to retrieved evidence; hypotheses are not presented as established facts."},
    "queries":list(dict.fromkeys([q,core+" review survey",core+" benchmark comparison",core+" limitations future work"]))}

def search(s):
    allp=[]
    for q in s["queries"]:
        for fn in (oa,ss):
            try: allp += fn(q,s["year_from"],s["year_to"],s["max_papers"])
            except Exception: pass
    u={}
    for p in allp:
        k=(p.doi or re.sub(r"\W+","",p.title.lower()))
        if k not in u or p.cited_by>u[k].cited_by:u[k]=p
    papers=rank(s["question"],list(u.values()))[:s["max_papers"]]
    return {"papers":[score(p) for p in papers]}

def retrieve(s):
    texts={};ev={}
    for p in s["papers"]:
        t=pdf_text(p.pdf_url) if p.pdf_url else ""
        texts[p.id]=t;ev[p.id]=evidence(s["question"],p,t)
    return {"paper_text":texts,"evidence":ev}

def analyze(s):
    out=[]
    for p in s["papers"]:
        src=s["paper_text"].get(p.id) or p.abstract
        def f(pat,d):
            m=re.search(pat,src,re.I)
            if not m:return d
            try:v=m.group(1)
            except IndexError:v=m.group(0)
            return v[:900]
        out.append(PaperAnalysis(
            paper_id=p.id,title=p.title,
            summary=(p.abstract or src[:1000])[:1000],
            method=f(r"(?:propose|present|introduce|method|approach|architecture|framework)[^.]{20,400}\.","Not confidently extracted."),
            dataset=f(r"(?:dataset|datasets|benchmark)[^.]{20,350}\.","Not confidently extracted."),
            findings=f(r"(?:results?|achieve|outperform|improv|performance)[^.]{20,400}\.","Not confidently extracted."),
            limitations=f(r"(?:limitation|limitations|challenge|future work|future research)[^.]{20,400}\.","Not confidently extracted."),
            evidence=s["evidence"].get(p.id,[])))
    return {"analyses":out}

def contradictions(s):
    rows=[]
    for i,a in enumerate(s["analyses"]):
        for b in s["analyses"][i+1:]:
            fa=(a.findings or "").lower();fb=(b.findings or "").lower()
            pos=lambda x:any(k in x for k in ["better","higher","outperform","improv"])
            neg=lambda x:any(k in x for k in ["lower","worse","degrad","underperform"])
            if pos(fa) and neg(fb) or neg(fa) and pos(fb):
                rows.append(Contradiction(topic="Potentially divergent performance language",
                    paper_a=a.title,paper_b=b.title,
                    explanation="Extracted result language points in different directions. Check the original datasets, baselines and metrics before treating this as a true contradiction.",
                    severity="Potential"))
    return {"contradictions":rows[:8]}

def synthesize(s):
    blocks=[]
    for i,a in enumerate(s["analyses"],1):
        blocks.append(f"[P{i}] {a.title}\nSUMMARY:{a.summary}\nMETHOD:{a.method}\nDATASET:{a.dataset}\nFINDINGS:{a.findings}\nLIMITATIONS:{a.limitations}\nEVIDENCE:"+" | ".join(e.quote for e in a.evidence))
    prompt=f"""You are a rigorous scientific reviewer.
Research question: {s['question']}
Use ONLY the supplied evidence. Do not invent facts, results or references.
Return JSON with:
synthesis (a coherent literature review using [P1] citations),
comparison (array of paper/method/dataset/findings/limitations),
gaps (array of strings),
hypotheses (array of strings).
Clearly distinguish evidence from interpretation and hypotheses.
Evidence:
{chr(10).join(blocks)}"""
    obj=json_ask(prompt)
    if obj:
        comparison=[ComparisonRow(paper=str(x.get("paper","")),method=str(x.get("method","")),dataset=str(x.get("dataset","")),findings=str(x.get("findings","")),limitations=str(x.get("limitations",""))) for x in obj.get("comparison",[])]
        return {"synthesis":obj.get("synthesis",""),"comparison":comparison,
                "gaps":[str(x) for x in obj.get("gaps",[])],"hypotheses":[str(x) for x in obj.get("hypotheses",[])]}
    return {"synthesis":"\n\n".join(f"[P{i+1}] {a.title}: {a.summary[:700]}" for i,a in enumerate(s["analyses"])),
        "comparison":[ComparisonRow(paper=f"[P{i+1}]",method=a.method,dataset=a.dataset,findings=a.findings,limitations=a.limitations,quality=s["papers"][i].quality) for i,a in enumerate(s["analyses"])],
        "gaps":[],"hypotheses":[]}

def verify_and_gaps(s):
    claims=build_claims(s["analyses"])
    gaps,hyps=build_gaps(s["analyses"],s["contradictions"])
    if s.get("gaps"):
        # LLM gaps are supplementary; keep deterministic evidence-grounded gaps first.
        gaps = gaps + [type(gaps[0])(id=f"LLM{i+1}",title="LLM-suggested gap",description=g,evidence_papers=[],strength=0.6) for i,g in enumerate(s["gaps"][:3])]
    if s.get("hypotheses"):
        hyps = hyps + [type(hyps[0])(id=f"LLM{i+1}",hypothesis=h,rationale="Generated from the retrieved literature.",test_design="Design a controlled empirical evaluation.",evidence_papers=[]) for i,h in enumerate(s["hypotheses"][:3])]
    return {"claims":claims,"gaps":gaps[:7],"hypotheses":hyps[:6]}

def refs(s):
    from app.services.citations import format_ref
    return {"references":[format_ref(i,p,s["citation_style"]) for i,p in enumerate(s["papers"],1)]}

def kg(s):
    return {"knowledge_graph":build_graph(s["papers"],s["analyses"],s["question"]),
            "similarity":build_similarity(s["papers"])}
