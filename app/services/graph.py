import re


def build_graph(papers, analyses, question):
    """Build a compact, deduplicated paper-to-method/dataset graph for display."""
    nodes, edges = [], []
    seen_concepts = {}
    max_papers = min(len(papers), 12)

    for i, paper in enumerate(papers[:max_papers]):
        pid = f"P{i+1}"
        nodes.append({
            "id": pid,
            "label": (paper.title or f"Paper {i+1}").strip(),
            "type": "paper",
            "year": paper.year,
        })
        analysis = analyses[i] if i < len(analyses) else None
        if not analysis:
            continue

        for kind, raw in (("method", getattr(analysis, "method", "")),
                          ("dataset", getattr(analysis, "dataset", ""))):
            # Only extract a few useful noun-like phrases; dedupe across papers.
            phrases = re.findall(
                r"\b(?:[A-Z][A-Za-z0-9-]{2,})(?:\s+[A-Z][A-Za-z0-9-]{2,}){0,2}\b",
                raw or ""
            )
            added_for_paper = 0
            for phrase in phrases:
                phrase = " ".join(phrase.split()).strip(" .,:;")
                if len(phrase) < 4 or phrase.lower() in {
                    "not confidently extracted", "future work", "the proposed"
                }:
                    continue
                key = (kind, phrase.casefold())
                if key not in seen_concepts:
                    if len(seen_concepts) >= 18:
                        continue
                    cid = f"{kind}-{len(seen_concepts)+1}"
                    seen_concepts[key] = cid
                    nodes.append({"id": cid, "label": phrase, "type": kind})
                edges.append({"source": pid, "target": seen_concepts[key]})
                added_for_paper += 1
                if added_for_paper >= 2:
                    break

    # Remove duplicate edges while preserving order.
    unique_edges = []
    seen_edges = set()
    for edge in edges:
        key = (edge["source"], edge["target"])
        if key not in seen_edges:
            unique_edges.append(edge)
            seen_edges.add(key)
    return {"nodes": nodes, "edges": unique_edges}
