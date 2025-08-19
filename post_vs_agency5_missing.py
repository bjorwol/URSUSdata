import pandas as pd, re, unicodedata

POST_FILE = "post_le_all_clean.csv"
A5_FILE   = "Agency 5.csv"
POST_COL  = "Agency"
A5_MAIN   = "CRP pra Agency name"
A5_ALT    = "Alternate Name"

dfp = pd.read_csv('/Users/bjorwol/Downloads/URSUSdata-main/results/post_le_all_clean.csv', dtype=str)
dfa = pd.read_csv('/Users/bjorwol/Downloads/URSUSdata-main/raw-data/Agency 5.csv', dtype=str)

def norm(s):
    s = "" if s is None or (isinstance(s,float) and pd.isna(s)) else unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).upper()
    s = re.sub(r"\bBART\b", " BAY AREA RAPID TRANSIT ", s)
    s = re.sub(r"\bUC\b", " UNIVERSITY OF CALIFORNIA ", s)
    s = re.sub(r"\bHOUSING AUTH\b", " HOUSING AUTHORITY ", s)
    s = re.sub(r"\bCITY OF\b", " ", s)
    s = re.sub(r"\bCOUNTY OF\b", " COUNTY ", s)
    s = re.sub(r"\bPD\b"," POLICE DEPARTMENT ",s)
    s = re.sub(r"\bSO\b"," SHERIFF S OFFICE ",s)
    s = re.sub(r"\bSD\b"," SHERIFF S DEPARTMENT ",s)
    s = re.sub(r"\bDA\b"," DISTRICT ATTORNEY ",s)
    s = re.sub(r"\bCHP\b"," CALIFORNIA HIGHWAY PATROL ",s)
    s = re.sub(r"[^\w\s]"," ",s)
    return re.sub(r"\s+"," ",s).strip()

post_norm = dfp[POST_COL].map(norm)
a5_norm = pd.Series(dtype=str)
if A5_MAIN in dfa: a5_norm = pd.concat([a5_norm, dfa[A5_MAIN].map(norm)], ignore_index=True)
if A5_ALT  in dfa: a5_norm = pd.concat([a5_norm,  dfa[A5_ALT].map(norm)],  ignore_index=True)

missing = dfp.loc[~post_norm.isin(set(a5_norm)), [POST_COL]].drop_duplicates().sort_values(POST_COL)
missing.to_csv("agencies_missing_postLE_agency5.csv", index=False)
print("Missing agencies:", len(missing))
