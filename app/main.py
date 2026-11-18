import uuid, asyncio, traceback
from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse,PlainTextResponse,StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.models import ResearchRequest,ResearchResponse
from app.agents.graph import build
from app.services.progress import init,emit,complete,fail,stream_events,RUNS
from app.services.exports import make_exports

app=FastAPI(title="Research Agent v4",version="4.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
GRAPH=build()

STEPS=[
("planner","Planning research strategy",10),
("search","Searching scholarly sources",25),
("retrieve","Retrieving open-access evidence",42),
("analyze","Analyzing papers",58),
("contradictions","Checking divergent findings",68),
("synthesize","Synthesizing literature",78),
("verify","Verifying claim/evidence links",88),
("refs","Formatting citations",94),
("kg","Building graphs and report",99),
]

def _execute_graph(rid, base, node_messages):
    """Run synchronous LangGraph work off the ASGI event loop so SSE can stream."""
    state = {}
    for update in GRAPH.stream(base, stream_mode="updates"):
        for node, delta in update.items():
            state.update(delta)
            label, message, pct = node_messages.get(node, (node, node, 50))
            emit(rid, label, message, pct)
    # Preserve request fields and the final graph state.
    state.update(base)
    return state


async def run_job(rid, r):
    try:
        base = {
            "run_id": rid,
            "question": r.question,
            "year_from": r.year_from,
            "year_to": r.year_to,
            "max_papers": r.max_papers,
            "citation_style": r.citation_style,
        }
        node_messages = {
            "planner": ("Planner", "Planning research strategy", 8),
            "search": ("Search", "Searching OpenAlex and Semantic Scholar", 20),
            "retrieve": ("Retrieve", "Retrieving papers and extracting evidence", 34),
            "analyze": ("Analyze", "Analyzing paper methods, findings and limitations", 48),
            "contradictions": ("Contradictions", "Checking for potentially divergent findings", 60),
            "synthesize": ("Synthesis", "Synthesizing the literature", 72),
            "verify": ("Verify", "Linking claims to available evidence", 82),
            "refs": ("Citations", "Formatting references", 90),
            "kg": ("Graphs", "Building paper relationship and similarity maps", 95),
        }
        # GRAPH.stream is synchronous. Running it directly inside async run_job
        # blocked FastAPI's event loop, so the browser received progress in a burst.
        state = await asyncio.to_thread(_execute_graph, rid, base, node_messages)
        emit(rid, "Report", "Generating PDF, DOCX and Markdown reports", 98)
        state["run_id"] = rid
        state["report_urls"] = make_exports(state)
        complete(rid, state)
    except Exception as exc:
        traceback.print_exc()
        fail(rid, exc)

@app.get("/api/health")
def health():
    from app.config import GEMINI_API_KEY
    return {"status":"ok","version":"4.0.0","llm":"gemini" if GEMINI_API_KEY else "local"}

@app.post("/api/research")
async def research(r:ResearchRequest):
    rid=uuid.uuid4().hex[:12]
    init(rid)
    asyncio.create_task(run_job(rid,r))
    return {"run_id":rid,"status":"started","events_url":f"/api/events/{rid}"}

@app.get("/api/events/{rid}")
async def events(rid):
    return StreamingResponse(stream_events(rid),media_type="text/event-stream",headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

@app.get("/api/result/{rid}",response_model=ResearchResponse)
def result(rid):
    rec=RUNS.get(rid)
    if not rec or rec.get("status")!="completed":
        raise HTTPException(202,detail=rec.get("status","not ready") if rec else "not found")
    s=rec["result"]
    return ResearchResponse(run_id=rid,question=s["question"],plan=s.get("plan",{}),queries=s.get("queries",[]),
        papers=s.get("papers",[]),analyses=s.get("analyses",[]),claims=s.get("claims",[]),
        contradictions=s.get("contradictions",[]),synthesis=s.get("synthesis",""),gaps=s.get("gaps",[]),
        hypotheses=s.get("hypotheses",[]),comparison=s.get("comparison",[]),
        knowledge_graph=s.get("knowledge_graph",{}),similarity=s.get("similarity",{}),
        references=s.get("references",[]),citation_style=s.get("citation_style","IEEE"),
        report_urls=s.get("report_urls",{}))

@app.post("/api/chat")
def chat(body:dict):
    rid=body.get("run_id");q=body.get("question","")
    rec=RUNS.get(rid)
    if not rec or rec.get("status")!="completed": raise HTTPException(404,"Research run not found")
    from app.services.llm import ask
    s=rec["result"]
    context="\n".join(f"[P{i+1}] {a.title}: {a.summary} Evidence: "+" | ".join(e.quote for e in a.evidence) for i,a in enumerate(s.get("analyses",[])))
    ans=ask(f"Answer only from this research context. Cite [P#]. If unsupported, say that clearly.\nQuestion: {q}\nContext:\n{context}")
    return {"answer":ans or "Gemini is not configured. Use the evidence shown in the report to answer this question."}

@app.get("/api/report/{rid}.{ext}")
def report(rid,ext):
    f=Path("data/reports")/f"{rid}.{ext}"
    if not f.exists():raise HTTPException(404,"Report not found")
    media={"md":"text/markdown","pdf":"application/pdf","docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}.get(ext,"application/octet-stream")
    return FileResponse(str(f),media_type=media,filename=f.name)

app.mount("/static",StaticFiles(directory="frontend"),name="static")
@app.get("/")
def index():return FileResponse("frontend/index.html")
