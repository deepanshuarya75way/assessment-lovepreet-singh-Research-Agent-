from langgraph.graph import StateGraph,END
from app.agents.state import State
from app.agents.nodes import planner,search,retrieve,analyze,contradictions,synthesize,verify_and_gaps,refs,kg

def build():
    g=StateGraph(State)
    for n,f in {"planner":planner,"search":search,"retrieve":retrieve,"analyze":analyze,
                "contradictions":contradictions,"synthesize":synthesize,
                "verify":verify_and_gaps,"refs":refs,"kg":kg}.items():
        g.add_node(n,f)
    g.set_entry_point("planner")
    for a,b in [("planner","search"),("search","retrieve"),("retrieve","analyze"),
                ("analyze","contradictions"),("contradictions","synthesize"),
                ("synthesize","verify"),("verify","refs"),("refs","kg"),("kg",END)]:
        g.add_edge(a,b)
    return g.compile()
