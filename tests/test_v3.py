from app.agents.nodes import planner
from app.services.retrieval import terms
def test_planner():
    x=planner({"question":"How are transformers used for medical image classification?"})
    assert len(x["queries"])>=2
def test_terms():
    assert "transformers" in terms("How are transformers used for medical image classification?")
