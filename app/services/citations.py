def format_ref(i,p,style="IEEE"):
    authors=p.authors[:6]
    names=", ".join(authors) if authors else "Unknown"
    if style.upper()=="APA":
        return f"{names} ({p.year or 'n.d.'}). {p.title}. DOI: {p.doi or 'N/A'}."
    if style.upper()=="MLA":
        return f'{names}. "{p.title}." {p.year or "n.d."}. DOI: {p.doi or "N/A"}.'
    return f"[{i}] {names}, \"{p.title},\" {p.year or 'n.d.'}. DOI: {p.doi or 'N/A'}."
