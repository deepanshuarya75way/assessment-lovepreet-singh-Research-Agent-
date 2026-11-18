def score(p):
    # Transparent heuristic, not a peer-review judgment.
    score=0.0
    score += min(0.35, p.cited_by/300)
    score += 0.25 if p.doi else 0
    score += 0.20 if p.year else 0
    score += 0.20 if p.abstract else 0
    p.quality=round(min(score,1.0),3)
    if p.quality>=0.75:p.credibility_label="Higher evidence metadata"
    elif p.quality>=0.5:p.credibility_label="Moderate evidence metadata"
    else:p.credibility_label="Limited metadata"
    return p
