from pathlib import Path
import pandas as pd
import numpy as np
import re

BASE = Path(__file__).resolve().parent
RAW  = BASE / "raw-data"
OUT  = BASE / "results"
OUT.mkdir(exist_ok=True)

OUT_UNRESOLVED = OUT / "unresolved_missing_agencies.csv"

def norm_name_series(s: pd.Series) -> pd.Series:
    s = s.fillna("").astype(str).str.lower()
    s = s.apply(lambda x: re.sub(r"[^a-z0-9&/ ]+", " ", x))
    s = s.str.replace(r"\s+", " ", regex=True).str.strip()
    return s

dic_df = pd.read_excel('raw-data/DIC_PRA_Rusch_07172025.xlsx', sheet_name='Statewide', engine='openpyxl')
agency_df = pd.read_csv('raw-data/Agency 5.csv')
facilities_df = pd.read_csv('raw-data/facilities_clean.csv')

dic_df["agency_number"] = dic_df["agency_number"].astype(str)
agency_df["NCIC"] = agency_df["NCIC"].astype(str)

for c in ["Primary Name", "Alternate URSUS Name", "URSUS Agency Name"]:
    if c not in agency_df.columns:
        agency_df[c] = ""

for c in ["facility", "agency", "death_agency_full_name"]:
    if c not in facilities_df.columns:
        facilities_df[c] = ""

id_merge = agency_df.merge(
    dic_df[["agency_number"]], left_on="NCIC", right_on="agency_number", how="left"
)
missing_from_dic = id_merge[id_merge["agency_number"].isna()].copy()

missing_from_dic["primary_clean"] = norm_name_series(missing_from_dic["Primary Name"])
missing_from_dic["alt_clean"]     = norm_name_series(missing_from_dic["Alternate URSUS Name"])
missing_from_dic["ursus_clean"]   = norm_name_series(missing_from_dic["URSUS Agency Name"])

missing_from_dic["_orig_idx"] = missing_from_dic.index
missing_from_dic["name_candidates"] = (
    missing_from_dic[["primary_clean", "alt_clean", "ursus_clean"]]
    .apply(lambda r: [v for v in r.tolist() if v], axis=1)
)

exploded = missing_from_dic.explode("name_candidates").rename(
    columns={"name_candidates": "candidate_clean"}
)

fac = facilities_df.copy()
fac["facility_clean"] = norm_name_series(fac["facility"])
fac["agency_clean"]   = norm_name_series(fac["agency"])
fac["death_clean"]    = norm_name_series(fac["death_agency_full_name"])

fac_long = fac.melt(
    id_vars=[c for c in fac.columns if c not in ["facility_clean","agency_clean","death_clean"]],
    value_vars=["facility_clean","agency_clean","death_clean"],
    var_name="crosswalk_source",
    value_name="crosswalk_clean"
)
fac_long = fac_long[(fac_long["crosswalk_clean"] != "")].drop_duplicates()

joined = exploded.merge(
    fac_long[["crosswalk_clean","facility","agency","death_agency_full_name"]],
    left_on="candidate_clean",
    right_on="crosswalk_clean",
    how="left"
)

def any_notna(s: pd.Series) -> bool:
    return bool(s.notna().any())

agg = joined.groupby("_orig_idx").agg({
    "crosswalk_clean": any_notna,
    "facility": lambda s: ", ".join(sorted(set([x for x in s.dropna().astype(str) if x]))[:5]) if any_notna(s) else "",
    "agency":   lambda s: ", ".join(sorted(set([x for x in s.dropna().astype(str) if x]))[:5]) if any_notna(s) else "",
    "death_agency_full_name": lambda s: ", ".join(sorted(set([x for x in s.dropna().astype(str) if x]))[:5]) if any_notna(s) else "",
})

enriched = missing_from_dic.set_index("_orig_idx").join(agg, how="left").rename(columns={
    "crosswalk_clean": "matched_by_facilities_crosswalk",
    "facility": "matched_facilities_sample",
    "agency": "matched_agencies_sample",
    "death_agency_full_name": "matched_death_agency_names_sample",
})
enriched["matched_by_facilities_crosswalk"] = enriched["matched_by_facilities_crosswalk"].fillna(False).astype(bool)

unresolved = enriched[~enriched["matched_by_facilities_crosswalk"]].copy()

cols = ["NCIC","ORI","Primary Name","Alternate URSUS Name","URSUS Agency Name","Agency County","County","CntyCode"]
cols = [c for c in cols if c in unresolved.columns]
unresolved[cols].drop_duplicates().sort_values(by=[c for c in ["County","Agency County","Primary Name"] if c in cols]) \
    .to_csv(OUT_UNRESOLVED, index=False)

print(f"✓ Final written to: {OUT_UNRESOLVED}")
