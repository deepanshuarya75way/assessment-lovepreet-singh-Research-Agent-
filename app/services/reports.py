from pathlib import Path
def make(s):
    p=Path("data/reports");p.mkdir(parents=True,exist_ok=True)
    lines=[f"# Research Report\n\n## Question\n{s['question']}",
           "\n## Synthesis\n"+s.get("synthesis",""),
           "\n## Research Gaps\n"+"\n".join("- "+x for x in s.get("gaps",[])),
           "\n## Proposed Hypotheses\n"+"\n".join("- "+x for x in s.get("hypotheses",[])),
           "\n## Potential Contradictions\n"+"\n".join(f"- {x.topic}: {x.explanation} ({x.paper_a} vs {x.paper_b})" for x in s.get("contradictions",[])),
           "\n## Comparison\n"]
    for x in s.get("comparison",[]):lines.append(str(x))
    lines.append("\n## References\n"+"\n".join(s.get("references",[])))
    f=p/f"{s['run_id']}.md";f.write_text("\n".join(lines),encoding="utf-8");return str(f)
