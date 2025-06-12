import os
import json
from arxive_taxonomy/arxiv_taxonomy import GROUPS, ARCHIVES, CATEGORIES, ARCHIVES_SUBSUMED, CATEGORY_ALIASES

def get_discipline(categories):
    if categories:
        categories = categories.split()
        first_category = categories[0]
        cat_info = CATEGORIES.get(first_category)
        if cat_info:
            # Match the category's in_archive with an archive
            archive_key = cat_info.in_archive
            if archive_key:
                # Match the archive with in_group from ARCHIVES
                archive_info = ARCHIVES[archive_key]
                if archive_info:
                    group_key = archive_info.in_group
                    if group_key:
                        # Match the group with GROUPS to get the full name
                        group_info = GROUPS[group_key]
                        if group_info:
                            return group_info.full_name
    
    return None

def process_jsonl_file(filepath):
    temp_path = filepath + ".tmp"
    with open(filepath, 'r', encoding='utf-8') as infile, open(temp_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            data = json.loads(line)
            metadata = data.get("metadata", {})
            categories = metadata.get("categories", "")
            discipline = get_discipline(categories)
            metadata["discipline"] = discipline
            data["metadata"] = metadata
            outfile.write(json.dumps(data) + "\n")
    os.replace(temp_path, filepath)  

def process_directory(root_dir):
    for root, _, files in os.walk(root_dir):
        for fname in files:
            if fname.endswith(".jsonl"):
                full_path = os.path.join(root, fname)
                process_jsonl_file(full_path)

if __name__ == "__main__":
    directory_path = "rag_pipeline/testo"
    process_directory(directory_path)
