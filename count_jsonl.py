import os
import json

def count_jsonl_elements_in_directory(directory):
    total_count = 0

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".jsonl"):
                filepath = os.path.join(root, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    count = sum(1 for _ in f)
                    print(f"{filename}: {count} entries")
                    total_count += count

    print(f"\nTotal entries across all .jsonl files: {total_count}")
    return total_count

# Example usage
directory_path = "/data/horse/ws/inbe405h-unarxive/unarxive_extended_data/unarXive_230324"
count_jsonl_elements_in_directory(directory_path)

