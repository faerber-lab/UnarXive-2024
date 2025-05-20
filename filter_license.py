import json
import os
from collections import defaultdict
from multiprocessing import Pool, cpu_count

def is_permissive(license_url):
    if license_url is None or license_url not in [
        # only use papers licensed such that result can be
        # shared as cc by-sa 4.0 — i.e. no nc and no nd
        # (could opt for using by-nc-sa and get ~15k more
        #  papers, but at ~200k it’s not a huge gain and
        #  requires restricting the use of the ML data)
        'http://creativecommons.org/licenses/by/4.0/',  # 130k
        'http://creativecommons.org/licenses/by/3.0/',  # 6k
        'http://creativecommons.org/licenses/by-sa/4.0/',  # 8k
        'http://creativecommons.org/publicdomain/zero/1.0/',  # 8k
        'http://creativecommons.org/licenses/publicdomain/',  # 2k
        # 'http://creativecommons.org/licenses/by-nc-sa/3.0/',  4k
        # 'http://creativecommons.org/licenses/by-nc-sa/4.0/',  18k
        # 'http://creativecommons.org/licenses/by-nc-nd/4.0/',  18k
    ]:
        return False
    return True

def tag_and_save_parallel(args):
    fp_full, out_dir_subset = args
    license_counts = defaultdict(int)
    updated_papers = []
    permissive_papers = []

    try:
        with open(fp_full, 'r', encoding='utf-8') as infile:
            for line in infile:
                try:
                    ppr = json.loads(line.strip())
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Skipping malformed line in {fp_full}: {e}")
                    continue

                metadata = ppr.get("metadata", {})
                license_url = metadata.get("license")
                license_counts[license_url] += 1
                updated_papers.append(ppr)
                if is_permissive(license_url):
                    permissive_papers.append(ppr)

        # Overwrite original file
        with open(fp_full, 'w', encoding='utf-8') as f:
            for ppr in updated_papers:
                f.write(json.dumps(ppr) + '\n')

        # Write permissive papers
        os.makedirs(out_dir_subset, exist_ok=True)
        subset_path = os.path.join(out_dir_subset, os.path.basename(fp_full))
        with open(subset_path, 'w', encoding='utf-8') as f:
            for ppr in permissive_papers:
                f.write(json.dumps(ppr) + '\n')

        print(f'[ {os.path.basename(fp_full)} ] Total: {len(updated_papers)}, Permissive: {len(permissive_papers)}')
        return dict(license_counts)
    
    except Exception as e:
        print(f"[ERROR] Failed to process {fp_full}: {e}")
        return {}


# ------------- Dispatching Parallel Jobs -------------
def process_all_parallel(input_dir):
    subset_dir = os.path.join(input_dir, 'permissive_subset')
    os.makedirs(subset_dir, exist_ok=True)

    all_jsonl_files = []

    for root, _, files in os.walk(input_dir):
        if subset_dir in root:
            continue
        for fname in files:
            if fname.endswith('.jsonl'):
                full_path = os.path.join(root, fname)
                all_jsonl_files.append((full_path, subset_dir))

    print(f"Launching {len(all_jsonl_files)} files across {min(cpu_count(), len(all_jsonl_files))} jobs...")
    license_total = defaultdict(int)

    with Pool(processes=min(cpu_count(), len(all_jsonl_files))) as pool:
        results = pool.map(tag_and_save_parallel, all_jsonl_files)

    for lic_dict in results:
        for lic, count in lic_dict.items():
            license_total[lic] += count

    print('\nLicense Summary:')
    for lic, count in license_total.items():
        print(f'{lic}: {count}')
    total_perm = sum(c for l, c in license_total.items() if is_permissive(l))
    print(f'Total permissive: {total_perm}')

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python tag_and_save_parallel.py /path/to/dataset")
        sys.exit(1)
    process_all_parallel(sys.argv[1])