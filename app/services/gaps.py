from app.models import Gap, Hypothesis

def build_gaps(analyses, contradictions):
    gaps=[
        Gap(id="G1",title="Cross-study comparability",description="Studies may use different datasets, metrics or protocols, making direct ranking unreliable.",evidence_papers=[a.paper_id for a in analyses[:4]],strength=0.82),
        Gap(id="G2",title="Incomplete reporting of limitations",description="Limitations and future-work statements are inconsistently reported across the retrieved literature.",evidence_papers=[a.paper_id for a in analyses if a.limitations!="Not confidently extracted."][:5],strength=0.72),
        Gap(id="G3",title="Open-access evidence coverage",description="Some papers lack accessible full text, restricting automated page-level evidence extraction.",evidence_papers=[a.paper_id for a in analyses if not a.evidence],strength=0.68)
    ]
    if contradictions:
        gaps.append(Gap(id="G4",title="Divergent findings",description="Potentially divergent reported outcomes require controlled reproduction under common experimental settings.",evidence_papers=[],strength=0.79))
    hyps=[
        Hypothesis(id="H1",hypothesis="A common benchmark and evaluation protocol will reduce uncertainty in cross-paper performance comparisons.",rationale="The literature uses heterogeneous experimental conditions.",test_design="Re-run representative methods on the same datasets with identical metrics.",evidence_papers=[a.paper_id for a in analyses[:3]]),
        Hypothesis(id="H2",hypothesis="A hybrid approach combining complementary components from leading methods can improve robustness.",rationale="Different papers expose complementary strengths and limitations.",test_design="Implement the hybrid, then compare against the strongest baselines under matched compute budgets.",evidence_papers=[a.paper_id for a in analyses[:4]])
    ]
    return gaps,hyps
