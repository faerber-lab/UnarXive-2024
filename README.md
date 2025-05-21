# UnarXive-2024
This project presents an updated and extended version of the UnarXive dataset, a large-scale full-text scholarly corpus derived from [arXiv.org](https://arxiv.org). We process and structure over 2.3 million papers, preserving rich document content and enriching metadata. Our pipeline enhances section-level grouping while maintaining compatibility with existing formats.

## 📦 Dataset Overview

The dataset consists of structured JSONL files, each representing a parsed scholarly document from arXiv. Each document includes:

- Full-text grouped by sections
- Metadata (title, authors, abstract, date, language, cited_by_count etc.)
- Citation information (bib entries and reference entries)
- Structural annotations like `cite_spans` and `ref_spans`
- Licensing and category labels
---

## 📈 Growth Statistics

As of 2022, UnarXive had indexed **1,882,082** papers. Between **January 2023** and **December 2024**, an additional **456,829** papers were submitted. The number of submissions continues to grow exponentially (see Figure 1).

This brings the total number of papers in our dataset to **2,338,911**.

Among these:
- 📘 **Physics**: 1,146,066 papers (49.12%)
- 🧮 **Mathematics**: 584,727 papers (25.28%)
- 💻 **Computer Science**: 608,118 papers (25,6%)
---

## 🧠 Use Cases

The dataset is well-suited for a wide range of NLP and bibliometric applications:

- Citation recommendation
- Section-aware classification
- Scientific summarization
- Network analysis
- Trend detection in research fields

---

## 🗃️ File Structure

Each paper is represented in JSONL format:

```json
{
  "paper_id": "2412.00056",
  "metadata": {
    "id": "2412.00056",
    "submitter": "...",
    "authors": " ... ",
    "title": "Improving Medical ...",
    "comments": "15 pages",
    "journal-ref": null,
    "doi": null,
    "report-no": null,
    "categories": "cs.CV cs.AI",
    "license": "http://creativecommons.org/licenses/by/4.0/",
    "abstract": "In recent years, vision-language...",
    "versions": [ ... ],
    "update_date": "2024-12-03",
    "authors_parsed": [ ... ],
    "language": "en",
    "citation_count": 5,
    "discipline": "Computer Science"
  },
  "abstract": "...",
  "bib_entries": { ... },
  "ref_entries": { ... },
  "sections": {
    "Introduction": {
      "text": "...",
      "cite_spans": [ ... ],
      "ref_spans": [ ... ]
    }
  }
}

