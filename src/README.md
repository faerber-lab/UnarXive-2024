## Reproducing UnarXive (2024)

### 1) Build the arXiv metadata SQLite DB

Script: `generate_metadata_db.py`
```bash
python src/generate_metadata_db.py <ARXIV_METADATA_JSONL_DIR> <META_DB_OUT_DIR>
```

### 2) Parse arXiv sources (normalize + Tralics parse)

Script: `prepare.py`
```bash
python src/prepare.py <ARXIV_SOURCES_TAR_DIR> <PARSED_OUT_DIR> <META_DB_SQLITE_FILE> [<TAR_FN_PATTERN>]
```

### 3) Match bibliography references against OpenAlex (local DB) + Crossref + GROBID

Script: `match_references_openalex.py`
```bash
python src/match_references_openalex.py <IN_DIR> <OUT_DIR> <MATCH_DB_HOST> <META_DB_SQLITE_FILE> <GROBID_HOST> <NUM_WORKERS>
```
Requirements:
- PostgreSQL reachable at `<MATCH_DB_HOST>`, with:
	- database name: `openalex`
	- user: `postgres`
	- tables: `openalex` and `crossref`
- GROBID reachable at: `http://<GROBID_HOST>:8070/api/processCitation`
---

### 4) Group sections + enrich metadata (language + cited_by_count)

Script: `gourp_sections_and_enrich_metadata.py`
```bash
python src/gourp_sections_and_enrich_metadata.py <INPUT_DIR> <OUTPUT_DIR> [<NUM_WORKERS>]
```

### 5) Filter by permissive license (creates a subset)

Script: `filter_license.py`
```bash
python src/filter_license.py <DATASET_DIR>
```

### 6) Add discipline from arXiv categories

Script: `extend_categories.py`
```bash
python src/extend_categories.py <DATASET_DIR>
```

