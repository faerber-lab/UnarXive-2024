import os
import glob
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

# --- CONFIGURATION ---
DATA_DIR = "/data/horse/ws/inbe405h-unarxive/processed_unarxive_extended_data"
OUT_DIR = "rag_pipeline/stats"
os.makedirs(OUT_DIR, exist_ok=True)

# --- PARSE FUNCTION ---
def parse_jsonl_file(filepath):
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    metadata = obj.get("metadata", {})
                    date_str = metadata.get("update_date")
                    disc = metadata.get("discipline")
                    results.append({
                        "date": date_str,
                        "discipline": disc,
                    })
                except Exception:
                    continue
    except Exception:
        pass
    return results

# --- LOAD FILES IN PARALLEL ---
file_list = glob.glob(os.path.join(DATA_DIR, "**", "*.jsonl"), recursive=True)
all_records = []
print(f"Found {len(file_list)} JSONL files.")

with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
    futures = [executor.submit(parse_jsonl_file, file) for file in file_list]
    for future in as_completed(futures):
        all_records.extend(future.result())

# --- CREATE DATAFRAME ---
df = pd.DataFrame(all_records)
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])
df = df[(df["date"] >= "2004-01-01") & (df["date"] <= "2024-12-31")]
df["year"] = df["date"].dt.year

# --- CUMULATIVE PUBLICATIONS ---
grouped = df.groupby(["year", "discipline"]).size().reset_index(name="count")
pivot = grouped.pivot(index="year", columns="discipline", values="count").fillna(0)
pivot = pivot.reindex(range(2004, 2025), fill_value=0)
cumulative = pivot.cumsum()

plt.figure(figsize=(6, 3))
for discipline in cumulative.columns:
    plt.plot(cumulative.index, cumulative[discipline], label=discipline.title())
plt.xlabel("Year")
plt.ylabel("number of papers")
plt.title("Publications per Discipline (2004–2024)")
plt.xticks(ticks=[2004, 2007, 2010, 2013, 2016, 2019, 2022, 2025])
plt.legend(loc="upper left", fontsize="x-small", ncol=1)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/pub_counts_by_year.png", dpi=300)
plt.close()

# Rename long discipline to 'electrical engineering'
df["discipline"] = df["discipline"].replace("Electrical Engineering and Systems Science", "Electrical Eng.").replace("Quantitative Biology", "Quant Bio").replace("Quantitative Finance", "Quant Finance")

# Count total publications by discipline

total_counts = df['discipline'].value_counts()
total_counts.plot(kind='bar', figsize=(6, 4), title="Total Publications by Discipline")
plt.xlabel("Number of papers")
plt.tight_layout()
plt.savefig("rag_pipeline/stats/total_by_discipline.png", dpi=300)
plt.close()



# --- TOTAL PUBLICATIONS PER YEAR ---
yearly_total = df.groupby("year")["discipline"].count()
yearly_total.plot(kind="bar", figsize=(6, 3), title="Total Publications Per Year")
plt.ylabel("Number of papers")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/total_per_year.png", dpi=300)
plt.close()

# --- DISCIPLINE SHARE OVER TIME ---
relative = pivot.div(pivot.sum(axis=1), axis=0) * 100
relative.plot.area(figsize=(6, 3), legend=False)
plt.title("Discipline Share Over Time (%)")
plt.xlabel("Year")
plt.ylabel("Share %")
plt.xticks([2004, 2007, 2010, 2013, 2016, 2019, 2022, 2025])
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/discipline_share_area.png", dpi=300)
plt.close()




# --- PER-DISCIPLINE STATS ---
total_papers = len(df)
discipline_counts = df["discipline"].value_counts()
top_disciplines = discipline_counts.head(5).index.tolist()

for discipline in top_disciplines:
    count = discipline_counts.get(discipline, 0)
    percent = count / total_papers * 100
    print(f"{discipline.title():<20}: {count:>6} papers ({percent:.2f}%)")

others_count = total_papers - sum(discipline_counts.get(d, 0) for d in top_disciplines)
others_percent = others_count / total_papers * 100
print(f"{'Others':<20}: {others_count:>6} papers ({others_percent:.2f}%)")
