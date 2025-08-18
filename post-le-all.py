from pathlib import Path
import re
import pandas as pd

IN_DIR  = Path("/Users/bjorwol/Downloads/URSUSdata-main/cleaned-post-le-data")
OUT_DIR = Path("/Users/bjorwol/Downloads/URSUSdata-main/results")
OUT_DIR.mkdir(parents=True, exist_ok=True)  

files = sorted(list(IN_DIR.glob("*_clean.csv")) + list(IN_DIR.glob("*_ss.csv")))

rows = []
for f in files:
    name = f.name
    m = re.search(r"(\d{2})[-_](\d{4})", name) or re.search(r"(\d{1,2})-(\d{1,2})-(\d{4})", name)
    if not m:
        print("Skipping (no date in name):", name)
        continue

    if len(m.groups()) == 2:
        mm, yyyy = int(m.group(1)), int(m.group(2))
    else:
        mm, _, yyyy = int(m.group(1)), int(m.group(2)), int(m.group(3))

    df = pd.read_csv(f)
    df["Year"] = yyyy
    df["Snapshot"] = "Jan" if mm == 1 else ("Jul" if mm == 7 else f"{mm:02d}")
    df["SourceFile"] = name
    rows.append(df)

out = pd.concat(rows, ignore_index=True)

out_path = OUT_DIR / "post_le_all.csv"
out.to_csv(out_path, index=False)
print("Wrote:", out_path)

