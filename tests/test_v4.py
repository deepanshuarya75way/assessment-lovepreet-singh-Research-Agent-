from app.agents.nodes import planner
from app.services.similarity import build_similarity
from app.models import Paper

def test_planner():
    x=planner({"question":"How are transformers used for medical image classification?"})
    assert len(x["queries"]) >= 2

def test_similarity():
    p=[Paper(id="1",title="CNN medical image classification",abstract="image classification medical"),
       Paper(id="2",title="Transformer medical image classification",abstract="transformer image classification medical")]
    x=build_similarity(p)
    assert len(x["nodes"])==2
