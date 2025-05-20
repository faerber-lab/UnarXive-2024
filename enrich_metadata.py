import json
import re
from urllib.parse import quote
import requests
from langdetect import detect


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

def enrich_metadata(paper,paper_info):
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
    return paper_info