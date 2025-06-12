
def process_sections(paper,paper_info):
    sections = {}
    for entry in paper.get("body_text", []):
        sec_name = entry.get("section", "Unknown Section")
        text = entry.get("text", "").strip()
        sec = sections.setdefault(sec_name, {"text": "", "cite_spans": [], "ref_spans": []})
        offset = len(sec["text"])
        sec["text"] += text

        for span in entry.get("cite_spans", []):
            span["start"] += offset
            span["end"] += offset
            sec["cite_spans"].append(span)

        for span in entry.get("ref_spans", []):
            span["start"] += offset
            span["end"] += offset
            sec["ref_spans"].append(span)

    paper_info["sections"] = sections
    return paper_info
