# UnarXive-2024
This project presents an updated and extended version of the UnarXive dataset, a large-scale full-text scholarly corpus derived from [arXiv.org](https://arxiv.org). We process and structure over 2.3 million papers, preserving rich document content and enriching metadata. Our pipeline enhances section-level grouping while maintaining compatibility with existing formats.

## Dataset Overview

The dataset consists of structured JSONL files, each representing a parsed scholarly document from arXiv. Each document includes:

- Full-text grouped by sections
- Metadata (title, authors, abstract, date, language, cited_by_count etc.)
- Citation information (bib entries and reference entries)
- Structural annotations like `cite_spans` and `ref_spans`
- Licensing and category labels
---

## Key Statistics

The total number of papers in our dataset is **2,338,911**.
Among these:
- **Physics**: 1,146,066 papers (49.12%)
- **Mathematics**: 584,727 papers (25.28%)
- **Computer Science**: 608,118 papers (25,6%)
---

