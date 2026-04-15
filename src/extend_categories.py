import os
import json
from arxive_taxonomy/arxiv_taxonomy import GROUPS, ARCHIVES, CATEGORIES, ARCHIVES_SUBSUMED, CATEGORY_ALIASES
import sys
from pathlib import Path

# Make the taxonomy modules importable when running as:
#   python src/extend_categories.py <DATASET_DIR>
_TAXONOMY_DIR = Path(__file__).resolve().parent / "arxive_taxonomy"
sys.path.insert(0, str(_TAXONOMY_DIR))

def get_discipline(categories: str | None):
    if categories:
        categories = categories.split()
        first_category = categories[0]
        cat_info = CATEGORIES.get(first_category)
        if cat_info:
            archive_key = cat_info.in_archive
            if archive_key:
                archive_info = ARCHIVES.get(archive_key)
                if archive_info:
                    group_key = archive_info.in_group
                    if group_key:
                        group_info = GROUPS.get(group_key)
                        if group_info:
                            return group_info.full_name

    return None


def process_jsonl_file(filepath: str):
    temp_path = filepath + ".tmp"
    with open(filepath, "r", encoding="utf-8") as infile, open(temp_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            data = json.loads(line)
            metadata = data.get("metadata", {})
            categories = metadata.get("categories", "")
            metadata["discipline"] = get_discipline(categories)
            data["metadata"] = metadata
            outfile.write(json.dumps(data) + "\n")
    os.replace(temp_path, filepath)


def process_directory(root_dir: str):
    for root, _, files in os.walk(root_dir):
        for fname in files:
            if fname.endswith(".jsonl"):
                process_jsonl_file(os.path.join(root, fname))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/extend_categories.py <DATASET_DIR>")
        sys.exit(1)

    process_directory(sys.argv[1])

