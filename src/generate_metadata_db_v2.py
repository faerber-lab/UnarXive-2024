""" From an arXiv metadata snapshot as provided by
        https://www.kaggle.com/Cornell-University/arxiv
    generate an SQLite database with indices for performant access.
"""

import json
import os
import re
import sqlite3
import sys
from tqdm import tqdm


def gen_meta_db(in_fp, output_dir):
    # input prep
    in_path, in_fn = os.path.split(in_fp)
    in_fn_base, ext = os.path.splitext(in_fn)

    # output prep
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Before processing, check if the SQLite file already exists and skip if it does.
    out_fp = os.path.join(output_dir, '{}.sqlite'.format(in_fn_base))
    if os.path.exists(out_fp):
        print(f"Skipping {out_fp}, database already exists.")
        return

    conn = sqlite3.connect(out_fp)
    db_cur = conn.cursor()
    db_cur.execute("""
        create table paper(
            'year' integer,
            'month' integer,
            'aid' text,
            'title' text,
            'json' text
        )
    """)

    aid_patt = re.compile(r'^(.*\/)?(\d\d)(\d\d).*$')

    num_lines = sum(1 for i in open(in_fp, 'rb'))
    print('filling table')
    with open(in_fp) as f:
        for line in tqdm(f, total=num_lines):
            try:
                ppr_meta = json.loads(line.strip())['metadata']  # Access only 'metadata' part
                aid_m = aid_patt.match(ppr_meta['id'])
                assert aid_m is not None
                aid = aid_m.group(0)
                y = int(aid_m.group(2))
                m = int(aid_m.group(3))
                title = ppr_meta['title']
                db_cur.execute(
                    (
                        "insert into paper "
                        "('year','month','aid','title','json')"
                        "values(?,?,?,?,?)"
                    ),
                    (y, m, aid, title, line.strip())
                )
            except (json.JSONDecodeError, KeyError, AssertionError) as e:
                print(f"Skipping malformed entry in {in_fp}: {e}")
                continue

    print('generating index')
    db_cur.execute(
          "create index ym  on paper('year', 'month')"
      )
    conn.commit()

def process_json_folder(input_folder, output_dir):
    # Iterate through all JSON files in the input folder
    for json_fn in os.listdir(input_folder):
        if json_fn.endswith('.jsonl'):
            json_fp = os.path.join(input_folder, json_fn)
            print(f"Processing {json_fn}")
            gen_meta_db(json_fp, output_dir)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: generate_metadata_db.py <arXiv_metadata_snapshot.json> <output_sqlite_directory>')
        sys.exit()
    process_json_folder(sys.argv[1],sys.argv[2])
