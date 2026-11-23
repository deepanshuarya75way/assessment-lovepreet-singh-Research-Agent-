from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ResearchRequest(BaseModel):
    question: str = Field(min_length=8)
    year_from: int = 2020
    year_to: int = 2026
    max_papers: int = Field(default=8, ge=3, le=15)
    citation_style: str = Field(default="IEEE")
    exact_match_boost: bool =False

class Paper(BaseModel):
    id: str
    title: str
    authors: List[str] = []
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    abstract: str = ""
    cited_by: int = 0
    source: str = "Unknown"
    relevance: float = 0
    quality: float = 0
    credibility_label: str = "Unrated"
    full_text_available: bool = False

class Evidence(BaseModel):
    paper_id: str
    title: str
    quote: str
    locator: str = "Extracted text"
    url: Optional[str] = None
    score: float = 0

class PaperAnalysis(BaseModel):
    paper_id: str
    title: str
    summary: str
    method: str
    dataset: str
    findings: str
    limitations: str
    evidence: List[Evidence] = []

class Claim(BaseModel):
    id: str
    claim: str
    paper_ids: List[str] = []
    evidence: List[Evidence] = []
    status: str = "Unverified"
    confidence: float = 0.0
    reason: str = ""

class Contradiction(BaseModel):
    topic: str
    paper_a: str
    paper_b: str
    explanation: str
    severity: str = "Potential"

class Gap(BaseModel):
    id: str
    title: str
    description: str
    evidence_papers: List[str] = []
    strength: float = 0.0

class Hypothesis(BaseModel):
    id: str
    hypothesis: str
    rationale: str
    test_design: str
    evidence_papers: List[str] = []

class ComparisonRow(BaseModel):
    paper: str
    method: str = ""
    dataset: str = ""
    findings: str = ""
    limitations: str = ""
    quality: float = 0.0

class ResearchResponse(BaseModel):
    run_id: str
    question: str
    plan: Dict[str, Any]
    queries: List[str]
    papers: List[Paper]
    analyses: List[PaperAnalysis]
    claims: List[Claim] = []
    contradictions: List[Contradiction] = []
    synthesis: str = ""
    gaps: List[Gap] = []
    hypotheses: List[Hypothesis] = []
    comparison: List[ComparisonRow] = []
    knowledge_graph: Dict[str, Any] = {}
    similarity: Dict[str, Any] = {}
    references: List[str] = []
    citation_style: str = "IEEE"
    report_urls: Dict[str, str] = {}
