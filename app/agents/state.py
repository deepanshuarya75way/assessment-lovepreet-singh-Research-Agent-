from typing import TypedDict,List,Dict,Any
from app.models import Paper,PaperAnalysis,Evidence,Claim,Contradiction,Gap,Hypothesis,ComparisonRow
class State(TypedDict,total=False):
    run_id:str;question:str;year_from:int;year_to:int;max_papers:int;citation_style:str
    plan:Dict[str,Any];queries:List[str];papers:List[Paper]
    paper_text:Dict[str,str];evidence:Dict[str,List[Evidence]]
    analyses:List[PaperAnalysis];claims:List[Claim];contradictions:List[Contradiction]
    synthesis:str;gaps:List[Gap];hypotheses:List[Hypothesis]
    comparison:List[ComparisonRow];knowledge_graph:Dict[str,Any];similarity:Dict[str,Any]
    references:List[str]
