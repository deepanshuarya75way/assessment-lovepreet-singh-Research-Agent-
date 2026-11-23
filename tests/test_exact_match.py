from app.models import paper
from app.services.retrieval import rank

papers=[
  paper(
    id="1",
    title="Application of generative AI in medicine",
    abstract="A study of artificial intelligence in healthcare.",
    cited_by=100
  ),
  paper(
    id="2",
    title="large language models in healthcare",
    abstract="A study of language models in medical applications.",
    cited_by=20
  ),
  paper(
    id="3",
    title="healthcare data analysis using machine learning",
    abstract="machine learning applications in medicine.",
    cited_by=50
  ),
]

query= "Large LAnguage Models in Healthcare"
normal=rank(query,papers.copy(),exact_match_boost=false)
boosted=rank(query,papers.copy(),exact_match_boost=true)

print("\n normal ranking:")
for p in normal :
  print(p.title,p.relevance)

print("\n boosted ranking:")
for p in boosted :
  print(p.title,p.relevance)