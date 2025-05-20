import os
import json
from multiprocessing import Pool
import sys
from enrich_metadata import enrich_metadata
from group_sections import process_sections

def _process_file(args):
    in_path, out_path = args

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(in_path, "r", encoding="utf-8") as f, \
         open(out_path, "w", encoding="utf-8") as wf:
        for line in f:
            paper = json.loads(line)
            paper_info = {k: v for k, v in paper.items() if k != "body_text"}
            paper_info.setdefault("metadata", {})
            paper_info = enrich_metadata(paper,paper_info)
            paper_info = process_sections(paper,paper_info)
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
