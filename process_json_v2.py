import os
import json
import re
from urllib.parse import quote
import requests
from collections import defaultdict
from langdetect import detect
from multiprocessing import Pool
import sys

def clean_title(title):
    if not title:
        return ""
    return ' '.join(title.replace('\n', ' ').replace(',', '').replace('.', '').split())

def fetch_citation_count_and_language(doi, title):
    if not doi and not title:
        return None, None

    target_title = clean_title(title)

    # Try DOI lookup
    if doi:
        encoded_doi = quote(f"https://doi.org/{doi}")
        url = f"https://api.openalex.org/works/{encoded_doi}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                openalex_title = clean_title(data.get("title", ""))
                if openalex_title == target_title:
                    return data.get("cited_by_count"), data.get("language")
        except Exception as e:
            print(f"Error querying DOI {doi}: {e}")

    # Fallback: title-based search
    if title:
        quoted_title = quote(f'"{title.strip()}"')
        search_url = f"https://api.openalex.org/works?filter=title.search:{quoted_title}"
        try:
            response = requests.get(search_url, timeout=10)
            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    openalex_title = clean_title(results[0].get("title", ""))
                    if openalex_title == target_title:
                        return results[0].get("cited_by_count"), results[0].get("language")
        except Exception as e:
            print(f"Error querying title: {e}")

    return None, None

def extract_paper_info(paper):
    paper_info = {k: v for k, v in paper.items() if k != "body_text"}
    paper_info.setdefault("metadata", {})
    doi = paper_info["metadata"].get("doi")
    title = paper_info["metadata"].get("title")
    citation_count, language = fetch_citation_count_and_language(doi, title)

    if language is None:
        abstract_text = paper.get("abstract", {}).get("text", "")
        try:
            language = detect(abstract_text.strip()) if abstract_text.strip() else None
        except Exception:
            language = None

    paper_info["metadata"]["language"] = language
    paper_info["metadata"]["cited_by_count"] = citation_count

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

def _process_file(args):
    in_path, out_path = args

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(in_path, "r", encoding="utf-8") as f, \
         open(out_path, "w", encoding="utf-8") as wf:
        for line in f:
            paper = json.loads(line)
            paper_info = extract_paper_info(paper)
            if paper_info.get("paper_id"):
                wf.write(json.dumps(paper_info, ensure_ascii=False) + "\n")

    return in_path, out_path

def process_directory(input_dir, output_dir, num_workers=None):
    if num_workers is None:
        num_workers = os.cpu_count()

    tasks = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if not file.endswith(".jsonl"):
                continue
            rel = os.path.relpath(root, input_dir)
            in_path = os.path.join(root, file)
            out_dir = os.path.join(output_dir, rel)
            out_path = os.path.join(out_dir, file)

            # Skip if file exists and is non-empty
            if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                print(f"Skipping existing file: {out_path}")
                continue

            tasks.append((in_path, out_path))

    with Pool(processes=num_workers) as pool:
        for in_path, out_path in pool.map(_process_file, tasks):
            print(f"Processed {in_path} -> {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_json.py <input_dir> <output_dir> [<num_workers>]")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    num_workers = int(sys.argv[3]) if len(sys.argv) > 3 else os.cpu_count()
    print(f"Using {num_workers} workers")
    process_directory(input_dir, output_dir, num_workers)
