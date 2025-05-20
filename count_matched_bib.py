import os
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

def process_jsonl_file(filepath):
    number_of_bib = 0
    number_of_matched_bib = 0
    number_of_ref = 0

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    data = json.loads(line)

                    # Count bib entries
                    bib_entries = data.get('bib_entries', {})
                    for entry in bib_entries.values():
                        number_of_bib += 1
                        if entry.get('contained_arXiv_ids'):
                            if len(entry['contained_arXiv_ids']) > 0:
                                number_of_matched_bib += 1

                    # Count ref entries
                    ref_entries = data.get('ref_entries', {})
                    number_of_ref += len(ref_entries)

                except json.JSONDecodeError:
                    continue  # skip malformed lines
    except Exception as e:
        print(f"Failed to process {filepath}: {e}")

    return number_of_bib, number_of_matched_bib, number_of_ref

def run_through_directory(root_dir):
    jsonl_files = []

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.jsonl'):
                jsonl_files.append(os.path.join(dirpath, filename))

    total_bib = 0
    total_matched_bib = 0
    total_ref = 0

    # Use all available CPUs
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = [executor.submit(process_jsonl_file, path) for path in jsonl_files]

        for future in as_completed(futures):
            bib, matched_bib, ref = future.result()
            total_bib += bib
            total_matched_bib += matched_bib
            total_ref += ref

    print(f"Total bib entries: {total_bib}")
    print(f"Total matched bib entries (with arXiv ids): {total_matched_bib}")
    print(f"Total ref entries: {total_ref}")

# Example usage:
run_through_directory('/data/horse/ws/inbe405h-unarxive/processed_unarxive_extended_data')
