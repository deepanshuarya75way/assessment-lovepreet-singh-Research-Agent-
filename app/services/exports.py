from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document

OUT=Path("data/reports"); OUT.mkdir(parents=True,exist_ok=True)

def markdown(s):
    lines=[
        "# Research Report",
        f"## Research Question\n{s['question']}",
        "## Literature Synthesis\n"+s.get("synthesis",""),
        "## Research Gaps\n"+"\n".join(f"- {g.title}: {g.description}" for g in s.get("gaps",[])),
        "## Proposed Hypotheses\n"+"\n".join(f"- {h.hypothesis}\n  - Rationale: {h.rationale}\n  - Test: {h.test_design}" for h in s.get("hypotheses",[])),
        "## Citation Verification\n"+"\n".join(f"- {c.status} ({c.confidence:.0%}): {c.claim}" for c in s.get("claims",[])),
        "## Potential Contradictions\n"+"\n".join(f"- {x.topic}: {x.explanation}" for x in s.get("contradictions",[])),
        "## References\n"+"\n".join(s.get("references",[]))
    ]
    return "\n\n".join(lines)

def make_exports(s):
    rid=s["run_id"]
    md=OUT/f"{rid}.md"; md.write_text(markdown(s),encoding="utf-8")

    doc=Document()
    doc.add_heading("Research Report",0)
    doc.add_heading("Research Question",1); doc.add_paragraph(s["question"])
    doc.add_heading("Literature Synthesis",1); doc.add_paragraph(s.get("synthesis",""))
    doc.add_heading("Research Gaps",1)
    for g in s.get("gaps",[]): doc.add_paragraph(f"{g.title}: {g.description}",style="List Bullet")
    doc.add_heading("Proposed Hypotheses",1)
    for h in s.get("hypotheses",[]): doc.add_paragraph(f"{h.hypothesis}\nRationale: {h.rationale}\nTest: {h.test_design}",style="List Bullet")
    doc.add_heading("Citation Verification",1)
    for c in s.get("claims",[]): doc.add_paragraph(f"{c.status} ({c.confidence:.0%}) — {c.claim}",style="List Bullet")
    doc.add_heading("References",1)
    for r in s.get("references",[]): doc.add_paragraph(r)
    docx=OUT/f"{rid}.docx"; doc.save(docx)

    pdf=OUT/f"{rid}.pdf"
    styles=getSampleStyleSheet()
    story=[Paragraph("Research Report",styles["Title"]),Paragraph(s["question"],styles["Heading2"]),Spacer(1,10)]
    story += [Paragraph("Literature Synthesis",styles["Heading2"]),Paragraph(s.get("synthesis","").replace("\n","<br/>"),styles["BodyText"])]
    story += [Paragraph("Research Gaps",styles["Heading2"])]
    for g in s.get("gaps",[]): story.append(Paragraph(f"<b>{g.title}</b>: {g.description}",styles["BodyText"]))
    story += [Paragraph("Proposed Hypotheses",styles["Heading2"])]
    for h in s.get("hypotheses",[]): story.append(Paragraph(f"<b>{h.hypothesis}</b><br/>Rationale: {h.rationale}<br/>Test: {h.test_design}",styles["BodyText"]))
    story += [Paragraph("References",styles["Heading2"])]
    for r in s.get("references",[]): story.append(Paragraph(r.replace("&","&amp;"),styles["BodyText"]))
    SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=40,bottomMargin=40).build(story)
    return {"markdown":f"/api/report/{rid}.md","docx":f"/api/report/{rid}.docx","pdf":f"/api/report/{rid}.pdf"}
